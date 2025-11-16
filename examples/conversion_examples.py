import os
from biomechzoo.biomechzoo import BiomechZoo
# get raw data folder
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fld_data = os.path.join(project_root, 'data')

#### Testing all conversion functions #############

# csv for opencap for all subfolders called opencap within fld_data_csv (only 1 file should process)
fld_data_csv = os.path.join(fld_data, 'other')
bmech = BiomechZoo(fld_data_csv, inplace=False, verbose='all', subfolders='opencap')
bmech.table2zoo(out_folder='csv', extension='csv', skip_rows=10)  # this csv has 10 header rows

# parquet2zoo for all files in fld_data_parquet containing the word Subject in the file name
fld_data_parquet = os.path.join(fld_data, 'other')
bmech = BiomechZoo(fld_data_parquet, inplace=False, verbose='all', name_contains='Subject')
bmech.table2zoo(out_folder='parquet2zoo', extension='.parquet', freq=60)

# mvnx
fld_data_mvnx = os.path.join(fld_data, 'other')
bmech = BiomechZoo(fld_data_mvnx, inplace=False, verbose='all')
bmech.mvnx2zoo(out_folder='mvnx')