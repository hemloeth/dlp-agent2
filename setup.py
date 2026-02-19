from setuptools import setup, find_packages

setup(
    name="dlp-agent",
    version="1.0.0",
    description="Data Loss Prevention Agent for detecting sensitive data",
    author="",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",  # For CLI
    ],
    entry_points={
        "console_scripts": [
            "dlp-agent=dlp_agent.main:main",
        ],
    },
    python_requires=">=3.8",
)
