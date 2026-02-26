import os
from pathlib import Path
import glob
import re
import copy

from biomechzoo.utils.engine import engine
from biomechzoo.utils.zload import zload
from biomechzoo.utils.fileparts import fileparts
from biomechzoo.processing.addchannel_data import addchannel_data
from biomechzoo.processing.renamechannel_data import renamechannel_data
from biomechzoo.utils.zsave import zsave


def combine_files_within(fld:str, suffix_map:list[str], name_contains:str | list[str], subfolders:str | list[str],
                         inplace:bool, out_folder:str):
    """
    Combines zoo-files within a subfolder into a single file

    This function operates on a root folder and automatically finds all the subdirectories. All channels withing the
    files within the folders will be combined into a single zoo-file.

    Parameters
    ----------
    fld : str
        Path to the root folder containing all zoo-files
    suffix_map : list[str]
        List of names containing suffixes for channels --> must be matched to the file names
    name_contains : str or list of str
        Name of list of names that should be within the filepath
    subfolders : str of list of str
            Folder of list of folders that should be within the filepath
    inplace : bool
    out_folder : str

    Returns
    -------
    None

    Notes
    -----
    Automatically saves the combined file to the out-folder.

    """
    # Get all base directories.
    all_files = engine(fld, extension="zoo", name_contains=name_contains, subfolders=subfolders)
    dirs = set()
    for f in all_files:
        dir_path = os.path.dirname(f)
        dirs.add(dir_path)


    for d in dirs:
        fl = engine(d, extension="zoo")
        data1 = zload(fl[0])

        data_new = copy.deepcopy(data1)

        #Rename channels with the suffix of the first file.
        directory, filename, extension = fileparts(fl[0])

        # find the suffix based on filename and rename the channel names
        s = [s for s in suffix_map if s in filename]
        suffix = ' '.join(s)
        ch_names = list(data_new.keys())
        ch_names.remove("zoosystem")
        new_ch_names = [f"{ch}_{suffix}" for ch in ch_names if ch != "zoosystem"]

        data_new = renamechannel_data(data_new, ch_names, new_ch_names)

        # add all the data from the other files to data_new
        sections = ["Video", "Analog"]
        for f in fl[1:]:
            _, filename, _ = fileparts(f)

            # find the suffix based on filename
            s = [s for s in suffix_map if s in filename]
            suffix = ' '.join(s)

            data2 = zload(f)
            for section in sections:
                channels = data2["zoosystem"][section]["Channels"]
                for ch in channels:
                    line_data = data2[ch]["line"]
                    event_data = data2[ch]["event"]

                    data_new = addchannel_data(data=data_new, ch_new_name= f"{ch}_{suffix}", ch_new_data=line_data, section=section)
                    data_new[f"{ch}_{suffix}"]["event"] = event_data

        zsave(fl[0], data_new, inplace=inplace, out_folder=out_folder, root_folder=fld)


def combine_files_between():
    NotImplementedError()