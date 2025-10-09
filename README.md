# BiomechZoo for Python
This is a development version of the biomechzoo toolbox for python. 

## How to install 
- biomechZoo for python is now an official package, you can simply add biomechZoo to your environment using
``pip install biomechzoo``

## Usage notes
- If you need to install a specific version, run ``pip install biomechzoo==x.x.x`` where x.x.x is the version number. 
- If you need to update biomechzoo to the latest version in your env, run ``pip install biomechzoo --upgrade``

## Dependencies notes
- We use Python 3.11 for compatibility with https://github.com/stanfordnmbl/opencap-processing
- We use Numpy 2.2.6 for compatibility with https://pypi.org/project/numba/

See also http://www.github.com/mcgillmotionlab/biomechzoo or http://www.biomechzoo.com for more information

## Developer notes

### Installing a dev environment
conda create -n biomechzoo-dev python=3.11
conda activate biomechzoo-dev
cd biomechzoo root folder
pip install -e ".[dev]"

### import issues
if using PyCharm: 
- Right-click on src/.
- Select Mark Directory as → Sources Root.