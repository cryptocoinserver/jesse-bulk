from setuptools import setup, find_packages

# also change in version.py
VERSION = '0.1.5'
DESCRIPTION = "Bulk backtesting for jesse"

REQUIRED_PACKAGES = [
    'jesse',
    'pyyaml',
    'joblib'
]

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='jesse-bulk',
    version=VERSION,
    author="cryptocoinserver",
    packages=find_packages(),
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cryptocoinserver/jesse-bulk",
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
