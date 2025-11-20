
from setuptools import setup, find_packages

setup(
    name="codex-enterprise",
    version="6.1.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'codex = codex_enterprise.cli:main',
        ],
    },
)
