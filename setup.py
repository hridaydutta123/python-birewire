from setuptools import setup, find_packages

setup(
    name="network-communities-randomization",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "networkx>=2.6.3",
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "rpy2>=3.4.5",
        "tqdm>=4.62.0",
    ],
    author="Hridoy Sankar Dutta",
    description="A tool for randomizing bipartite networks while preserving degree distributions",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)