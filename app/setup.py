from setuptools import setup, find_packages

with open("dependencies.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="input_processor_api",
    version="0.1.0",
    packages=find_packages(),
    install_requires=requirements
)
