from setuptools import setup

setup(
    name="provision",
    version="0.0.1",
    packages=["provision"],
    entry_points={"console_scripts": ["provision = provision.cli:cli"]},
)
