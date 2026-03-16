from biomechzoo.utils.combine_xsens_csv import combine_quats_to_csv
from biomechzoo.visualization.ensembler import Ensembler
from biomechzoo.biomechzoo import BiomechZoo
import os

def main():

    # Combine the quaternions from our two sensors #####################################################

    combine_quats_to_csv(
        csv_files=[rsh_data_long_2, rf_data_long_2, rt_data_long_2, rh_data_long_2],
        prefixes=["RSh", "RF", "RT", "RH"],
        out_folder= out_fld,
        out_filename="123AA_combined.csv"
    )

    combine_quats_to_csv(
        csv_files=[rsh_data_long_3, rf_data_long_3, rt_data_long_3, rh_data_long_3],
        prefixes=["RSh", "RF", "RT", "RH"],
        out_folder= out_fld,
        out_filename="123AB_combined.csv"
    )

    # STEP 0: Initialize our BiomechZoo object #########################################################
    root = os.getcwd()
    fld = os.path.join(root, out_fld)

    bmech = BiomechZoo(
        in_folder=fld,
        inplace = False,
        verbose=2
    )

    # STEP 1: Convert out combined quaternion file into a .zoo file ####################################
    bmech.table2zoo(
        out_folder= "1 - table2zoo_combined",
        extension='.csv',
        freq = 120
    )

    # STEP 2: Calculate the 3D angles between the IMU sensors ##########################################
    bmech.quats2euler(
        prox_prefix="RSh",
        dist_prefix="RF",
        order="XZY",
        out_folder= "2 - relative_angles_combined",
        inplace=False
    )

    bmech.quats2euler(
        prox_prefix="RSh",
        dist_prefix="RH",
        order="XZY",
        out_folder= "2 - relative_angles_combined",
        inplace=False
    )

    bmech.quats2euler(
        prox_prefix="RH",
        dist_prefix="RF",
        order="XZY",
        out_folder= "2 - relative_angles_combined",
        inplace=False
    )

    bmech.quats2euler(
        prox_prefix="RF",
        dist_prefix="RT",
        order="XZY",
        out_folder= "2 - relative_angles_combined",
        inplace=False
    )

    # STEP 3: Add heel strikes using the mcgrath method ###########################################
    bmech.addevent(
        ch="RSh_Gyr_Y",
        event_type="mcgrath_fs",
        event_name="FS",
        out_folder= "3 - add_event"
    )

    # STEP 4: Split by gait cycles #################################################################
    bmech.split_trial_by_gait_cycle(
        first_event_name="FS_1",
        out_folder= "4 - split_trial_by_gait_cycle",
    )


    # STEP 5: Normalize gait cycle lengths ##########################################################
    bmech.normalize(
        out_folder= "5 - normalize"
    )

    # STEP 6: Visualize the results #################################################################
    ensembler = Ensembler(
        fld=bmech.in_folder,
        ch=[
            'RSh_RF_alpha','RSh_RF_beta','RSh_RF_gamma',
            'RSh_RH_alpha', 'RSh_RH_beta', 'RSh_RH_gamma',
            'RH_RF_alpha', 'RH_RF_beta', 'RH_RF_gamma',
            'RF_RT_alpha', 'RF_RT_beta', 'RF_RT_gamma'
        ],
        conditions = [''],
        show_legend = True,
        subj_pattern=r"\d{3}[A-Z]{2}"
    )

    ensembler.cycles()

    ensembler.save(
        file_name="Combined Waveforms",
        extension="jpeg",
        folder = os.path.join(example_root, 'data', 'imu_do_not_upload', '6 - Figures')
    )

    ensembler.average()

    ensembler.save(
        file_name="Mean(SD) Waveforms",
        extension="jpeg",
        folder = os.path.join(example_root, 'data', 'imu_do_not_upload', '6 - Figures')
    )

# Defining the desired file paths:
example_root = os.path.dirname(os.path.dirname(__file__))
common_root = os.path.join(example_root, 'data', 'imu_do_not_upload', 'raw data')
lsh_data_short = os.path.join(common_root, 'short_example ', 'LSh_20250818_114924.csv')
lf_data_short = os.path.join(common_root, 'short_example ','LF_20250818_114924.csv')
rsh_data_long_2 = os.path.join(common_root, 'long_example', '123AA_RSh.csv')
rf_data_long_2 = os.path.join(common_root, 'long_example','123AA_RF.csv')
rt_data_long_2 = os.path.join(common_root, 'long_example','123AA_RT.csv')
rh_data_long_2 = os.path.join(common_root, 'long_example','123AA_RH.csv')
rsh_data_long_3 = os.path.join(common_root, 'long_example', '123AB_RSh.csv')
rf_data_long_3 = os.path.join(common_root, 'long_example','123AB_RF.csv')
rt_data_long_3 = os.path.join(common_root, 'long_example','123AB_RT.csv')
rh_data_long_3 = os.path.join(common_root, 'long_example','123AB_RH.csv')
out_fld = os.path.join(example_root, 'data', 'imu_do_not_upload', '0-create_combined_data')

if __name__ == "__main__":
    main()
