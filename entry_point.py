import sys
import os
import traceback
import datetime

def global_exception_handler(exctype, value, tb):
    with open("dlp_agent_crash.log", "a") as f:
        f.write(f"--- Crash on {datetime.datetime.now()} ---\n")
        traceback.print_exception(exctype, value, tb, file=f)
    
sys.excepthook = global_exception_handler

# Ensure the root directory is in sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from dlp_agent.main import main
except ImportError as e:
    print(f"Error: Could not import dlp_agent. Make sure the directory structure is correct. {e}")
    sys.exit(1)

if __name__ == "__main__":
    main()
