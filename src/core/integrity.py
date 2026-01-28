"""File integrity verification system
SECURITY: Detects tampering and unauthorized modifications
"""
import hashlib
import os
import json
from typing import Dict, List, Tuple
from pathlib import Path

class IntegrityChecker:
    """Verify file integrity to detect tampering"""
    
    CRITICAL_FILES = [
        'src/main.py',
        'src/core/config.py',
        'src/core/logger.py',
        'src/core/safe_wmi.py',
        'src/monitors/__init__.py',
        'src/monitors/gpu_monitor.py',
        'launcher.bat',
    ]
    
    def __init__(self, manifest_path: str = "data/integrity.json"):
        self.manifest_path = manifest_path
        self.manifest: Dict[str, str] = {}
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """Create data directory if needed"""
        os.makedirs(os.path.dirname(self.manifest_path), exist_ok=True)
    
    def _compute_hash(self, file_path: str) -> str:
        """Compute SHA-256 hash of file
        
        Args:
            file_path: Path to file
        
        Returns:
            SHA-256 hash as hex string
        """
        sha256 = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                # Read in chunks to handle large files
                while chunk := f.read(8192):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            print(f"[ERROR] Failed to hash {file_path}: {e}")
            return ""
    
    def generate_manifest(self, files: List[str] = None) -> Dict[str, str]:
        """Generate integrity manifest for files
        
        Args:
            files: List of files to check (default: CRITICAL_FILES)
        
        Returns:
            Dictionary mapping file paths to their hashes
        """
        if files is None:
            files = self.CRITICAL_FILES
        
        manifest = {}
        
        for file_path in files:
            if os.path.exists(file_path):
                file_hash = self._compute_hash(file_path)
                if file_hash:
                    manifest[file_path] = file_hash
                    print(f"[INFO] {file_path}: {file_hash[:16]}...")
            else:
                print(f"[WARN] File not found: {file_path}")
        
        return manifest
    
    def save_manifest(self, manifest: Dict[str, str] = None):
        """Save manifest to disk
        
        Args:
            manifest: Manifest to save (default: generate new)
        """
        if manifest is None:
            manifest = self.generate_manifest()
        
        try:
            with open(self.manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            print(f"[INFO] Manifest saved to {self.manifest_path}")
        except Exception as e:
            print(f"[ERROR] Failed to save manifest: {e}")
    
    def load_manifest(self) -> Dict[str, str]:
        """Load manifest from disk
        
        Returns:
            Manifest dictionary or empty dict
        """
        if not os.path.exists(self.manifest_path):
            return {}
        
        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load manifest: {e}")
            return {}
    
    def verify_integrity(self, raise_on_failure: bool = False) -> Tuple[bool, List[str]]:
        """Verify file integrity against saved manifest
        
        Args:
            raise_on_failure: Raise exception if tampering detected
        
        Returns:
            Tuple of (all_valid, list_of_modified_files)
        """
        manifest = self.load_manifest()
        
        if not manifest:
            print("[WARN] No integrity manifest found")
            print("[INFO] Run with --generate-manifest to create one")
            return True, []  # Fail open on first run
        
        modified_files = []
        
        for file_path, expected_hash in manifest.items():
            if not os.path.exists(file_path):
                print(f"[ERROR] File missing: {file_path}")
                modified_files.append(file_path)
                continue
            
            current_hash = self._compute_hash(file_path)
            
            if current_hash != expected_hash:
                print(f"[SECURITY] File modified: {file_path}")
                print(f"  Expected: {expected_hash[:16]}...")
                print(f"  Current:  {current_hash[:16]}...")
                modified_files.append(file_path)
        
        if modified_files:
            print(f"\n[SECURITY] {len(modified_files)} file(s) have been modified!")
            print("[SECURITY] This may indicate tampering or unauthorized changes.")
            
            if raise_on_failure:
                raise SecurityError(f"File integrity check failed: {modified_files}")
            
            return False, modified_files
        
        print("[OK] All files passed integrity check")
        return True, []
    
    def verify_critical_files_exist(self) -> Tuple[bool, List[str]]:
        """Verify all critical files exist
        
        Returns:
            Tuple of (all_exist, list_of_missing_files)
        """
        missing = []
        
        for file_path in self.CRITICAL_FILES:
            if not os.path.exists(file_path):
                print(f"[ERROR] Critical file missing: {file_path}")
                missing.append(file_path)
        
        if missing:
            print(f"\n[SECURITY] {len(missing)} critical file(s) missing!")
            return False, missing
        
        return True, []

class SecurityError(Exception):
    """Raised when security check fails"""
    pass

# Global integrity checker
_integrity_checker = None

def get_integrity_checker() -> IntegrityChecker:
    """Get global integrity checker instance"""
    global _integrity_checker
    if _integrity_checker is None:
        _integrity_checker = IntegrityChecker()
    return _integrity_checker

def verify_on_startup(strict: bool = False) -> bool:
    """Verify integrity on application startup
    
    Args:
        strict: Raise exception on failure
    
    Returns:
        True if all checks pass
    """
    checker = get_integrity_checker()
    
    # Check critical files exist
    all_exist, missing = checker.verify_critical_files_exist()
    if not all_exist:
        if strict:
            raise SecurityError(f"Critical files missing: {missing}")
        return False
    
    # Verify integrity
    valid, modified = checker.verify_integrity(raise_on_failure=strict)
    return valid

if __name__ == "__main__":
    import sys
    
    checker = IntegrityChecker()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--generate":
        print("[INFO] Generating integrity manifest...")
        checker.save_manifest()
    else:
        print("[INFO] Verifying file integrity...")
        valid, modified = checker.verify_integrity()
        
        if not valid:
            sys.exit(1)
