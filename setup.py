from pathlib import Path

from setuptools import setup, find_packages

import hysterical_ticket

# pip install -U twine
# python setup.py sdist bdist_wheel && python -m twine upload dist/*
setup(
    name="hysterical_ticket",
    description="歇斯底里的双色球！But Chat with LLM",
    version=hysterical_ticket.__version__,
    keywords=["XLangAI", "ClaudeAI", "hysterical_ticket"],
    author="QIN2DIM",
    author_email="yaoqinse@gmail.com",
    long_description=Path(__file__).parent.joinpath("README.md").read_text(encoding="utf8"),
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/QIN2DIM/hysterical_ticket",
    packages=find_packages(
        include=["hysterical_ticket", "hysterical_ticket.*", "LICENSE"], exclude=["tests"]
    ),
    install_requires=[
        "httpx>=0.24.1",
        "pyyaml>=6.0.1",
        "easygui>=0.98.3",
        "pyperclip>=1.8.2",
        "bs4>=0.0.1",
        "beautifulsoup4>=4.12.2",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
    ],
)
