# make a test python 3.10 env
conda create -n test-bmz python=3.10 -c conda-forge
conda activate test-bmz

# building
cd to biomechzoo-conda where the recipe files are
conda build recipe -c conda-forge
pip install mvnx
conda install --use-local biomechzoo -c conda-forge

# test installation
cd to repo root
python
import biomechzoo
print(biomechzoo.__version__)  