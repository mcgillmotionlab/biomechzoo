from Josh_MSc.utils.csv_combine import combine_quats_to_csv
from biomechzoo.visualization.ensembler import Ensembler
from biomechzoo.utils.zload import zload
import matplotlib.pyplot as plt
from biomechzoo.biomechzoo import BiomechZoo
import os

def main():

    data_root = os.path.dirname(os.path.dirname(__file__))

    LSh_data = os.path.join(data_root, 'data', 'imu_do_not_upload', 'LSh_20250818_114924.csv')
    LF_data = os.path.join(data_root, 'data', 'imu_do_not_upload', 'LF_20250818_114924.csv')
    out_folder = os.path.join(data_root, 'data', 'imu_do_not_upload', '0-create_combined_data')

    # Combine the quaternions from our two sensors:
    combine_quats_to_csv(
        csv_files=[LSh_data, LF_data],
        prefixes=["LSh", "LF"],
        out_folder= out_folder,
        out_filename="sample_combined_quats.csv"
    )

    # Initialize our BiomechZoo object
    root = os.getcwd()
    data_fld = out_folder
    fld = os.path.join(root, data_fld)

    bmech = BiomechZoo(
        in_folder=fld,
        verbose=2
    )

    # Convert out combined quaternion file into a .zoo file
    bmech.table2zoo(
        out_folder= "1 - table2zoo_combined",
        extension='.csv',
        inplace=False
    )

    # Calculate the 3D angles between the IMU sensors
    bmech.imu_angles(
        prox_prefix="LSh",
        dist_prefix="LF",
        order="XZY",
        out_folder= "2 - relative_angles_combined",
        inplace=False
    )


    # # Add heel strikes using the mcgrath method
    # bmech.addevent(
    #     ch="gamma",
    #     event_type="mcgrath_fs",
    #     event_name="FS",
    #     out_folder= "3 - add_event",
    #     fsamp = 120
    # )
    #
    # # Split by gait cycles
    # bmech.split_trial_by_gait_cycle(
    #     first_event_name="FS",
    #     out_folder= "4 - split_trial_by_gait_cycle",
    # )

    # Normalize gait cycle lengths
    # bmech.normalize(out_folder= "5 - normalize"
    # )

    # Visualize the results
    ##Ensembler()


data_root = os.path.dirname(os.path.dirname(__file__))

example_data = os.path.join(data_root, 'data', 'imu_do_not_upload', '2 - relative_angles_combined','sample_combined_quats.zoo')

if __name__ == "__main__":
    main()

    angles_imu = zload(example_data)

    angle_keys = ['alpha', 'beta', 'gamma']

    # Plot each angle
    for key in angle_keys:
        plt.plot(angles_imu[key]['line'], label=key)
        plt.xlabel('Time (frames)')
        plt.ylabel(f' {key} (degrees)')
        plt.legend()
        plt.show()
