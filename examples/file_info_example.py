from pathlib import Path

from biomechzoo.biomechzoo import BiomechZoo


project_root = Path(__file__).resolve().parents[1]
data_folder = project_root / 'data' / 'sample_study' / 'normalized'

# Inspect a specific sample file from the repository's data folder.
bmech = BiomechZoo(str(data_folder))
bmech.file_info('HC030A/Straight/HC030A05.zoo', head_rows=3)

# To inspect a random .zoo file in data_folder instead, use:
# bmech.file_info(head_rows=3)
