import os

from biomechzoo.visualization.qc_app import run_quality_check
from biomechzoo.biomechzoo import BiomechZoo

# project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# fld_data = os.path.join(project_root, 'data', 'csv', 'opencap')

fld_data = "/Users/Werk/Documents/Postdoc-McGill/breast-reduction/data/normalize"


subj_pattern = [r"\b\d{3}[A-Z]{2}\b", r"\b\d{3}[A-Z]{3}\b"]
ch = ['gy_shank']

# create zoo files
bmech = BiomechZoo(fld_data, inplace=True, verbose='all')
bmech.table2zoo(extension='csv', skip_rows=0)  # this csv has 10 header rows

run_quality_check(fld=fld_data, ch=ch, out_folder=None, conditions=["pre", "post"], name_contains=["Jogging",],
                  subj_pattern=subj_pattern, event_name=None)



