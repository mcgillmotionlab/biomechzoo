import os
from biomechzoo.visualization.ensembler import Ensembler


# get raw data folder
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fld_data = os.path.join(project_root, 'data', 'csv', 'opencap')

out_folder = os.path.join(project_root, 'data', 'csv', 'QC')
ensembler = Ensembler(fld=fld_data, ch=['knee_angle_r'],
                      conditions=['Post'],
                      name_contains=["jogging", '_r.'],
                      out_folder=out_folder
                      )

# This will plot individual gait cycles with events.
ensembler.quality_check_cycles()