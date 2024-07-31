from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="chatlet",
    version="0.1.0",
    author="Slava Vishnyakov",
    author_email="bomboze@gmail.com",
    description="A Python wrapper for the OpenRouter API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/slava-vishnyakov/chatlet",
    packages=find_packages(),
    install_requires=[
        "requests",
        "python-dotenv",
        "fastcore",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
)
