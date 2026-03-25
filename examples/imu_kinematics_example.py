from biomechzoo.visualization.ensembler import Ensembler
from biomechzoo.biomechzoo import BiomechZoo
import os


# Defining the desired file paths:
example_root = os.path.dirname(os.path.dirname(__file__))

def main():

    # STEP 0: Initialize our BiomechZoo object #########################################################

    bmech = BiomechZoo(
        in_folder=os.path.join(example_root, 'data', 'imu_xsens_dot', 'raw data'),
        inplace = False,
        verbose=2
    )

    # STEP 1: Convert out combined quaternion file into a .zoo file ####################################
    bmech.table2zoo(
        out_folder= "1 - table2zoo",
        extension='.csv',
        freq = 120
    )

    # STEP 2: Convert out combined quaternion file into a .zoo file ####################################
    bmech.combine_files(
        within=True,
        suffix=['RF', 'RH', 'RSh', 'RT'],
        out_folder="2 - combined",
    )

    # STEP 3: Calculate the 3D angles between the IMU sensors ##########################################
    bmech.quats2euler(ch_prox=['Quat_W_RSh', 'Quat_X_RSh', 'Quat_Y_RSh', 'Quat_Z_RSh'],
                      ch_dist=['Quat_W_RF', 'Quat_X_RF', 'Quat_Y_RF', 'Quat_Z_RF'],
                      sequence="XZY",
                      out_folder="3 - relative_angles_combined", inplace=False)

    bmech.quats2euler(ch_prox=['Quat_W_RSh', 'Quat_X_RSh', 'Quat_Y_RSh', 'Quat_Z_RSh'],
                      ch_dist=['Quat_W_RH', 'Quat_X_RH', 'Quat_Y_RH', 'Quat_Z_RH'],
                      sequence="XZY",
                      out_folder="3 - relative_angles_combined", inplace=False)

    bmech.quats2euler(ch_prox=['Quat_W_RH', 'Quat_X_RH', 'Quat_Y_RH', 'Quat_Z_RH'],
                      ch_dist=['Quat_W_RF', 'Quat_X_RF', 'Quat_Y_RF', 'Quat_Z_RF'],
                      sequence="XZY",
                      out_folder="3 - relative_angles_combined", inplace=False)

    bmech.quats2euler(ch_prox=['Quat_W_RF', 'Quat_X_RF', 'Quat_Y_RF', 'Quat_Z_RF'],
                      ch_dist=['Quat_W_RT', 'Quat_X_RT', 'Quat_Y_RT', 'Quat_Z_RT'],
                      sequence="XZY",
                      out_folder="3 - relative_angles_combined", inplace=False)

    # STEP 3: Add heel strikes using the mcgrath method ###########################################
    bmech.addevent(
        ch="Gyr_Y_RSh",
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
        conditions = ['123AA','123AB'],
        show_legend = True,
        subj_pattern=r"\d{3}[A-Z]{2}"
    )

    ensembler.cycles()

    ensembler.save(
        file_name="Combined Waveforms",
        extension="jpeg",
        folder = os.path.join(example_root, 'data', 'imu_xsens_dot', '6 - Figures')
    )

    ensembler.average()

    ensembler.save(
        file_name="Mean(SD) Waveforms",
        extension="jpeg",
        folder = os.path.join(example_root, 'data', 'imu_xsens_dot', '6 - Figures')
    )

if __name__ == "__main__":
    main()
