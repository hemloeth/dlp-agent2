import click
import sys
import json
import os
import warnings
import logging

# Suppress annoying library warnings
warnings.filterwarnings("ignore", category=UserWarning, module="torch.utils.data.dataloader")
warnings.filterwarnings("ignore", category=UserWarning, module="PIL.Image")
warnings.filterwarnings("ignore", message="urllib3.*doesn't match a supported version")
logging.getLogger("easyocr.easyocr").setLevel(logging.ERROR)

from dlp_agent.config import load_policy

@click.command()
@click.option('--scan-dir', help='Directory to scan', required=False)
@click.option('--policy', help='Path to policy file', default='config/policy.json')
@click.option('--debug', is_flag=True, help='Enable debug logging')
@click.option('--json-out', help='Path to output JSON logs', required=False)
@click.option('--web', is_flag=True, help='Send logs to the dashboard page in real time')
@click.option('--web-url', default='http://localhost:3000/api/dashboard/logs', show_default=True,
              help='Dashboard endpoint URL to POST logs to (used with --web)')
def main(scan_dir, policy, debug, json_out, web, web_url):
    """DLP Agent - Detect Sensitive Data."""
    try:
        policy_config = load_policy(policy)
        
        if not scan_dir:
            scan_dir = "C:\\" if os.name == 'nt' else "/"
            # If no scan directory was provided, assume auto-execution and enable web sink
            web = True
            click.echo(f"No scan directory provided. Defaulting to system root: {scan_dir}. Web logging enabled.")

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
            web_sink = WebSink(url=web_url)
            sinks.append(web_sink)
            # Send device metadata once at scan start
            from dlp_agent.utils.device_info import get_device_info
            device_info = get_device_info()
            click.echo(f"[WebSink] Device: {device_info['device_name']} | IP: {device_info['ip_address']} | MAC: {device_info['mac_address']}")
            device_url = web_url.replace("/api/dashboard/logs", "/api/dashboard/device")
            web_sink.send_device_info(device_info, device_url=device_url)
        
        walker = FileWalker(policy_config, debug=debug)
        processor = StreamProcessor(policy_config, sinks=sinks)
        
        scanned_files = 0
        total_findings = 0
        
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
            future_to_file = {executor.submit(processor.process_file, f): f for f in walker.walk(os.path.abspath(scan_dir))}
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    if debug:
                        click.echo(f"Scanning file: {file_path}")
                    findings_count = future.result()
                    total_findings += findings_count
                    scanned_files += 1
                except Exception as exc:
                    click.echo(f"Error processing {file_path}: {exc}", err=True)

                    
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
