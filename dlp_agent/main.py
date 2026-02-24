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
@click.option('--web', is_flag=True, help='Send logs to the dashboard page in real time')
@click.option('--web-url', default='https://dlp-gtis.vercel.app/dashboard/logs', show_default=True,
              help='Dashboard endpoint URL to POST logs to (used with --web)')
def main(scan_dir, policy, debug, json_out, web, web_url):
    """DLP Agent - Detect Sensitive Data."""
    try:
        policy_config = load_policy(policy)
        
        if not scan_dir:
            click.echo("No scan directory provided. Use --scan-dir <path>")
            return

        click.echo(f"Scanning directory: {scan_dir}")
        if debug:
            click.echo("Debug mode enabled")

        from dlp_agent.scanner import FileWalker, StreamProcessor
        from dlp_agent.events.sinks import CliSink, JsonSink, WebSink
        
        # Initialize sinks
        sinks = [CliSink()]
        if json_out:
            sinks.append(JsonSink(json_out))
        if web:
            click.echo(f"[WebSink] Sending logs to dashboard -> {web_url}")
            sinks.append(WebSink(url=web_url))
        
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
