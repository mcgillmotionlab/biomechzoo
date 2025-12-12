import os

from biomechzoo.visualization.qc_app import run_quality_check


root= os.getcwd()
fld = "/Users/Werk/Documents/Postdoc-McGill/breast-reduction/data/normalize"
out_folder = os.path.join(root, 'outlier_report')

subj_pattern = [r"\b\d{3}[A-Z]{2}\b", r"\b\d{3}[A-Z]{3}\b"]

run_quality_check(fld=fld, ch="gy_shank", out_folder=out_folder, conditions="pre", name_contains=["Walking"],
                  subj_pattern=subj_pattern)

