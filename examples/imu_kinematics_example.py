from Josh_MSc.utils.csv_combine import combine_quats_to_csv
from biomechzoo.visualization.ensembler import Ensembler
from biomechzoo.utils.zload import zload
import matplotlib.pyplot as plt
from biomechzoo.biomechzoo import BiomechZoo
import os

example_root = os.path.dirname(os.path.dirname(__file__))

lsh_data = os.path.join(example_root, 'data', 'imu_do_not_upload', 'LSh_20250818_114924.csv')
lf_data = os.path.join(example_root, 'data', 'imu_do_not_upload', 'LF_20250818_114924.csv')
out_fld = os.path.join(example_root, 'data', 'imu_do_not_upload', '0-create_combined_data')

def main():

    # Combine the quaternions from our two sensors
    combine_quats_to_csv(
        csv_files=[lsh_data, lf_data],
        prefixes=["LSh", "LF"],
        out_folder= out_fld,
        out_filename="sample_combined_quats.csv"
    )

    # STEP 0: Initialize our BiomechZoo object
    root = os.getcwd()
    fld = os.path.join(root, out_fld)

    bmech = BiomechZoo(
        in_folder=fld,
        inplace = False,
        verbose=2
    )

    # STEP 1: Convert out combined quaternion file into a .zoo file
    bmech.table2zoo(
        out_folder= "1 - table2zoo_combined",
        extension='.csv',
        freq = 120
    )

    # STEP 2: Calculate the 3D angles between the IMU sensors
    bmech.imu_angles(
        prox_prefix="LSh",
        dist_prefix="LF",
        order="XZY",
        out_folder= "2 - relative_angles_combined",
        inplace=False
    )

    # STEP 3: Add heel strikes using the mcgrath method
    bmech.addevent(
        ch="LSh_Gyr_Y",
        event_type="mcgrath_fs",
        event_name="FS",
        out_folder= "3 - add_event"
    )

    # STEP 4: Split by gait cycles
    bmech.split_trial_by_gait_cycle(
        first_event_name="FS_1",
        out_folder= "4 - split_trial_by_gait_cycle",
    )


    # STEP 5: Normalize gait cycle lengths
    # TODO: Note that the normalize_data.py function was altered to ensure that every channel had an 'event' column
    bmech.normalize(
        out_folder= "5 - normalize"
    )

    # STEP 6: Visualize the results
    ensembler = Ensembler(
        fld=bmech.in_folder,
        ch=['LSh_LF_alpha','LSh_LF_beta','LSh_LF_gamma'],
        conditions = [''],
        subj_pattern=r".*"
    )
    ensembler.cycles()
    ensembler.average()
    ensembler.save(file_name="individual gait cycles")



if __name__ == "__main__":
    main()

    data_root = os.path.dirname(os.path.dirname(__file__))

    example_data = os.path.join(data_root, 'data', 'imu_do_not_upload', '2 - relative_angles_combined',
                                'sample_combined_quats.zoo')
    # PLOT THE RESULTING ANGLES
    angles_imu = zload(example_data)
    angle_keys = ['LSh_LF_alpha', 'LSh_LF_beta', 'LSh_LF_gamma', 'LSh_Gyr_Y']
    for key in angle_keys:
        plt.plot(angles_imu[key]['line'], label=key)
        plt.xlabel('Time (frames)')
        plt.ylabel(f' {key} (degrees)')
        plt.legend()
        plt.show()
