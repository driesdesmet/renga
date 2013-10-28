import os
from setuptools import setup, find_packages


def get_desc(module):
    """Use the docstring of the __init__ file to be the description"""

    return " ".join(__import__(module).__doc__.splitlines()).strip()


def read_file(filename):
    """Read a file into a string"""
    
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''


def get_readme():
    """Return the README file contents. Supports text,rst, and markdown"""
    
    for name in ('README', 'README.rst', 'README.md'):
        if os.path.exists(name):
            return read_file(name)
    return ''


setup(
    name="renga",
    version="0.1a",
    url="https://github.com/driesdesmet/renga",
    author='Dries Desmet',
    author_email='dries@urga.be',
    description=get_desc("renga"),
    long_description=get_readme(),
    packages=find_packages(),
    scripts=['deploy', 'create'],
    include_package_data=True,
    install_requires=read_file('requirements.txt'),
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Development Status :: 1 - Planning',
    ],
)
