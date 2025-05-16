from setuptools import setup, find_packages

setup(
    name="smart_support_agent",
    version="0.1.0",
    packages=find_packages(include=["core*", "cli*", "config*", "factory*"]),
    install_requires=[
        "click>=8.1.0",
        "numpy>=1.24.0",
        "faiss-cpu>=1.7.4",
        "requests>=2.31.1",
        "python-dotenv>=1.0.4",
        "unstructured>=0.14.3",
        "langchain-text-splitters>=0.0.1",
        "beautifulsoup4>=4.12.0",
        "pypdf>=3.17.0",
        "langchain-core>=0.1.7",
        "langchain-community>=0.3.0",
        "requests-html>=0.10.0",
    ],
    extras_require={
        "test": [
            "pytest>=7.3.0",
            "pytest-cov>=4.1.0",
        ],
    },
)
