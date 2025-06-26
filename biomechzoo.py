import os
from ezc3d import c3d
from utils.engine import engine  # assumes this returns .zoo files in folder
from utils.zload import zload
from utils.zsave import zsave
from processing.removechannel_data import removechannel_data
from processing.explodechannel_data import explodechannel_data
from processing.normalize_data import normalize_data
from conversion.c3d2zoo_data import c3d2zoo_data


class BiomechZoo:
    def __init__(self, in_folder, inplace=False, verbose=False):
        self.in_folder = in_folder
        self.verbose = verbose
        self.inplace = inplace  # choice to save processed files to new folder

        if self.verbose:
            print('BiomechZoo initialized')
            print('processing folder set to: {}'.format(self.in_folder))
            if inplace:
                print('each processing step will be applied to same folder (no backups per step)')
            else:
                print('each processing step will be applied to a new folder')

    def _update_folder(self, out_folder, inplace, in_folder):
        """
        Utility to update self.folder if not inplace.

        Parameters:
        - out_folder (str or None): The output folder provided by user
        - inplace (bool): Whether processing is inplace
        - in_folder (str): The current input folder
        """
        if not inplace:
            # get full path for out_folder
            in_folder_path = os.path.dirname(in_folder)
            self.in_folder = os.path.join(in_folder_path, out_folder)

    def c3d2zoo(self, out_folder=None, inplace=None):
        """ Converts all .c3d files in the folder to .zoo format """
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace

        fl = engine(in_folder, extension='.c3d')
        for f in fl:
            if verbose:
                print('converting c3d to zoo for {}'.format(f))
            c3d_obj = c3d(f)
            data = c3d2zoo_data(c3d_obj)
            f_zoo = f.replace('.c3d', '.zoo')
            zsave(f_zoo, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)

        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def removechannel(self, ch, mode='remove', out_folder=None, inplace=None):
        """ removes channels from zoo files """
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace

        fl = engine(in_folder)
        for f in fl:
            if verbose:
                print('removing channels for {}'.format(f))
            data = zload(f)
            data = removechannel_data(data, ch, mode)
            zsave(f, data, inplace=inplace, root_folder=in_folder, out_folder=out_folder)

        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def explodechannel(self, out_folder=None, inplace=None):
        """ explodes all channels in a zoo file """
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace

        fl = engine(in_folder)
        for f in fl:
            if verbose:
                print('removing channels for {}'.format(f))
            data = zload(f)
            data = explodechannel_data(data)
            zsave(f, data, inplace=inplace, root_folder=in_folder, out_folder=out_folder)

        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def normalize(self, nlen=101, out_folder=None, inplace=None):
        """ time normalizes all channels to length nlen """
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace

        fl = engine(in_folder)
        for f in fl:
            if verbose:
                print('normalizing channels to length {} for {}'.format(nlen, f))
            data = zload(f)
            data = normalize_data(data, nlen)
            zsave(f, data, inplace=inplace, root_folder=in_folder, out_folder=out_folder)

        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)
