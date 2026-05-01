[![Docs](https://readthedocs.org/projects/biomechzoo/badge/?version=latest)](https://biomechzoo.readthedocs.io/)
[![PyPI version](https://img.shields.io/pypi/v/biomechzoo)](https://pypi.org/project/biomechzoo/)

# BiomechZoo
BiomechZoo is a biomechanics processing toolbox for human movement analysis.

## Installation
- Install the latest stable version: ``pip install biomechzoo``
- Install a specific version ``pip install biomechzoo==0.7.18``
- Upgrade your installation to the latest version ``pip install --upgrade biomechzoo``

## Compatibility
- Python 3.11 is the supported version
- Core dependencies are optimized for modern scientific Python stacks

## Readthedocs
- See documentation https://biomechzoo.readthedocs.io/en/latest/

## Developer notes

### Github version
- clone the repository here: http://www.github.com/mcgillmotionlab/biomechzoo 

### Installing a dev environment
- conda create -n biomechzoo-dev python=3.11
- conda activate biomechzoo-dev
- cd biomechzoo root folder
- pip install -e ".[dev]"

### IDE setup (PyCharm)
- If imports are not resolving, mark the `src/` directory as a source root.