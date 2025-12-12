import os

from biomechzoo.visualization.qc_app import run_quality_check


project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fld_data = os.path.join(project_root, 'data', 'csv', 'opencap')

subj_pattern = [r"\b\d{3}[A-Z]{2}\b", r"\b\d{3}[A-Z]{3}\b"]
ch = ['hip_flexion_r']

run_quality_check(fld=fld_data, ch=ch, out_folder=None, conditions=["Pre", "Post"], name_contains=["jogging", '_r.'],
                  subj_pattern=subj_pattern)

