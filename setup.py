from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="korea-realestate-api",
    version="0.1.0",
    description="Python client for Korean public real estate APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Korea Real Estate API Contributors",
    python_requires=">=3.11",
    packages=find_packages(exclude=["tests*", "examples*"]),
    install_requires=[
        "httpx>=0.27.0",
        "xmltodict>=0.13.0",
        "pandas>=2.0.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "click>=8.1.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.0",
            "respx>=0.21.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "korea-realestate=korea_realestate.__main__:cli",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
