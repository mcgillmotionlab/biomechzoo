import os
import inspect
import time

from biomechzoo.imu.tilt_algorithm import tilt_algorithm_data
from biomechzoo.utils.engine import engine  # assumes this returns .zoo files in folder
from biomechzoo.utils.zload import zload
from biomechzoo.utils.zsave import zsave
from biomechzoo.utils.batchdisp import batchdisp
from biomechzoo.utils.get_split_events import get_split_events
from biomechzoo.processing.split_trial_data import split_trial_data
from biomechzoo.conversion.c3d2zoo_data import c3d2zoo_data
from biomechzoo.conversion.table2zoo_data import table2zoo_data
from biomechzoo.conversion.mvnx2zoo_data import mvnx2zoo_data
from biomechzoo.processing.removechannel_data import removechannel_data
from biomechzoo.processing.renamechannel_data import renamechannel_data
from biomechzoo.processing.removeevent_data import removeevent_data
from biomechzoo.processing.explodechannel_data import explodechannel_data
from biomechzoo.processing.addevent_data import addevent_data
from biomechzoo.processing.partition_data import partition_data
from biomechzoo.processing.renameevent_data import renameevent_data
from biomechzoo.biomech_ops.normalize_data import normalize_data
from biomechzoo.biomech_ops.phase_angle_data import phase_angle_data
from biomechzoo.biomech_ops.continuous_relative_phase_data import continuous_relative_phase_data
from biomechzoo.biomech_ops.filter_data import filter_data
from biomechzoo.linear_algebra_ops.compute_magnitude_data import compute_magnitude_data
from biomechzoo.linear_algebra_ops.rectify import rectify_data
class BiomechZoo:
    def __init__(self, in_folder, inplace=False, subfolders=None, name_contains=None, verbose=0):
        self.verbose = verbose
        self.in_folder = in_folder
        self.verbose = verbose
        self.inplace = inplace               # choice to save processed files to new folder
        self.subfolders = subfolders         # only run processes on list in subfolder
        self.name_contains = name_contains   # only run processes on files with name_contains in file name

        batchdisp('BiomechZoo initialized', level=1, verbose=verbose)
        batchdisp('verbosity set to: {}'.format(verbose), level=1, verbose=verbose)
        batchdisp('root processing folder set to: {}'.format(self.in_folder), level=1, verbose=verbose)
        if name_contains is not None:
            batchdisp('only include files containing name_contains string: {}'.format(self.name_contains), level=1, verbose=verbose)
        if subfolders is not None:
            if type(subfolders) is list:
                batchdisp('only process files in subfolder(s):', level=1, verbose=verbose)
                for subfolder in self.subfolders:
                    batchdisp('{}'.format(os.path.join(self.in_folder, subfolder)), level=1, verbose=verbose)
            else:
                batchdisp('only process files in subfolder(s): {}'.format(os.path.join(self.in_folder, self.subfolders)), level=1, verbose=verbose)

        if inplace:
            batchdisp('Processing mode: overwrite (inplace=True) (each step will be applied to same folder)', level=1, verbose=verbose)
        else:
            batchdisp('Processing mode: backup (inplace=False)(each step will be applied to a new folder)', level=1, verbose=verbose)

    def _update_folder(self, out_folder, inplace, in_folder):
        """
        Utility to update self.in_folder if not inplace.

        Parameters:
        - out_folder (str or None): The output folder provided by user
        - inplace (bool): Whether processing is inplace
        - in_folder (str): The current input folder
        """
        if not inplace:
            # get full path for out_folder
            in_folder_path = os.path.dirname(in_folder)
            self.in_folder = os.path.join(in_folder_path, out_folder)

        batchdisp('all files saved to: {}'.format(self.in_folder ), level=1, verbose=self.verbose)

    def mvnx2zoo(self, out_folder=None, inplace=False):
        """ Converts all .mvnx files in the folder to .zoo format """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.mvnx', name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            batchdisp('converting mvnx to zoo for {}'.format(f), level=2, verbose=verbose)
            data = mvnx2zoo_data(f)
            f_zoo = f.replace('.mvnx', '.zoo')
            zsave(f_zoo, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)
        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def c3d2zoo(self, out_folder=None, inplace=None):
        """ Converts all .c3d files in the folder to .zoo format """
        start_time = time.time()
        from ezc3d import c3d
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.c3d', name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            batchdisp('converting c3d to zoo for {}'.format(f), level=2, verbose=verbose)
            c3d_obj = c3d(f)
            data = c3d2zoo_data(c3d_obj)
            f_zoo = f.replace('.c3d', '.zoo')
            zsave(f_zoo, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)
        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def table2zoo(self, extension, out_folder=None, inplace=None, skip_rows=0, freq=None):
        """ Converts generic .csv file in the folder to .zoo format """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder

        if not extension.startswith('.'):
            extension = '.' + extension

        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension=extension, name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            batchdisp('converting {} to zoo for {}'.format(extension, f), level=2, verbose=verbose)
            data = table2zoo_data(f, extension=extension, skip_rows=skip_rows, freq=freq)
            f_zoo = f.replace(extension, '.zoo')
            zsave(f_zoo, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)
        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def xls2zoo(self, out_folder=None, inplace=None):
        raise NotImplementedError('Use table2zoo instead')

    def csv2zoo(self, out_folder=None, inplace=None):
        raise NotImplementedError('Use table2zoo instead')

    def parquet2zoo(self, out_folder=None, inplace=None):
        raise NotImplementedError('Use table2zoo instead')


    def tilt_algorithm(self, chname_avert, chname_medlat, chname_antpost, out_folder=None, inplace=False):
        """ tilt correction for acceleration data """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            batchdisp('tilt correction of acceleration channels for {}'.format(f), level=2, verbose=verbose)
            data = zload(f)
            data = tilt_algorithm_data(data, chname_avert, chname_medlat, chname_antpost)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp(
            '{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time),
            level=1, verbose=verbose)
        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def compute_magnitude(self, chname1, chname2, chname3, out_folder=None, inplace=False):
        """ compute euclidean magnitude  """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            batchdisp('compute magnitude from channels {}, {}, {} for {}'.format(chname1, chname2, chname3, f), level=2, verbose=verbose)
            data = zload(f)
            data = compute_magnitude_data(data, chname1, chname2, chname3)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp(
            '{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time),
            level=1, verbose=verbose)
        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def rectify(self, chs, out_folder=None, inplace=False):
        """ rectify a signal to absolute value  """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            batchdisp('rectifying signal for channels {} for {}'.format(chs, f), level=2, verbose=verbose)
            data = zload(f)
            data = rectify_data(data, chs)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp(
            '{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time),
            level=1, verbose=verbose)
        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)
    def phase_angle(self, ch, out_folder=None, inplace=None):
        """ computes phase angles"""
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            if verbose:
                batchdisp('computing phase angles for {}'.format(f), level=2, verbose=verbose)
            data = zload(f)
            data = phase_angle_data(data, ch)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)

        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def continuous_relative_phase(self, ch_prox, ch_dist, out_folder=None, inplace=None):
        """ computes CRP angles"""
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            if verbose:
                batchdisp('computing CRP angles between channel {} (prox) and {} (dist) for {}'.format(ch_prox, ch_dist, f), level=2, verbose=verbose)
            data = zload(f)
            data = continuous_relative_phase_data(data, ch_dist, ch_prox)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)

        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def split_trial_by_gait_cycle(self, first_event_name, out_folder=None, inplace=None):
        """ split by gait cycle according to event_name"""
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            f_name = os.path.splitext(os.path.basename(f))[0]
            data = zload(f)
            split_events = get_split_events(data, first_event_name)
            if split_events is None:
                print('no event {} found, saving original file'.format(first_event_name))
                zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
            else:
                for i, _ in enumerate(split_events[0:-1]):
                    fl_new = f.replace(f_name, f_name + '_' + str(i + 1))
                    start = split_events[i]
                    end = split_events[i + 1]
                    batchdisp('splitting by gait cycle from {} to {} for {}'.format(start, end, f), level=2,
                              verbose=verbose)
                    data_new = split_trial_data(data, start, end)
                    if data_new is not None:
                        zsave(fl_new, data_new, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)

        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)


    # def mean_absolute_relative_phase_deviation_phase(self, channels, out_folder=None, inplace=None):
    #     verbose = self.verbose
    #     in_folder = self.in_folder
    #     if inplace is None:
    #         inplace = self.inplace
    #
    #     fl = engine(in_folder)
    #     for f in fl:
    #         for channel in channels:
    #             batchdisp('collecting trials for marp and dp for {}'.format(f), level=2, verbose=verbose)
    #             data = zload(f)
    #             data = removechannel_data(data, ch, mode)
    #             zsave(f, data, inplace=inplace, root_folder=in_folder, out_folder=out_folder)
    #             batchdisp('remove channel complete', level=1, verbose=verbose)
    #
    #     # Update self.folder after  processing
    #     self._update_folder(out_folder, inplace, in_folder)
    def renameevent(self, evt, nevt, out_folder=None, inplace=None):
        """ renames event evt to nevt in all zoo files """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            batchdisp('renaming events from {} to {} for {}'.format(evt, nevt ,f), level=2, verbose=verbose)
            data = zload(f)
            data = renameevent_data(data, evt, nevt)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)

        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def renamechannnel(self, ch, ch_new, out_folder=None, inplace=None):
        """ renames channels from ch to ch_new in all zoo files """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            batchdisp('renaming channels from {} to {} for {}'.format(ch, ch_new ,f), level=2, verbose=verbose)
            data = zload(f)
            data = renamechannel_data(data, ch, ch_new)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)

        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def removechannel(self, ch, mode='remove', out_folder=None, inplace=None):
        """ removes channels from zoo files """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            batchdisp('removing channels for {}'.format(f), level=2, verbose=verbose)
            data = zload(f)
            data = removechannel_data(data, ch, mode)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)

        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)


    def removeevent(self, events, mode='remove', out_folder=None, inplace=None):
        """ removes channels from zoo files """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            batchdisp('removing events {} for {}'.format(events, f), level=2, verbose=verbose)
            data = zload(f)
            data = removeevent_data(data, events, mode)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)

        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)


    def explodechannel(self, out_folder=None, inplace=None):
        """ explodes all channels in a zoo file """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            if verbose:
                batchdisp('removing channels for {}'.format(f), level=2, verbose=verbose)
            data = zload(f)
            data = explodechannel_data(data)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)

        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def normalize(self, nlen=101, out_folder=None, inplace=None):
        """ time normalizes all channels to length nlen """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            if verbose:
                batchdisp('normalizing channels to length {} for {}'.format(nlen, f), level=2, verbose=verbose)
            data = zload(f)
            data = normalize_data(data, nlen)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)

        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def addevent(self, ch, event_type, event_name, out_folder=None, inplace=None, constant=None):
        """ adds events of type evt_type with name evt_name to channel ch """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            if verbose:
                batchdisp('adding event {} to channel {} for {}'.format(event_type, ch, f), level=2, verbose=verbose)
            data = zload(f)
            data = addevent_data(data, ch, event_type, event_name, constant)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)

        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def partition(self, evt_start, evt_end, out_folder=None, inplace=None):
        """ partitions data between events evt_start and evt_end """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            if verbose:
                batchdisp('partitioning data between events {} and {} for {}'.format(evt_start, evt_end, f), level=2, verbose=verbose)
            data = zload(f)
            data = partition_data(data, evt_start, evt_end)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)
        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def filter(self, ch, filt=None, out_folder=None, inplace=None):
        """ filter data"""
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            if verbose:
                batchdisp('filtering data for channel {} in {}'.format(ch, f), level=2, verbose=verbose)
            data = zload(f)
            data = filter_data(data, ch, filt)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time),
            level=1, verbose=verbose)
        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

