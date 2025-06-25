import os
import shutil


def copy_files(fld, new_fld):
    """
    Copy all files from `fld` (including subfolders) to `new_fld`,
    preserving folder structure.

    Parameters:
        fld (str): Source folder
        new_fld (str): Destination folder
    """
    for root, _, files in os.walk(fld):
        for file in files:
            src_path = os.path.join(root, file)
            rel_path = os.path.relpath(src_path, fld)
            dst_path = os.path.join(new_fld, rel_path)

            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            shutil.copy2(src_path, dst_path)
