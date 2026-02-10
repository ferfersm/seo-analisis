"""
Setup configuration for gsc-analytics package.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gsc-analytics",
    version="2.0.0",
    author="Data Growth Lab",
    author_email="your.email@example.com",
    description="Advanced analytics module for Google Search Console data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TU_USUARIO/gsc-analytics",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        "python-dateutil>=2.8.0",
        "searchconsole @ git+https://github.com/joshcarty/google-searchconsole",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
        ],
    },
)
