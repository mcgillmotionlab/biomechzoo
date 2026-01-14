## Code modified from "https://github.com/mcgillmotionlab/OpenSense-DOTS/tree/main"

# create a .sto file for calibration and another one for imu inverse kinematics from Excel file
# if the .sto files already exist, they will be deleted

import pandas as pd
import numpy as np
from scipy.spatial.transform import Rotation as R
from biomechzoo.conversion.table2zoo_data import table2zoo_data
import os

def create_sto(freq:int, path:str, segments:dict)-> None:

    """
    Creates a .sto file to interface with OpenSense

    :param freq:
    :param path:
    :param out_name:
    :param segments: dictionary formated with the excel ranges on the excel file you can find the quaternions for the
                associated segments. e.g.,

                segments = { # segment name + column name in the excel file (raw data)
                    'tibia_r': 'A:D',
                    'calcn_r': 'E:H',
                    'forefoot_r': 'I:L',
                    'digits_r': 'M:P',
                }

    :return:

    """

    sto_file_cal = "orientation_pose.sto"  # name of .sto file that will be created for calibration
    sto_file = "orientation.sto"  # name of .sto file that will be created for inverse kinematics
    Q = {}

    data_quat = {}

    if path == "" or filename == "":
        print("The path or the name of the file is empty")
    else:

        # delete sto file if it already exists
        if os.path.isfile(path + sto_file):
            os.remove(path + sto_file)

        # import data from excel file
        for name, col_range in segments.items():
            data = pd.read_excel(path + filename, sheet_name, usecols=col_range, header=0)
            print(f"...importing {name} data")

            quaternions = data.to_numpy()[:, [1, 2, 3, 0]]
            r_all = R.from_quat(quaternions)
            Q[name] = r_all

        # Calculate time based on length and sampling frequency
        sampling_rate = freq
        num_samples = len(list(Q.values())[0])
        time = np.arange(num_samples) / sampling_rate

        # build data structure for .sto file
        for name in Q:
            q_array = Q[name].as_quat()  # returns (n, 4): [x, y, z, w]
            q_array = q_array[:, [3, 0, 1, 2]]  # reorder to w, x, y, z
            data_quat[f"{name}_imu"] = [','.join(f"{v:.8f}" for v in row) for row in q_array]

        # write calibration file (first frame)
        with open(path + sto_file_cal, 'w') as f:
            f.write("DataRate=120\n")
            f.write("DataType=Quaternion\n")
            f.write("version=3\n")
            f.write("OpenSimVersion=4.5\n")
            f.write("endheader\n")
            f.write("time\t" + '\t'.join(data_quat.keys()) + '\n')

            line = f"{time[0]:.5f}\t" + '\t'.join(data_quat[seg][0] for seg in data_quat)
            f.write(line + '\n')

        # write inverse kinematics file (all the data)
        with open(path + sto_file, 'w') as f:
            f.write("DataRate=120\n")
            f.write("DataType=Quaternion\n")
            f.write("version=3\n")
            f.write("OpenSimVersion=4.5\n")
            f.write("endheader\n")
            f.write("time\t" + '\t'.join(data_quat.keys()) + '\n')

            for i in range(len(time)):
                line = f"{time[i]:.5f}\t" + '\t'.join(data_quat[seg][i] for seg in data_quat)
                f.write(line + '\n')

    print(f"...imported {sto_file} to {path}")

### VARIABLES ###

freq = 120
path = "/Users/joshualowery/Desktop/test_data/" # folder that contains Excel file with Link raw data
filename = "orientation_test.xlsx" # name of file with raw data
sheet_name = 0 # index of the first sheet named 'Segment Orientation - Quad' (index starts at 0)
segments = { # segment name + column name in the excel file (raw data)
        'tibia_r': 'A:D',
        'calcn_r': 'E:H',
        'forefoot_r': 'I:L',
        'digits_r': 'M:P',
    }
sto_file_cal = "orientation_pose.sto" # name of .sto file that will be created for calibration
sto_file = "orientation.sto" # name of .sto file that will be created for inverse kinematics

Q = {}
time = None
data_quat = {}

### ---------------------------------------------------------------------------------------------------------------------

if path == "" or filename == "":
    print("The path or the name of the file is empty")
else :

    # delete sto file if it already exists
    if os.path.isfile(path+sto_file) :
        os.remove(path+sto_file)


    # import data from excel file
    for name, col_range in segments.items():
        data = pd.read_excel(path+filename, sheet_name, usecols=col_range, header=0)
        print(f"...importing {name} data")

        quaternions = data.to_numpy()[:, [1, 2, 3, 0]]
        r_all = R.from_quat(quaternions)
        Q[name] = r_all

    # Calculate time based on length and sampling frequency
    sampling_rate = freq
    num_samples = len(list(Q.values())[0])
    time = np.arange(num_samples) / sampling_rate

    # build data structure for .sto file
    for name in Q:
        q_array = Q[name].as_quat()  # returns (n, 4): [x, y, z, w]
        q_array = q_array[:, [3, 0, 1, 2]]  # reorder to w, x, y, z
        data_quat[f"{name}_imu"] = [','.join(f"{v:.8f}" for v in row) for row in q_array]


    # write calibration file (first frame)
    with open(path+sto_file_cal, 'w') as f:
        f.write("DataRate=120\n")
        f.write("DataType=Quaternion\n")
        f.write("version=3\n")
        f.write("OpenSimVersion=4.5\n")
        f.write("endheader\n")
        f.write("time\t" + '\t'.join(data_quat.keys()) + '\n')

        line = f"{time[0]:.5f}\t" + '\t'.join(data_quat[seg][0] for seg in data_quat)
        f.write(line + '\n')


    # write inverse kinematics file (all the data)
    with open(path+sto_file, 'w') as f:
        f.write("DataRate=120\n")
        f.write("DataType=Quaternion\n")
        f.write("version=3\n")
        f.write("OpenSimVersion=4.5\n")
        f.write("endheader\n")
        f.write("time\t" + '\t'.join(data_quat.keys()) + '\n')

        for i in range(len(time)):
            line = f"{time[i]:.5f}\t" + '\t'.join(data_quat[seg][i] for seg in data_quat)
            f.write(line + '\n')


if __name__ == "__main__":

    create_sto(
        freq = 120,
        path = "/Users/joshualowery/Desktop/test_data/",
        segments = {
        'tibia_r': 'A:D',
        'calcn_r': 'E:H',
        'forefoot_r': 'I:L',
        'digits_r': 'M:P',
    }
    )

