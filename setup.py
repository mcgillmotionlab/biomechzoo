from setuptools import setup, find_packages

setup(
    name="biomechzoo",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib",
        "ezc3d",
        "pandas",
        "mvnx",
    ],
)
