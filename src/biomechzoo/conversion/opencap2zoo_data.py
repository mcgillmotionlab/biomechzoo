import os
from typing import NoReturn

import pandas as pd

#todo: review. do not use in current form


def opencap2zoo_data(ik_file: str) -> NoReturn:
    """
    Convert OpenCap inverse-kinematics output to zoo format.

    Not implemented. Reserved for future OpenCap support; do not use
    in its current form.

    Parameters
    ----------
    ik_file : str
        Path to an OpenSim ``.mot`` inverse-kinematics file.

    Raises
    ------
    NotImplementedError
        Always.
    """
    raise NotImplementedError
    ik_data = pd.read_csv(ik_file, sep='\t', comment='#')  # OpenSim .mot format
    a = 1


def _compute_opencap_quantities() -> None:
    """
    Placeholder for future OpenCap quantity computations.

    Not implemented; currently a no-op stub.
    """
    b = 2


if __name__ == '__main__':
    """ for unit testing"""
    # -------TESTING--------
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)

    fl = os.path.join(project_root, 'data', 'OpenCap', 'gait_3', 'OpenSimData', 'Kinematics', 'gait_3.mot')

    data = opencap2zoo_data(fl)