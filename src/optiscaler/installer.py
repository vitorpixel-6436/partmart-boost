#!/usr/bin/env python3
"""OptiScaler Installer

Version: 0.3.5d (package 3.8a, stage 3/6)
"""
import zipfile
import shutil
from pathlib import Path
from typing import Optional, Callable

from .types import InstallStatus, InstallationError
from .downloader import GitHubAPI, Downloader


class OptiScalerInstaller:
    """OptiScaler auto-installer
    
    Downloads and installs OptiScaler from GitHub releases.
    
    Usage:
        installer = OptiScalerInstaller(Path("./optiscaler"))
        
        # Get latest version
        version = installer.get_latest_version()
        
        # Install with progress
        def progress(status, percent):
            print(f"{status}: {percent}%")
        
        installer.install(progress_callback=progress)
    """
    
    def __init__(self, install_dir: Path):
        """Initialize installer
        
        Args:
            install_dir: Target installation directory
        """
        self.install_dir = install_dir
        self.github_api = GitHubAPI()
        self.downloader = Downloader()
        
        # Temporary directory for downloads
        self.temp_dir = install_dir.parent / "optiscaler_temp"
        
        print("[OptiScalerInstaller] Initialized (Stage 3)")
    
    def get_latest_version(self) -> Optional[str]:
        """Get latest OptiScaler version from GitHub
        
        Returns:
            Version string or None
        """
        release = self.github_api.get_latest_release()
        if release:
            version = release.get('tag_name', '')
            # Remove 'v' prefix if present
            if version.startswith('v'):
                version = version[1:]
            return version
        return None
    
    def download(
        self,
        version: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> bool:
        """Download OptiScaler release
        
        Args:
            version: Version to download (None = latest)
            progress_callback: Progress callback (downloaded, total)
        
        Returns:
            True if successful
        """
        print("[OptiScalerInstaller] Starting download...")
        
        # Get release info
        release = self.github_api.get_latest_release()
        if not release:
            print("[OptiScalerInstaller] Failed to get release info")
            return False
        
        # Get download URL
        download_url = self.github_api.get_download_url(release)
        if not download_url:
            print("[OptiScalerInstaller] No download URL found")
            return False
        
        # Create temp directory
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Download file
        archive_path = self.temp_dir / "optiscaler.zip"
        success = self.downloader.download(
            download_url,
            archive_path,
            progress_callback
        )
        
        if not success:
            print("[OptiScalerInstaller] Download failed")
            return False
        
        print(f"[OptiScalerInstaller] Downloaded to: {archive_path}")
        return True
    
    def extract(self) -> bool:
        """Extract OptiScaler archive
        
        Returns:
            True if successful
        """
        archive_path = self.temp_dir / "optiscaler.zip"
        
        if not archive_path.exists():
            print("[OptiScalerInstaller] Archive not found")
            return False
        
        print("[OptiScalerInstaller] Extracting archive...")
        
        try:
            # Create install directory
            self.install_dir.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                # Get list of files
                file_list = zip_ref.namelist()
                print(f"[OptiScalerInstaller] Files in archive: {len(file_list)}")
                
                # Extract all files
                zip_ref.extractall(self.temp_dir / "extracted")
            
            # Find OptiScaler files in extracted directory
            extracted_dir = self.temp_dir / "extracted"
            
            # Look for OptiScaler files (may be in subdirectory)
            optiscaler_files = list(extracted_dir.rglob("nvngx.dll"))
            
            if optiscaler_files:
                # Found OptiScaler files, copy to install dir
                source_dir = optiscaler_files[0].parent
                print(f"[OptiScalerInstaller] Found OptiScaler in: {source_dir}")
                
                # Copy all files from source to install dir
                for item in source_dir.iterdir():
                    dst = self.install_dir / item.name
                    if item.is_file():
                        shutil.copy2(item, dst)
                        print(f"[OptiScalerInstaller] Copied: {item.name}")
                    elif item.is_dir():
                        shutil.copytree(item, dst, dirs_exist_ok=True)
                        print(f"[OptiScalerInstaller] Copied dir: {item.name}")
            else:
                # No nvngx.dll found, copy entire extracted dir
                print("[OptiScalerInstaller] Copying all extracted files...")
                for item in extracted_dir.rglob("*"):
                    if item.is_file():
                        rel_path = item.relative_to(extracted_dir)
                        dst = self.install_dir / rel_path
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dst)
            
            print("[OptiScalerInstaller] Extraction complete")
            return True
        
        except zipfile.BadZipFile:
            print("[OptiScalerInstaller] Corrupted ZIP file")
            return False
        
        except Exception as e:
            print(f"[OptiScalerInstaller] Extraction error: {e}")
            return False
    
    def verify(self) -> bool:
        """Verify OptiScaler installation
        
        Returns:
            True if valid
        """
        print("[OptiScalerInstaller] Verifying installation...")
        
        # Check for main DLL
        main_dll = self.install_dir / "nvngx.dll"
        if not main_dll.exists():
            print("[OptiScalerInstaller] Main DLL not found")
            return False
        
        # Check file size
        size = main_dll.stat().st_size
        if size < 1024:  # Less than 1KB = invalid
            print(f"[OptiScalerInstaller] Invalid file size: {size} bytes")
            return False
        
        # Check for at least one backend DLL
        backend_dlls = [
            "ffx_fsr3_x64.dll",
            "libxess.dll",
        ]
        
        found_backend = False
        for dll_name in backend_dlls:
            if (self.install_dir / dll_name).exists():
                found_backend = True
                print(f"[OptiScalerInstaller] Found backend: {dll_name}")
                break
        
        if not found_backend:
            print("[OptiScalerInstaller] No backend DLLs found")
            return False
        
        print("[OptiScalerInstaller] Installation verified")
        return True
    
    def install(
        self,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ) -> bool:
        """Download and install OptiScaler
        
        Args:
            progress_callback: Progress callback (status, percent)
        
        Returns:
            True if successful
        """
        print("\n[OptiScalerInstaller] Starting installation...")
        
        try:
            # Step 1: Download (0-50%)
            if progress_callback:
                progress_callback("Downloading", 0)
            
            def download_progress(downloaded, total):
                if total > 0 and progress_callback:
                    percent = int((downloaded / total) * 50)  # 0-50%
                    progress_callback("Downloading", percent)
            
            if not self.download(progress_callback=download_progress):
                raise InstallationError("Download failed")
            
            # Step 2: Extract (50-80%)
            if progress_callback:
                progress_callback("Extracting", 50)
            
            if not self.extract():
                raise InstallationError("Extraction failed")
            
            if progress_callback:
                progress_callback("Extracting", 80)
            
            # Step 3: Verify (80-100%)
            if progress_callback:
                progress_callback("Verifying", 80)
            
            if not self.verify():
                raise InstallationError("Verification failed")
            
            if progress_callback:
                progress_callback("Complete", 100)
            
            # Cleanup temp files
            self._cleanup()
            
            print("[OptiScalerInstaller] Installation complete!")
            return True
        
        except Exception as e:
            print(f"[OptiScalerInstaller] Installation failed: {e}")
            self._cleanup()
            return False
    
    def uninstall(self) -> bool:
        """Uninstall OptiScaler
        
        Returns:
            True if successful
        """
        print("[OptiScalerInstaller] Uninstalling...")
        
        try:
            if self.install_dir.exists():
                shutil.rmtree(self.install_dir)
                print(f"[OptiScalerInstaller] Removed: {self.install_dir}")
            
            self._cleanup()
            
            print("[OptiScalerInstaller] Uninstall complete")
            return True
        
        except Exception as e:
            print(f"[OptiScalerInstaller] Uninstall error: {e}")
            return False
    
    def _cleanup(self):
        """Clean up temporary files"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                print("[OptiScalerInstaller] Cleaned up temp files")
        except Exception as e:
            print(f"[OptiScalerInstaller] Cleanup warning: {e}")
