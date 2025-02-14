from dataclasses import dataclass
from typing import List, Optional
import urllib3
import json
from urllib.parse import urlparse
from functools import partial
import fnmatch
from pathlib import Path
from typing import Dict, Callable

@dataclass
class GitHubConfig:
    """Configuration for GitHub API access"""
    base_url: str
    token: Optional[str] = None
    api_version: str = "2022-11-28"

class GitHubFileManager:
    """A class for managing GitHub repository files"""
    
    def __init__(
        self,
        config: GitHubConfig,
        output_dir: Optional[str] = None,
        verbose: bool = True
    ):
        """Initialize the GitHub file manager with configuration"""
        self.config = config
        self.output_dir = Path(output_dir) if output_dir else Path("github_downloads")
        self.http = urllib3.PoolManager()
        self.verbose = verbose
        self._register_modules()
    
    def _log(self, message: str) -> None:
        """Helper method to control logging output"""
        if self.verbose:
            print(message)
    
    def _register_modules(self) -> None:
        """Register available transformation modules"""
        self._modules: Dict[str, Callable] = {}
        # Add modules here as needed
    
    def _parse_base_url(self, url: str) -> tuple[str, str]:
        """Parse repository owner and name from base URL"""
        parts = url.split('/')
        return parts[-2], parts[-1]
    
    def _get_tree_sha(self, branch: str = 'main') -> str:
        """Get the tree SHA for a given branch"""
        owner, repo = self._parse_base_url(self.config.base_url)
        api_url = f"https://api.github.com/repos/{owner}/{repo}/git/ref/heads/{branch}"
        headers = {
            'Accept': f'application/vnd.github+json',
            'X-GitHub-Api-Version': self.config.api_version
        }
        
        if self.config.token:
            headers['Authorization'] = f'token {self.config.token}'
        
        response = self.http.request('GET', api_url, headers=headers)
        if response.status != 200:
            raise Exception(f"Failed to fetch tree SHA: {response.data.decode('utf-8')}")
            
        return json.loads(response.data.decode('utf-8'))['object']['sha']
    
    def _get_raw_url(self, path: str) -> str:
        """Convert API path to raw.githubusercontent.com URL"""
        owner, repo = self._parse_base_url(self.config.base_url)
        return f"https://raw.githubusercontent.com/{owner}/{repo}/main/{path}"
    
    def _match_pattern(self, filename: str, pattern: str) -> bool:
        """Match filename against pattern"""
        return fnmatch.fnmatch(filename, pattern)
    
    def list_files(
        self,
        directory_path: str = "",
        patterns: Optional[List[str]] = None
    ) -> List[str]:
        """
        List raw URLs of files in a repository directory matching optional patterns
        
        Args:
            directory_path (str): Path to directory within repository
            patterns (List[str]): List of patterns to match filenames against
            
        Returns:
            List[str]: List of raw URLs for matching files
        """
        tree_sha = self._get_tree_sha()
        
        owner, repo = self._parse_base_url(self.config.base_url)
        api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{tree_sha}"
        params = {'recursive': '1'}
        
        response = self.http.request('GET', api_url, fields=params)
        if response.status != 200:
            raise Exception(f"Failed to fetch directory contents: {response.data.decode('utf-8')}")
            
        tree_data = json.loads(response.data.decode('utf-8'))
        urls = []
        
        for item in tree_data['tree']:
            if directory_path and not item['path'].startswith(directory_path):
                continue
                
            if item['type'] == 'blob':
                filename = item['path'].split('/')[-1]
                
                if patterns is None or any(self._match_pattern(filename, pattern) for pattern in patterns):
                    urls.append(self._get_raw_url(item['path']))
                
        return urls