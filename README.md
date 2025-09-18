# Repository for the Python version of biomechZoo
This is a development version of the biomechzoo toolbox for python. To use biomechzoo
as a packagage alongside your code, follow the "How to install" instructions below

## How to install 
- make sure the local version of your code sits at the same level as biomechzoo. 
e.g.
code_root/
code_root/biomechzoo/         ← the repo with the actual package
code_root/student_code/       ← where your scripts or notebooks live
    
- open terminal or command window
- create an environment for your research project: ``conda create -n name python=3.13 -c conda-forge``, where name is of your choice
- activate your new environment: ``conda activate name``
- navigate to parent directory where biomechzoo was cloned. e.g. ``code_root``
- install biomechzoo: ``pip install -e biomechzoo``
- install additional requirements: ``pip install -r biomechzoo/pip_requirements.txt``

## Updates (not tested)
- If updates are made to biomechzoo, simply pull the latest version 
  from github, you won't need to reinstall (unless there are new dependencies)

## Usage notes
- To use biomechzoo in your project, you will need to import biomechzoo as: 
``from biomechzoo.biomechzoo import BiomechZoo``
- Then, you can create an object that is an instance of the BimechZoo class as:
``bmech = BiomechZoo(fld)`` where ``fld`` is the path to your data


# opencap users
- opencap users should pre-process their data using ``https://github.com/stanfordnmbl/opencap-processing``
- processed data could be saved to csv using pandas and then imported to biomechzoo using csv2zoo (not yet functional)