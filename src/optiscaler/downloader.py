#!/usr/bin/env python3
"""OptiScaler Download Manager

Version: 0.3.5d (package 3.8a, stage 3/6)
"""
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Callable, Dict, Any

from .types import InstallationError


class GitHubAPI:
    """GitHub API client for OptiScaler releases"""
    
    API_BASE = "https://api.github.com"
    REPO_OWNER = "optiscaler"
    REPO_NAME = "OptiScaler"
    
    def __init__(self):
        self.base_url = f"{self.API_BASE}/repos/{self.REPO_OWNER}/{self.REPO_NAME}"
    
    def get_latest_release(self) -> Optional[Dict[str, Any]]:
        """Get latest OptiScaler release from GitHub
        
        Returns:
            Release data dict or None
        """
        url = f"{self.base_url}/releases/latest"
        
        try:
            print(f"[GitHubAPI] Fetching latest release...")
            
            request = urllib.request.Request(url)
            request.add_header('Accept', 'application/vnd.github.v3+json')
            request.add_header('User-Agent', 'PartMart-Boost')
            
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read())
                
                version = data.get('tag_name', 'unknown')
                print(f"[GitHubAPI] Latest version: {version}")
                
                return data
        
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print("[GitHubAPI] Repository or releases not found")
            elif e.code == 403:
                print("[GitHubAPI] Rate limit exceeded")
            else:
                print(f"[GitHubAPI] HTTP error: {e.code}")
            return None
        
        except Exception as e:
            print(f"[GitHubAPI] Error fetching release: {e}")
            return None
    
    def get_download_url(self, release: Dict[str, Any]) -> Optional[str]:
        """Extract download URL from release data
        
        Args:
            release: Release data from GitHub API
        
        Returns:
            Download URL or None
        """
        assets = release.get('assets', [])
        
        # Look for ZIP file
        for asset in assets:
            name = asset.get('name', '').lower()
            if name.endswith('.zip'):
                url = asset.get('browser_download_url')
                if url:
                    print(f"[GitHubAPI] Found asset: {asset['name']}")
                    return url
        
        # Fallback: use source code ZIP
        zipball_url = release.get('zipball_url')
        if zipball_url:
            print("[GitHubAPI] Using source code archive")
            return zipball_url
        
        print("[GitHubAPI] No download URL found")
        return None


class Downloader:
    """File downloader with progress tracking"""
    
    CHUNK_SIZE = 8192  # 8KB chunks
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    def __init__(self):
        self.progress_callback: Optional[Callable[[int, int], None]] = None
    
    def download(
        self,
        url: str,
        destination: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> bool:
        """Download file from URL
        
        Args:
            url: Download URL
            destination: Save path
            progress_callback: Progress callback (downloaded, total)
        
        Returns:
            True if successful
        """
        self.progress_callback = progress_callback
        
        for attempt in range(self.MAX_RETRIES):
            try:
                print(f"[Downloader] Attempt {attempt + 1}/{self.MAX_RETRIES}")
                print(f"[Downloader] URL: {url}")
                print(f"[Downloader] Destination: {destination}")
                
                # Create parent directory
                destination.parent.mkdir(parents=True, exist_ok=True)
                
                # Start download
                request = urllib.request.Request(url)
                request.add_header('User-Agent', 'PartMart-Boost')
                
                with urllib.request.urlopen(request, timeout=30) as response:
                    # Get total size
                    total_size = int(response.headers.get('Content-Length', 0))
                    downloaded = 0
                    
                    print(f"[Downloader] Size: {total_size / (1024*1024):.2f} MB")
                    
                    # Download in chunks
                    with open(destination, 'wb') as f:
                        while True:
                            chunk = response.read(self.CHUNK_SIZE)
                            if not chunk:
                                break
                            
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Progress callback
                            if self.progress_callback and total_size > 0:
                                self.progress_callback(downloaded, total_size)
                    
                    print(f"[Downloader] Downloaded: {downloaded / (1024*1024):.2f} MB")
                    return True
            
            except urllib.error.URLError as e:
                print(f"[Downloader] Network error: {e}")
                if attempt < self.MAX_RETRIES - 1:
                    print(f"[Downloader] Retrying in {self.RETRY_DELAY}s...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    print("[Downloader] Max retries reached")
                    return False
            
            except Exception as e:
                print(f"[Downloader] Download error: {e}")
                return False
        
        return False
