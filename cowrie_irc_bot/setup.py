from setuptools import setup, find_packages

# Read version from __init__.py
with open('src/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('"\'')
            break
    else:
        version = '0.1.0'

# Read long description from README
with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name="cowrie_irc_bot",
    version=version,
    description="Monitor Cowrie honeypot logs and send alerts to IRC",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="xKippo-lite Team",
    author_email="info@example.com",
    url="https://github.com/example/cowrie-irc-bot",
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.8',
    install_requires=[
        "irc>=20.0.0",
        "pytz>=2023.3",
    ],
    extras_require={
        "geo": ["geoip2>=4.7.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.1.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        'console_scripts': [
            'cowrie-irc-bot=src.main:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
    ],
)