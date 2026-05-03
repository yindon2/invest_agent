from setuptools import setup, find_packages

setup(
    name="invest-agent",
    version="1.0.0",
    description="投资学AI Agent - 基于Claude Code Agent能力框架",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="yindon2",
    url="https://github.com/yindon2/invest_agent",
    py_modules=["agent"],
    packages=find_packages(),
    install_requires=[
        "akshare>=1.18.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "scipy>=1.10.0",
        "statsmodels>=0.14.0",
    ],
    entry_points={
        "console_scripts": [
            "invest-agent=agent:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.10",
)
