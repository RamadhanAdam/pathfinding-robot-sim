"""
setup.py
---------
Installation script for vacuum cleaner simulation.
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="vacuum-cleaner-ai",
    version="1.0.0",
    author="Ramadhan Zome",
    author_email="your.email@example.com",
    description="AI-powered vacuum cleaner simulation with pathfinding and battery management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/vacuum-cleaner-ai",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "vacuum-sim=main:main",
        ],
    },
)
