from biomechzoo.biomechzoo import BiomechZoo
from biomechzoo.utils.find_repo_root import find_repo_root
import os

project_root = find_repo_root(os.getcwd())
fld_raw_data = os.path.join(project_root, 'data', 'PAT_IMU_do_not_upload', 'raw')


def main():

    # STEP 0: Initialize our BiomechZoo object #########################################################################
    bmech = BiomechZoo(
        in_folder=fld_raw_data,
        inplace = False,
        verbose=2,
    )

    # STEP 1: Convert csv data to .zoo file ############################################################################
    bmech.table2zoo(
        out_folder= "1-table2zoo",
        extension='.csv',
    )

    # STEP 2: Clean the data ###########################################################################################
    ch = ['ax_m/s/s', 'ay_m/s/s', 'az_m/s/s', 'time_s']
    bmech.removechannel(
        mode='keep',
        ch=ch,
        out_folder='2-clean',
    )

    bmech.renamechannel(
        ch_current=ch,
        ch_new=['ax', 'ay', 'az', 'time'],
        out_folder='2-clean',
        inplace=True,
    )


    # STEP 4: COMPUTE NON-LINEAR DYNAMICS ##############################################################################
    bmech.signal_analysis(
        channels=['ax', 'ay', 'az'],
        etype='ldlj',
        out_folder='3-non-linear dynamics',
        inplace=False,
    )



if __name__ == "__main__":
    main()
