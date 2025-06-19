from setuptools import setup, find_packages

setup(
    name="biomechzoo",
    version="0.1.0",
    author="Philippe C. Dixon",
    author_email="phil.dixon@mcgill.ca",
    description="Python port of the BiomechZoo biomechanics toolbox",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mcgillmotionlab/biomechzoo_python",  # Update this
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib",
        "ezc3d",  # or other core dependencies
    ],
    python_requires='>=3.10',
)
