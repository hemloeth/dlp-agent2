import click
import sys
import json
import os
from dlp_agent.config import load_policy

@click.command()
@click.option('--scan-dir', help='Directory to scan', required=False)
@click.option('--policy', help='Path to policy file', default='config/policy.json')
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--json-out', help='Path to output JSON logs', required=False)
@click.option('--web', is_flag=True, help='Run with a local web UI')
@click.option('--host', default='127.0.0.1', show_default=True, help='Web UI bind host (with --web)')
@click.option('--port', default=8765, show_default=True, type=int, help='Web UI port (with --web)')
@click.option('--no-open-browser', is_flag=True, help='Do not auto-open browser (with --web)')
def main(scan_dir, policy, debug, json_out, web, host, port, no_open_browser):
    """DLP Agent - Detect Sensitive Data."""
    try:
        if web:
            from dlp_agent.web_server import WebScanServer

            server = WebScanServer(
                host=host,
                port=port,
                default_policy_path=policy,
                debug=debug,
                json_out=json_out,
                open_browser=(not no_open_browser),
            )
            click.echo(f"Web UI running on http://{host}:{port}/", err=True)
            if scan_dir:
                server.start_scan(scan_dir, policy_path=policy)
            server.serve_forever()
            return

        policy_config = load_policy(policy)

        if not scan_dir:
            click.echo("No scan directory provided. Use --scan-dir <path>", err=True)
            return

        click.echo(f"Scanning directory: {scan_dir}")
        if debug:
            click.echo("Debug mode enabled")

        from dlp_agent.scanner import FileWalker, StreamProcessor
        from dlp_agent.events.sinks import CliSink, JsonSink
        
        # Initialize sinks
        sinks = [CliSink()]
        if json_out:
            sinks.append(JsonSink(json_out))
        
        walker = FileWalker(policy_config, debug=debug)
        processor = StreamProcessor(policy_config, sinks=sinks)
        
        scanned_files = 0
        total_findings = 0
        
        for file_path in walker.walk(os.path.abspath(scan_dir)):
            if debug:
                click.echo(f"Scanning file: {file_path}")
            scanned_files += 1
            
            # Processor now handles emission to sinks
            findings_count = processor.process_file(file_path)
            total_findings += findings_count
                    
        click.echo(f"\nScan Complete. Scanned {scanned_files} files. Found {total_findings} issues.", err=True)
        
        # Flush/Close sinks
        for sink in sinks:
            sink.flush()
            if hasattr(sink, 'close'):
                sink.close()
            
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
