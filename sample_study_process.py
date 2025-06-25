import os
import biomechzoo as bmech
from biomechzoo.utils.copy_files import copy_files

# Here we demonstrate capabilities of the biomechzoo python
# implementation using the sample study data

# step 0: get root folder of the sample study
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
fld0 = os.path.join(project_root, 'biomechzoo/data', 'sample_study', 'raw c3d files')

# step 1: convert c3d files to zoo format (mat files saved with the
# extension '.zoo' and compatible with Matlab)
fld1 = fld0.replace(fld0, 'raw c3d files', '1-c3d2zoo')
copy_files(fld0, fld1)
bmech.conversion.c3d2zoo(fld1)
