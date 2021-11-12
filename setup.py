from setuptools import setup, find_packages

# also change in version.py
VERSION = '0.1.2'
DESCRIPTION = "Bulk backtesting for jesse"

REQUIRED_PACKAGES = [
    'jesse',
    'pyyaml',
]

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='jesse-bulk',
    version=VERSION,
    author="Saleh Mir",
    author_email="algo@hey.com",
    packages=find_packages(),
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://jesse.trade",
    project_urls={
        'Documentation': 'https://docs.jesse.trade',
        'Say Thanks!': 'http://forum.jesse.trade/',
        'Source': 'http://github.com/jesse-ai/jesse',
        'Tracker': 'https://github.com/jesse-ai/jesse/issues',
    },
    install_requires=REQUIRED_PACKAGES,
    entry_points='''
        [console_scripts]
        jesse-bulk=jesse_bulk.__init__:cli
    ''',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    include_package_data=True,
)
