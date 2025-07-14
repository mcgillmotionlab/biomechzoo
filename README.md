# Repository for the Python version of biomechZoo

### suggested structure
biomechzoo/
├── __init__.py
├── biomechzoo.py           # Contains BiomechZoo class (batch public methods)
├── processing/
│   ├── __init__.py
│   ├── normalize_data.py   # File-level processing function
│   └── normalize_line.py   # Channel-level processing function
└── utils/
    ├── __init__.py
    └── engine.py           # engine function to list files


## Environment

cd to the root folder of the repository in the terminal or command window, and run the following commands:

``conda create -n biomechzoo python=3.9 -y``

``conda activate biomechzoo``

``conda install -r requirements.txt``