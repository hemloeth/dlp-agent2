import sys
import os

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
