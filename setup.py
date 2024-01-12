import re
from setuptools import setup


with open('README.md') as f:
    readme = f.read()


version = ''
with open('traefik-py/__init__.py') as f:
    version = re.search(r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read()).group(1)
