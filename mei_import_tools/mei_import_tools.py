# __init__.py
from .mei_import_tools import GitHubFileManager, GitHubConfig

# Add this line to prevent circular imports
__package__ = __name__

# mei_import_tools.py
import urllib3
import json
import fnmatch
import os

class GitHubConfig:
    def __init__(self, base_url, **kwargs):
        self.base_url = base_url
        self.__dict__.update(kwargs)

class GitHubFileManager:
    def __init__(self, base_url):
        self.base_url = base_url
        self.owner, self.repo = self._parse_base_url(base_url)
        self.http = urllib3.PoolManager(
            timeout=urllib3.Timeout(total=30),
            maxsize=10,
            cert_reqs='CERT_REQUIRED',
            ca_certs=certifi.where(),
            retries=urllib3.Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504]
            )
        )
    
    def _parse_base_url(self, url):
        parts = url.split('/')
        return parts[-2], parts[-1]
    
    def _get_tree_sha(self, branch='main'):
        api_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/ref/heads/{branch}"
        headers = {
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        response = self.http.request('GET', api_url, headers=headers)
        if response.status != 200:
            raise Exception(f"Failed to fetch tree SHA: {response.data.decode('utf-8')}")
        return json.loads(response.data.decode('utf-8'))['object']['sha']
    
    def _get_raw_url(self, path):
        return f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/main/{path}"
    
    def _match_pattern(self, filename, pattern):
        return fnmatch.fnmatch(filename, pattern)
    
    def list_files(self, directory_path="", patterns=None):
        tree_sha = self._get_tree_sha()
        api_url = f"https://api.github.com/repos/{self.owner}/{self.repo}/git/trees/{tree_sha}"
        params = {'recursive': '1'}
        headers = {
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        response = self.http.request('GET', api_url, fields=params, headers=headers)
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