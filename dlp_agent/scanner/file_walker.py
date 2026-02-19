import os

class FileWalker:
    def __init__(self, config: dict, debug: bool = False):
        self.config = config
        self.debug = debug
        self.allowed_extensions = set(config.get('scan', {}).get('allowedExtensions', []))
        self.excluded_paths = set(config.get('scan', {}).get('excludedPaths', []))
        self.max_file_size = config.get('scan', {}).get('maxFileSizeMB', 10) * 1024 * 1024

    def walk(self, root_dir: str):
        """
        Generator that yields valid file paths to scan.
        """
        for root, dirs, files in os.walk(root_dir):
            # Modify dirs in-place to skip excluded directories
            # We must use a copy of dirs to iterate safely while modifying
            dirs[:] = [d for d in dirs if not self._is_excluded(os.path.join(root, d))]
            
            for file in files:
                file_path = os.path.join(root, file)
                if self._should_scan_file(file_path):
                    yield file_path

    def _is_excluded(self, path: str) -> bool:
        # Normalize path for comparison
        path = path.replace('\\', '/')
        for excluded in self.excluded_paths:
            if excluded in path:
                return True
        return False

    def _should_scan_file(self, file_path: str) -> bool:
        # Check extension
        _, ext = os.path.splitext(file_path)
        if ext.lower() not in self.allowed_extensions:
            return False

        # Check file size
        try:
            if os.path.getsize(file_path) > self.max_file_size:
                return False
        except OSError:
            return False

        return True
