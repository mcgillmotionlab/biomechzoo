import os
import shutil
from utils.engine import engine  # assumes this returns .zoo files in folder
from processing.zload import zload
from processing.zsave import zsave
from conversion.c3d2zoo import c3d2zoo


class BiomechZoo:
    def __init__(self, folder, backup_root='backups', verbose=False):
        self.folder = folder
        self.backup_root = backup_root
        self.verbose = verbose
        self.history = []

    def _log(self, message):
        if self.verbose:
            print('{}' .format(message))

    def _backup(self, step_name, files):
        self._log('Backing up files before step \'{}\'...'.format(step_name))
        backup_folder = os.path.join(self.backup_root, step_name)
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
        for fl in files:
            fname = os.path.basename(fl)
            backup_path = os.path.join(backup_folder, fname)
            shutil.copy2(fl, backup_path)
        self._log('Backup complete: {} files copied to {}'.format(len(files), backup_folder))

    def convert_c3d2zoo(self, output_folder=None):
        if self.verbose:
            print('Starting c3d2zoo conversion in folder: {}'.format(self.folder))
        saved_files = c3d2zoo(self.folder, output_folder, verbose=self.verbose)
        self.history.append('c3d2zoo_conversion')
        if self.verbose:
            print('Conversion complete: {} files converted'.format(len(saved_files)))
        return saved_files

    def normalize(self, num_frames=101):
        self._log('Starting normalization...')
        files = engine(self.folder)  # get list of .zoo files
        if not files:
            self._log('No zoo files found to normalize.')
            return
        self._backup('normalize', files)
        for fl in files:
            data = zload(fl)
            # Normalize each channel to num_frames (implement your normalize_line function)
            for ch in data:
                if ch == 'zoosystem':
                    continue
                arr = data[ch]
                # simple example: resample or interpolate to num_frames
                data[ch] = self._normalize_line(arr, num_frames)
            zsave(fl, data)
        self.history.append('normalize')
        self._log('Normalization complete.')

    def _normalize_line(self, data, num_frames):
        import numpy as np
        from scipy.interpolate import interp1d

        original_len = len(data)
        if original_len == num_frames:
            return data  # no change needed

        x_original = np.linspace(0, 1, original_len)
        x_new = np.linspace(0, 1, num_frames)
        f = interp1d(x_original, data, kind='linear', axis=0)
        return f(x_new)

    def remove_channels(self, channels, mode='remove'):
        '''
        channels: list of channel names to remove or keep
        mode: 'remove' (default) to remove listed channels,
              'keep' to keep only the listed channels
        '''
        self._log('Starting remove_channels...')
        files = engine(self.folder)
        if not files:
            self._log('No zoo files found to remove channels from.')
            return
        self._backup('remove_channels', files)
        for fl in files:
            data = zload(fl)
            data_new = {'zoosystem': data['zoosystem']}
            keys = [k for k in data if k != 'zoosystem']
            if mode == 'remove':
                for ch in keys:
                    if ch not in channels:
                        data_new[ch] = data[ch]
                    else:
                        self._log('Removing channel \'{}\' from file {}'.format(ch, fl))
            elif mode == 'keep':
                for ch in keys:
                    if ch in channels:
                        data_new[ch] = data[ch]
                    else:
                        self._log('Removing channel \'{}\' from file {}'.format(ch, fl))
            else:
                raise ValueError('mode must be \'remove\' or \'keep\'')
            zsave(fl, data_new)
        self.history.append('remove_channels_{}'.format(mode))
        self._log('Channel removal complete.')
