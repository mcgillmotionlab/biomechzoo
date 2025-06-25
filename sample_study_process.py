import os
import shutil
import biomechzoo as bmech
from biomechzoo.utils.copy_files import copy_files
from biomechzoo.engine import engine
from biomechzoo.utils.zload import zload


# Here we demonstrate capabilities of the biomechzoo python
# implementation using the sample study data

# step 0: get root folder of the sample study
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
fld0 = os.path.join(project_root, 'biomechzoo', 'biomechzoo', 'data', 'sample_study', 'raw c3d files')

# step 1: convert c3d files to zoo format (mat files saved with the
# extension '.zoo' and compatible with Matlab)
fld1 = fld0.replace('raw c3d files', '1-c3d2zoo')
shutil.copytree(fld0, fld1, dirs_exist_ok=True)
copy_files(fld0, fld1)
bmech.conversion.c3d2zoo(fld1)

# testing load 1 zoo file
fl = engine(fld1, extension='.zoo', subfolders=['Turn'], name_contains='HC0')[0]
data = zload(fl)
