import os
import re
import copy
import warnings

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


def combine_files_between(in_folder:str, fld1:str, fld2:str, suffix:str,  name_contains:str | list[str], subfolders:str | list[str],
                          method:str="down",inplace:bool=False,
                          fl1exclude:list=None, fl2exclude:list=None,
                          out_folder:str=None, strmatch:str=None,):

    """
    Combines 2 zoo-files in different subfolders into a single file.

    This function operates on 2 folders that have the same root and automatically finds all the subdirectories.
    The function find the files to combine by matching the filename. Possible use case is combining data collected with
    different motion capture devices, e.g. IMUs and Vicon, Vicon and Force plates.

    Parameters
    ----------
    in_folder : str
        Path to the root folder containing all zoo-files
    fld1 : str
        Path to the subfolder th be merged
    fld2 : str
        Path to the subfolder to be merged
    suffix : str
        Name containing suffix for the channels
    name_contains : str or list of str
        Name of list of names that should be within the filepath
    subfolders : str of list of str
            Folder of list of folders that should be within the filepath
    method: str
        determines if you want to upsample the signal with the lower frequency ("up"), if you want to downsample
        the signal with the  highest frequency ('down'), or leave them the same 'none'. Default is down if frequencies are different.
    inplace: bool
    fl1exclude: str or list of str
        files names to ignore from fld1. Default is None.
    fl2exclude: str or list of str
        filenames to ignore from fld2. Default is None.
    strmatch: str
        The regular expression to find the common subject folder.
    out_folder : str

    Returns
    -------
    None

    Notes
    -----
    Automatically saves the combined file to the out-folder using the subdirectories of the first folder path.
    Filenames MUST have the exact same name.

    Currently files need to have the same file name in order to combine successfully e.g.

    #TODO: Allow to work without strmatch
    #TODO: find the files to exclude for fl1 and fl2
    #TODO: Find the files that are shared between the two folders.
    #TODO: REWORK COMBINE TO INCLUDE RESAMPLING METHODS AND TO USE THE SELF INPUT
    """


    fl1 = engine(fld1, extension="zoo", name_contains=name_contains, subfolders=subfolders)
    fl2= engine(fld2, extension="zoo", name_contains=name_contains, subfolders=subfolders)

    # set up framework for the first folder
    fname1 = []
    dict1 = {}
    for f in fl1:
        match = re.search(strmatch, f)
        if match:
            if match[0] not in dict1.keys():
                dict1.update({match[0]: {}})

        directory, filename, extension = fileparts(f)
        fname1.append(filename + extension)
        dict1[match[0]].update({filename + extension: f})

    # set up the framework for the second folder
    fname2 = []
    dict2 = {}
    for f in fl2:
        match = re.search(strmatch, f)
        if match:
            if match[0] not in dict2.keys():
                dict2.update({match[0]: {}})

        directory, filename, extension = fileparts(f)
        fname2.append(filename + extension)

        dict2[match[0]].update({filename + extension: f})

    # Find the match between framework 1 and framework 2 on the first (participant?) level
    lvl1 = [s for s in dict1.keys() if s in dict2.keys()]

    for key in lvl1:
        # Find common file names.
        lvl2 = [f for f in dict1[key].keys() if f in dict2[key].keys()]

        for l2 in lvl2:
            # load data
            f1 = dict1[key][l2]
            data1 = zload(f1)

            f2 = dict2[key][l2]
            data2 = zload(f2)

            # combining the data
            data_new = copy.deepcopy(data1)
            sections = ["Video", "Analog"]

            # Add all the video an analog files from data2
            for section in sections:
                ch2 = data2["zoosystem"][section]["Channels"]
                freq1 = data1["zoosystem"][section]["Freq"]
                freq2 = data2["zoosystem"][section]["Freq"]

                if freq1 != freq2:
                    warnings.warn("Frequencies do not match")
                    # TODO: implement resample

                if ch2:
                    for ch in ch2:
                        line_data = data2[ch]["line"]
                        event_data = data2[ch]["event"]

                        data_new = addchannel_data(data=data_new, ch_new_name=f"{ch}_{suffix}", ch_new_data=line_data)
                        data_new[f"{ch}_{suffix}"]["event"] = event_data

            zsave(f1, data_new, inplace=inplace, out_folder=out_folder, root_folder=in_folder)


if __name__ == '__main__':
    from biomechzoo.biomechzoo import BiomechZoo
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    data_dir = os.path.join(project_root, 'data', 'sample_study')

    # test combine_files_between
    # create copy of normalized where channel names are changed
    bmech = BiomechZoo(os.path.join(data_dir, 'normalized'))
    ch_old = ['LeftAnklePower', 'LeftKneePower', 'LeftHipPower']
    ch_new = ['LAnklePower', 'LKPower', 'LHipPower']
    bmech.renamechannnel(ch=ch_old, ch_new=ch_new, out_folder='normalized_rename')
    bmech.removechannel(ch=ch_new, mode='keep', out_folder='normalized_rename_remove')

    bmech.combine_files(within=False,
                        fld1=os.path.join(data_dir, 'normalized_rename_remove'),
                        fld2=os.path.join(data_dir, 'normalized'),
                        strmatch=r"HC\w+",
                        )
