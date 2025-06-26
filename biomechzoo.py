import os
from ezc3d import c3d
from utils.engine import engine  # assumes this returns .zoo files in folder
from utils.zload import zload
from utils.zsave import zsave
from processing.removechannel_data import removechannel_data
from conversion.c3d2zoo_data import c3d2zoo_data


class BiomechZoo:
    def __init__(self, folder, verbose=False):
        self.folder = folder
        self.verbose = verbose

        if self.verbose:
            print('BiomechZoo initialized')
            print('processing folder set to: {}'.format(self.folder))

    def c3d2zoo(self):
        """ Converts all .c3d files in the folder to .zoo format """

        fl = engine(self.folder, extension='.c3d')
        for f in fl:
            if self.verbose:
                print('converting c3d to zoo for {}'.format(f))
            c3d_obj = c3d(f)
            data = c3d2zoo_data(c3d_obj)
            f_zoo = f.replace('.c3d', '.zoo')
            zsave(f_zoo, data)

    def removechannel(self, ch, mode='remove'):
        """ removes channels from zoo files """

        fl = engine(self.folder)
        for f in fl:
            if self.verbose:
                print('removing channels for {}'.format(f))
            data = zload(f)
            data = removechannel_data(data, ch, mode)
            zsave(f, data)