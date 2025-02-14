from setuptools import setup, find_packages

setup(
    name='intervals_mei_tools',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'urllib3',
        'certifi',
        'json',
        'fnmatch'
    ],
    python_requires='>=3.6'
)