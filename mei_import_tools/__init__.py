# __init__.py
def get_github_manager():
    from mei_import_tools import GitHubFileManager
    return GitHubFileManager

def get_config():
    from mei_import_tools import GitHubConfig
    return GitHubConfig

__package__ = __name__
__all__ = ['get_github_manager', 'get_config']



# old version
# __init__.py
# from mei_import_tools import GitHubFileManager, GitHubConfig

# __package__ = __name__
# __all__ = ['GitHubFileManager', 'GitHubConfig']

