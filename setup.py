from setuptools import setup, find_packages

setup(
    name='intervals-mei-tools',
    version='0.1.0',
    description='Tools for working with MEI intervals',
    author='Richard Freedman',
    author_email='richard.freedman@example.com',  # Update email address
    url='https://github.com/RichardFreedman/intervals_mei_tools',
    
    packages=[''],
    py_modules=['mei_import_tools'],
    
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    
    python_requires='>=3.6',
)