import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SofaModel",
    version="0.1.002",
    author="Gaëtan Desrues",
    author_email="gaetan.desrues@inria.fr",
    url="https://gitlab.inria.fr/gdesrues1/basesofamodel",
    description="Description",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["SofaModel"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
