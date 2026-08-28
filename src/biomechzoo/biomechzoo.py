import inspect
import os
import time
from typing import Dict, List, Optional, Union

from biomechzoo.imu.tilt_algorithm import tilt_algorithm_data
from biomechzoo.linear_algebra_ops.kinematics import (quats2euler_data, dcms2euler_data, marker2dcm_data, quats2dcm_data,
                                                      rotate_dcm_data)
from biomechzoo.biomech_ops.resample import resample_data
from biomechzoo.utils.engine import engine  # assumes this returns .zoo files in folder
from biomechzoo.utils.zload import zload
from biomechzoo.utils.zsave import zsave
from biomechzoo.utils.batchdisp import batchdisp
from biomechzoo.utils.get_split_events import get_split_events
from biomechzoo.processing.split_trial_data import split_trial_data
from biomechzoo.conversion.c3d2zoo_data import c3d2zoo_data
from biomechzoo.conversion.table2zoo_data import table2zoo_data
from biomechzoo.conversion.mvnx2zoo_data import mvnx2zoo_data
from biomechzoo.processing.combine_files_data import combine_files_within, combine_files_between
from biomechzoo.processing.removechannel_data import removechannel_data
from biomechzoo.processing.renamechannel_data import renamechannel_data
from biomechzoo.processing.removeevent_data import removeevent_data
from biomechzoo.processing.explodechannel_data import explodechannel_data
from biomechzoo.processing.addevent_data import addevent_data
from biomechzoo.processing.sync_channels_data import sync_channels_data
from biomechzoo.processing.partition_data import partition_data
from biomechzoo.processing.renameevent_data import renameevent_data
from biomechzoo.biomech_ops.normalize_data import normalize_data
from biomechzoo.biomech_ops.phase_angle_data import phase_angle_data
from biomechzoo.biomech_ops.continuous_relative_phase_data import continuous_relative_phase_data
from biomechzoo.biomech_ops.filter_data import filter_data
from biomechzoo.linear_algebra_ops.compute_magnitude_data import compute_magnitude_data
from biomechzoo.linear_algebra_ops.rectify import rectify_data
from biomechzoo.utils.group_by_terminal_folder import group_by_terminal_folder
from biomechzoo.processing.rep_trial_data import reptrial_data

class BiomechZoo:
    """Batch-processing pipeline over a folder of .zoo files."""

    def __init__(
            self, in_folder: str, inplace: bool = False,
            subfolders: Optional[Union[str, List[str]]] = None,
            name_contains: Optional[Union[str, List[str]]] = None,
            name_excludes: Optional[Union[str, List[str]]] = None,
            verbose: Union[int, str] = 0,
    ) -> None:
        """
        Parameters
        ----------
        in_folder : str
            Root folder to process.
        inplace : bool, optional
            If True, each step overwrites files in place. If False,
            each step writes to a new folder. Default is False.
        subfolders : str or list of str, optional
            Restrict processing to these subfolder names.
        name_contains : str or list of str, optional
            Only process files whose name contains this substring.
        name_excludes : str or list of str, optional
            Skip files whose name contains this substring.
        verbose : int or str, optional
            Verbosity level passed to :func:`batchdisp`. Default is 0.
        """
        self.verbose = verbose
        self.in_folder = in_folder
        self.verbose = verbose
        self.inplace = inplace               # choice to save processed files to new folder
        self.subfolders = subfolders         # only run processes on list in subfolder
        self.name_contains = name_contains   # only run processes on files with name_contains in file name
        self.name_excludes = name_excludes   # only run processes on files without name_excludes in file name
        batchdisp('BiomechZoo initialized', level=1, verbose=verbose)
        batchdisp('verbosity set to: {}'.format(verbose), level=1, verbose=verbose)
        batchdisp('root processing folder set to: {}'.format(self.in_folder), level=1, verbose=verbose)
        if name_contains is not None:
            batchdisp('only include files containing name_contains string: {}'.format(self.name_contains), level=1, verbose=verbose)
        if name_excludes is not None:
            batchdisp('excludes files containing name_excludes string: {}'.format(self.name_excludes), level=1,
                      verbose=verbose)
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

    def _update_folder(
            self, out_folder: Optional[str], inplace: bool, in_folder: str,
    ) -> None:
        """
        Update ``self.in_folder`` to the new output folder if not inplace.

        Parameters
        ----------
        out_folder : str or None
            The output folder provided by the user.
        inplace : bool
            Whether processing is inplace.
        in_folder : str
            The current input folder.
        """
        if not inplace:
            # get full path for out_folder
            in_folder_path = os.path.dirname(in_folder)
            self.in_folder = os.path.join(in_folder_path, out_folder)

        batchdisp('all files saved to: {}'.format(self.in_folder ), level=1, verbose=self.verbose)

    def remove_files(
            self, fl_remove: List[str], out_folder: Optional[str] = None,
            inplace: Optional[bool] = None,
    ) -> None:
        """
        Remove files listed in ``fl_remove`` from ``self.in_folder``.

        Files not in ``fl_remove`` are saved using :func:`zsave`.

        Parameters
        ----------
        fl_remove : list of str
            Substrings identifying files to remove (a file is removed
            if any entry is found in its path).
        out_folder : str, optional
            Output folder for files that are kept.
        inplace : bool, optional
            If True, overwrite in place. Defaults to ``self.inplace``.
        """

        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder

        inplace = self.inplace if inplace is None else inplace

        # Get all files using engine (BiomechZoo pattern)
        fl = engine(in_folder, name_contains=self.name_contains, name_excludes=self.name_excludes,
                    subfolders=self.subfolders)
        removed = 0
        for f in fl:
            if any(rem in f for rem in fl_remove):
                removed += 1
                batchdisp('not copying {} to new folder {}'.format(f, out_folder), level=2, verbose=verbose)
                continue

            # Save only good files
            data = zload(f)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)

        method_name = inspect.currentframe().f_code.co_name
        t = time.time() - start_time
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, removed, t), level=1,
                  verbose=verbose)
        self._update_folder(out_folder, inplace, in_folder)


    def mvnx2zoo(
            self, out_folder: Optional[str] = None, inplace: bool = False,
    ) -> None:
        """
        Convert all .mvnx files in the folder to .zoo format.

        Parameters
        ----------
        out_folder : str, optional
            Output folder for converted files.
        inplace : bool, optional
            If True, overwrite in place. Default is False.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.mvnx', name_contains=self.name_contains, name_excludes=self.name_excludes,
                    subfolders=self.subfolders)
        for f in fl:
            batchdisp('converting mvnx to zoo for {}'.format(f), level=2, verbose=verbose)
            data = mvnx2zoo_data(f)
            f_zoo = f.replace('.mvnx', '.zoo')
            zsave(f_zoo, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)
        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def c3d2zoo(
            self, out_folder: Optional[str] = None,
            inplace: Optional[bool] = None,
    ) -> None:
        """
        Convert all .c3d files in the folder to .zoo format.

        Parameters
        ----------
        out_folder : str, optional
            Output folder for converted files.
        inplace : bool, optional
            If True, overwrite in place. Defaults to ``self.inplace``.
        """
        start_time = time.time()
        from ezc3d import c3d
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.c3d', name_contains=self.name_contains, name_excludes=self.name_excludes,
                    subfolders=self.subfolders)
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

    def table2zoo(
            self, extension: str, out_folder: Optional[str] = None,
            inplace: Optional[bool] = None, skip_rows: int = 0,
            freq: Optional[int] = None, sep: str = ",",
    ) -> None:
        """
        Convert generic table files (CSV/Parquet) in the folder to .zoo format.

        Parameters
        ----------
        extension : str
            File extension to convert (e.g. 'csv', 'parquet').
        out_folder : str, optional
            Output folder for converted files.
        inplace : bool, optional
            If True, overwrite in place. Defaults to ``self.inplace``.
        skip_rows : int, optional
            Number of header rows to skip. Default is 0.
        freq : int, optional
            Sampling frequency in Hz. If None, inferred from a time column.
        sep : str, optional
            Column separator. Default is ','.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder

        if not extension.startswith('.'):
            extension = '.' + extension

        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension=extension, name_contains=self.name_contains, name_excludes=self.name_excludes,
                    subfolders=self.subfolders)
        for f in fl:
            batchdisp('converting {} to zoo for {}'.format(extension, f), level=2, verbose=verbose)
            data = table2zoo_data(f, extension=extension, skip_rows=skip_rows, freq=freq, sep=sep)
            f_zoo = f.replace(extension, '.zoo')
            zsave(f_zoo, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)
        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def xls2zoo(
            self, out_folder: Optional[str] = None,
            inplace: Optional[bool] = None,
    ) -> None:
        """Deprecated. Raises NotImplementedError; use :meth:`table2zoo`."""
        raise NotImplementedError('Use table2zoo instead')

    def csv2zoo(
            self, out_folder: Optional[str] = None,
            inplace: Optional[bool] = None,
    ) -> None:
        """Deprecated. Raises NotImplementedError; use :meth:`table2zoo`."""
        raise NotImplementedError('Use table2zoo instead')

    def parquet2zoo(
            self, out_folder: Optional[str] = None,
            inplace: Optional[bool] = None,
    ) -> None:
        """Deprecated. Raises NotImplementedError; use :meth:`table2zoo`."""
        raise NotImplementedError('Use table2zoo instead')

    def combine_files(
            self, within: bool = True, suffix: Optional[str] = None,
            out_folder: Optional[str] = None, inplace: Optional[bool] = None,
            fld1: Optional[str] = None, fld2: Optional[str] = None,
            method: Optional[str] = None,
            fl1exlude: Optional[List[str]] = None,
            fl2exclude: Optional[List[str]] = None,
            strmatch: Optional[str] = None,
    ) -> None:
        """
        Merge multiple .zoo files into 1 zoo-file.

        Parameters
        ----------
        within : bool, optional
            If True, combine files within ``self.in_folder`` (see
            :func:`combine_files_within`). If False, combine files
            between ``fld1`` and ``fld2`` (see
            :func:`combine_files_between`). Default is True.
        suffix : str, optional
            Suffix map / channel suffix used to combine channels.
        out_folder : str, optional
            Output folder. Defaults to ``fld2`` when not combining within.
        inplace : bool, optional
            If True, overwrite in place. Defaults to ``self.inplace``.
        fld1 : str, optional
            First folder to combine, when ``within=False``.
        fld2 : str, optional
            Second folder to combine, when ``within=False``.
        method : str, optional
            Resampling method when combining between folders of
            different frequencies.
        fl1exlude : list of str, optional
            Filenames to ignore from ``fld1``.
        fl2exclude : list of str, optional
            Filenames to ignore from ``fld2``.
        strmatch : str, optional
            Regular expression to find the common subject folder.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace

        if out_folder is None:
            out_folder = fld2

        if within:
            combine_files_within(fld=in_folder, suffix_map=suffix, name_contains=self.name_contains, subfolders=self.subfolders, inplace=inplace, out_folder=out_folder,)
        else:
            combine_files_between(in_folder=in_folder, fld1=fld1, fld2=fld2, suffix=suffix,  name_contains=self.name_contains,
                                  subfolders=self.subfolders,
                                  method=method, inplace=inplace,
                                  fl1exclude=fl1exlude, fl2exclude=fl2exclude,
                                  out_folder=out_folder, strmatch=strmatch)

        method_name = inspect.currentframe().f_code.co_name
        batchdisp(
            '{} process complete for in {:.2f} secs'.format(method_name, time.time() - start_time),
            level=1, verbose=verbose)

        self._update_folder(out_folder, inplace, in_folder)

    def tilt_algorithm(
            self, chname_avert: str, chname_medlat: str, chname_antpost: str,
            out_folder: Optional[str] = None, inplace: bool = False,
    ) -> None:
        """
        Apply tilt correction for acceleration data.

        Parameters
        ----------
        chname_avert : str
            Name of the vertical acceleration channel.
        chname_medlat : str
            Name of the mediolateral acceleration channel.
        chname_antpost : str
            Name of the anteroposterior acceleration channel.
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Default is False.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, name_contains=self.name_contains, name_excludes=self.name_excludes,
                    subfolders=self.subfolders)
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

    def rep_trial(
            self, channels: Union[List[str], str] = 'all',
            method: str = 'mean', out_folder: Optional[str] = None,
            inplace: bool = False,
    ) -> None:
        """
        Extract representative trial per subject/condition folder.

        Parameters
        ----------
        channels : list of str or 'all', optional
            Channels used to compute the representative trial. Default is 'all'.
        method : {'mean', 'rmse'}, optional
            Method for computing the representative trial. Default is 'mean'.
        out_folder : str, optional
            Output folder path.
        inplace : bool, optional
            If True, overwrite existing files. Default is False.
        """

        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder

        if inplace is None:
            inplace = self.inplace

        method = method.lower()

        # find all zoo files
        fl = engine(in_folder, name_contains=self.name_contains, name_excludes=self.name_excludes,
                    subfolders=self.subfolders)

        if len(fl) == 0:
            batchdisp('rep_trial: no zoo files found', level=1, verbose=verbose)
            return

        # group files by terminal folder
        groups = group_by_terminal_folder(fl, in_folder)

        for folder, files in groups.items():
            if len(files) == 0:
                batchdisp('{} : no trials found'.format(folder), level=2, verbose=verbose)
                continue

            if len(files) == 1:
                batchdisp('{} : only 1 trial, keeping single trial'.format(folder), level=2, verbose=verbose)
                continue

            batchdisp('{} : building rep trial from {} trials'.format(folder, len(files)),
                      level=2, verbose=verbose)

            # load data
            gdata = {}
            for i, f in enumerate(files):
                gdata['data{}'.format(i + 1)] = zload(f)

            # compute representative trial
            data, file_index = reptrial_data(gdata, channels, method)

            # delete old trials
            for f in files:
                os.remove(f)

            # output filename
            if method == 'mean':
                fout = files[0].replace('.zoo', '_mean.zoo')
            elif method == 'rmse':
                fout = files[file_index]
            else:
                raise ValueError('Method {} not implemented'.format(method))

            batchdisp('saving representative trial {}'.format(fout),
                      level=2, verbose=verbose)

            zsave(fout, data, inplace=inplace,
                  out_folder=out_folder, root_folder=in_folder)

        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete in {:.2f} secs'.format(method_name, time.time() - start_time),
            level=1, verbose=verbose)

        # Update folder after processing
        self._update_folder(out_folder, inplace, in_folder)

    def compute_magnitude(
            self, chname1: Optional[str], chname2: Optional[str],
            chname3: Optional[str], ch_new_name: Optional[str] = None,
            out_folder: Optional[str] = None, inplace: bool = False,
    ) -> None:
        """
        Compute Euclidean magnitude from up to 3 channels as a new channel.

        Parameters
        ----------
        chname1, chname2, chname3 : str or None
            Channel names for the X, Y, Z components. Any may be
            None; at least 2 must be provided.
        ch_new_name : str, optional
            Name of the output magnitude channel. Auto-generated if None.
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Default is False.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, name_contains=self.name_contains, name_excludes=self.name_excludes,
                    subfolders=self.subfolders)
        for f in fl:
            batchdisp('compute magnitude from channels {}, {}, {} for {}'.format(chname1, chname2, chname3, f), level=2, verbose=verbose)
            data = zload(f)
            data = compute_magnitude_data(data, chname1, chname2, chname3, ch_new_name)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp(
            '{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time),
            level=1, verbose=verbose)
        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def rectify(
            self, chs: Union[str, List[str]], out_folder: Optional[str] = None,
            inplace: bool = False,
    ) -> None:
        """
        Rectify one or more channels to their absolute value.

        Parameters
        ----------
        chs : str or list of str
            Channel name(s) to rectify.
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Default is False.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, name_contains=self.name_contains, name_excludes=self.name_excludes,
                    subfolders=self.subfolders)
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

    def phase_angle(
            self, ch: List[str], out_folder: Optional[str] = None,
            inplace: Optional[bool] = None,
    ) -> None:
        """
        Compute phase angles (Hilbert transform) for the given channels.

        Parameters
        ----------
        ch : list of str
            Channel names to compute phase angle for.
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Defaults to ``self.inplace``.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, name_excludes=self.name_excludes,
                    subfolders=self.subfolders)
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

    def continuous_relative_phase(
            self, ch_prox: str, ch_dist: str, out_folder: Optional[str] = None,
            inplace: Optional[bool] = None,
    ) -> None:
        """
        Compute continuous relative phase (CRP) between two channels.

        Parameters
        ----------
        ch_prox : str
            Name of the proximal channel.
        ch_dist : str
            Name of the distal channel.
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Defaults to ``self.inplace``.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, name_excludes=self.name_excludes,
                    subfolders=self.subfolders)
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

    def split_trial_by_gait_cycle(
            self, first_event_name: str, out_folder: Optional[str] = None,
            inplace: Optional[bool] = None,
    ) -> None:
        """
        Split trials into per-gait-cycle sub-trials using a numbered event.

        Parameters
        ----------
        first_event_name : str
            Name of the first event in the numbered sequence
            (e.g. 'RFS1'); see :func:`get_split_events`.
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Defaults to ``self.inplace``.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, name_excludes=self.name_excludes,
                    subfolders=self.subfolders)
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

    def renameevent(
            self, evt: Union[str, List[str]], nevt: Union[str, List[str]],
            out_folder: Optional[str] = None, inplace: Optional[bool] = None,
    ) -> None:
        """
        Rename event(s) ``evt`` to ``nevt`` in all zoo files.

        Parameters
        ----------
        evt : str or list of str
            Existing event name(s) to rename.
        nevt : str or list of str
            New event name(s). Must be the same length as ``evt``.
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Defaults to ``self.inplace``.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, name_excludes=self.name_excludes,
                    subfolders=self.subfolders)
        for f in fl:
            batchdisp('renaming events from {} to {} for {}'.format(evt, nevt ,f), level=2, verbose=verbose)
            data = zload(f)
            data = renameevent_data(data, evt, nevt)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)

        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def renamechannnel(
            self, ch: Union[str, List[str]], ch_new: Union[str, List[str]],
            out_folder: Optional[str] = None, inplace: Optional[bool] = None,
    ) -> None:
        """
        Rename channel(s) from ``ch`` to ``ch_new`` in all zoo files.

        Parameters
        ----------
        ch : str or list of str
            Current channel name(s) to rename.
        ch_new : str or list of str
            New channel name(s). Must be the same length as ``ch``.
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Defaults to ``self.inplace``.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, name_excludes=self.name_excludes,
                    subfolders=self.subfolders)
        for f in fl:
            batchdisp('renaming channels from {} to {} for {}'.format(ch, ch_new ,f), level=2, verbose=verbose)
            data = zload(f)
            data = renamechannel_data(data, ch, ch_new)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)

        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def removechannel(
            self, ch: List[str], mode: str = 'remove',
            out_folder: Optional[str] = None, inplace: Optional[bool] = None,
    ) -> None:
        """
        Remove or keep channels from zoo files.

        Parameters
        ----------
        ch : list of str
            Channel names to remove or keep, depending on ``mode``.
        mode : {'remove', 'keep'}, optional
            Operation mode. Default is 'remove'.
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Defaults to ``self.inplace``.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, name_excludes=self.name_excludes,
                    subfolders=self.subfolders)
        for f in fl:
            batchdisp('removing channels for {}'.format(f), level=2, verbose=verbose)
            data = zload(f)
            data = removechannel_data(data, ch, mode)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)

        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)


    def removeevent(
            self, events: Union[str, List[str]], mode: str = 'remove',
            out_folder: Optional[str] = None, inplace: Optional[bool] = None,
    ) -> None:
        """
        Remove or keep events across all channels in zoo files.

        Parameters
        ----------
        events : str or list of str
            Event name(s) to remove or keep, depending on ``mode``.
        mode : {'remove', 'keep'}, optional
            Operation mode. Default is 'remove'.
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Defaults to ``self.inplace``.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, name_excludes=self.name_excludes,
                    subfolders=self.subfolders)
        for f in fl:
            batchdisp('removing events {} for {}'.format(events, f), level=2, verbose=verbose)
            data = zload(f)
            data = removeevent_data(data, events, mode)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)

        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)


    def explodechannel(
            self, out_folder: Optional[str] = None,
            inplace: Optional[bool] = None,
    ) -> None:
        """
        Explode all n x 3 channels in a zoo file into X, Y, Z components.

        Parameters
        ----------
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Defaults to ``self.inplace``.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, name_excludes=self.name_excludes,
                    subfolders=self.subfolders)
        for f in fl:
            if verbose:
                batchdisp('exploding channels for {}'.format(f), level=2, verbose=verbose)
            data = zload(f)
            data = explodechannel_data(data)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)

        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def normalize(
            self, nlen: int = 101, out_folder: Optional[str] = None,
            inplace: Optional[bool] = None,
    ) -> None:
        """
        Time-normalize all channels to a target length.

        Parameters
        ----------
        nlen : int, optional
            Target number of samples. Default is 101.
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Defaults to ``self.inplace``.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, name_excludes=self.name_excludes,
                    subfolders=self.subfolders)
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

    def addevent(
            self, ch: Union[str, List[str]], event_type: str, event_name: str,
            out_folder: Optional[str] = None, inplace: Optional[bool] = None,
            fsamp: Optional[float] = None, constant: Optional[float] = None,
    ) -> None:
        """
        Add an event of type ``event_type`` named ``event_name`` to channel(s).

        Parameters
        ----------
        ch : str or list of str
            Channel name(s) to add the event to.
        event_type : str
            Event type; see :func:`addevent_data` for supported values.
        event_name : str
            Name of the event to add.
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Defaults to ``self.inplace``.
        fsamp : float, optional
            Sampling frequency in Hz. If None, read from zoosystem metadata.
        constant : float, optional
            Threshold/parameter value for certain event types.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, name_excludes=self.name_excludes,
                    subfolders=self.subfolders)
        for f in fl:
            if verbose:
                batchdisp('adding event {} to channel {} for {}'.format(event_type, ch, f), level=2, verbose=verbose)
            data = zload(f)
            data = addevent_data(data, ch, event_name, event_type, fsamp, constant)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)

        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def sync_channels(
            self, method: str, ch_1: List[str], ch_2: List[str],
            manual_lag: Optional[int] = None, out_folder: Optional[str] = None,
            inplace: Optional[bool] = None,
    ) -> None:
        """
        Biomechzoo-style wrapper for :func:`sync_channels_data`.

        Parameters
        ----------
        method : {'cross-correlation', 'manual'}
            Synchronization method.
        ch_1 : list of str
            First signal group's channel names.
        ch_2 : list of str
            Second signal group's channel names.
        manual_lag : int, optional
            Number of samples to shift when ``method='manual'``.
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Defaults to ``self.inplace``.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, name_excludes=self.name_excludes,
                    subfolders=self.subfolders)
        for f in fl:
            if verbose:
                batchdisp('sync_channels for file {} using method: {}'.format(f, method), level=2, verbose=verbose)
            data = zload(f)
            data = sync_channels_data(data, method, ch_1, ch_2, manual_lag)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp(
            '{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time), level=1, verbose=verbose)
        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def partition(
            self, evt_start: str, evt_end: str,
            out_folder: Optional[str] = None, inplace: Optional[bool] = None,
    ) -> None:
        """
        Partition data between events ``evt_start`` and ``evt_end``.

        Parameters
        ----------
        evt_start : str
            Name of the starting event.
        evt_end : str
            Name of the ending event.
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Defaults to ``self.inplace``.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, extension='.zoo', name_contains=self.name_contains, name_excludes=self.name_excludes,
                    subfolders=self.subfolders)
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

    def filter(
            self, ch: Union[str, List[str]], filt: Optional[Dict] = None,
            out_folder: Optional[str] = None, inplace: Optional[bool] = None,
    ) -> None:
        """
        Filter one or more channels.

        Parameters
        ----------
        ch : str or list of str
            Channel name(s) to filter.
        filt : dict, optional
            Filter parameters; see :func:`filter_data`.
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Defaults to ``self.inplace``.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, name_contains=self.name_contains, name_excludes=self.name_excludes,
                    subfolders=self.subfolders)
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

    def resample(
            self, up: int = 1, down: int = 1, out_folder: Optional[str] = None,
            inplace: Optional[bool] = None,
    ) -> None:
        """
        Resample data using polyphase filtering.

        Parameters
        ----------
        up : int, optional
            Upsampling factor. Default is 1.
        down : int, optional
            Downsampling factor. Default is 1.
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Defaults to ``self.inplace``.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            if verbose:
                batchdisp('resampling data for for data in {}'.format(f), level=2, verbose=verbose)
            data = zload(f)
            data = resample_data(data, up=up, down=down)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time),
            level=1, verbose=verbose)
        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def quats2euler(
            self, ch_prox: List[str], ch_dist: List[str], sequence: str,
            out_folder: Optional[str] = None, inplace: bool = False,
    ) -> None:
        """
        Generate joint angles from proximal/distal quaternion orientations.

        Parameters
        ----------
        ch_prox : list of str
            Proximal segment's quaternion channel names (W, X, Y, Z).
        ch_dist : list of str
            Distal segment's quaternion channel names (W, X, Y, Z).
        sequence : str
            Euler angle rotation sequence.
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Default is False.
        """

        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace
        fl = engine(in_folder, name_contains=self.name_contains, name_excludes=self.name_excludes,  subfolders=self.subfolders)
        for f in fl:
            batchdisp('quats2euler for distal channel {} with respect to proximal channel {} using sequence {} for {}'.
                      format(ch_dist, ch_prox, sequence, f), level=2, verbose=verbose)
            data = zload(f)
            data = quats2euler_data(data, ch_prox, ch_dist, sequence)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp('{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time),
            level=1, verbose=verbose)
        # Update self.folder after  processing
        self._update_folder(out_folder, inplace, in_folder)

    def dcms2euler(
            self, ch_prox: List[str], ch_dist: List[str], sequence: str,
            out_folder: Optional[str] = None, inplace: bool = False,
    ) -> None:
        """
        Generate joint angles from proximal/distal DCM orientations.

        Parameters
        ----------
        ch_prox : list of str
            Proximal segment's DCM column-vector channel names (i, j, k).
        ch_dist : list of str
            Distal segment's DCM column-vector channel names (i, j, k).
        sequence : str
            Euler angle rotation sequence.
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Default is False.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace

        fl = engine(in_folder, name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            batchdisp('DCMs2euler for distal channel {} with respect to proximal channel {} using sequence {} for {}'.
                      format(ch_dist, ch_prox, sequence, f), level=2, verbose=verbose)
            data = zload(f)
            data = dcms2euler_data(data, ch_prox, ch_dist, sequence)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp(
            '{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time),
            level=1, verbose=verbose)
        batchdisp('all files saved to: {}'.format(out_folder), level=1, verbose=verbose)
        self._update_folder(out_folder, inplace, in_folder)

    def marker2dcm(
            self, seg: str, origin: str, marker_1: str, marker_2: str,
            out_folder: Optional[str] = None, inplace: bool = False,
    ) -> None:
        """
        Biomechzoo-style wrapper for :func:`marker2dcm_data`.

        Parameters
        ----------
        seg : str
            Segment label used to name the output DCM channels.
        origin : str
            Marker defining the local coordinate system origin.
        marker_1 : str
            Marker defining the primary axis.
        marker_2 : str
            Marker used to define the temporary orthogonal-axis vector.
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Default is False.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace

        fl = engine(in_folder, name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            batchdisp('marker2dcm for segment {} in file {}'.format(seg, f), level=2, verbose=verbose)
            data = zload(f)
            data = marker2dcm_data(data, seg=seg, origin=origin, marker_1=marker_1, marker_2=marker_2)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp(
            '{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time),
            level=1, verbose=self.verbose)
        batchdisp('all files saved to: {}'.format(out_folder), level=1, verbose=verbose)
        self._update_folder(out_folder, inplace, in_folder)

    def quats2dcm(
            self, seg: str, ch: List[str], out_folder: Optional[str] = None,
            inplace: bool = False,
    ) -> None:
        """
        Biomechzoo-style wrapper for :func:`quats2dcm_data`.

        Parameters
        ----------
        seg : str
            Segment label used to name the output DCM channels.
        ch : list of str
            Quaternion channel names (W, X, Y, Z).
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Default is False.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace

        fl = engine(in_folder, name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            batchdisp('quats2dcm for segment {} in file {}'.format(seg, f), level=2, verbose=verbose)
            data = zload(f)
            data = quats2dcm_data(data, seg=seg, ch=ch)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp(
            '{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl),
                                                                       time.time() - start_time),
            level=1, verbose=self.verbose)
        batchdisp('all files saved to: {}'.format(out_folder), level=1, verbose=verbose)
        self._update_folder(out_folder, inplace, in_folder)

    def rotate_dcm(
            self, ch: List[str], axis: str, degrees: float,
            out_folder: Optional[str] = None, inplace: bool = False,
    ) -> None:
        """
        Biomechzoo-style wrapper for :func:`rotate_dcm_data`.

        Parameters
        ----------
        ch : list of str
            DCM column-vector channel names (i, j, k) for the segment
            to rotate.
        axis : {'X', 'Y', 'Z'}
            Principal axis to rotate about.
        degrees : float
            Rotation angle in degrees.
        out_folder : str, optional
            Output folder for processed files.
        inplace : bool, optional
            If True, overwrite in place. Default is False.
        """
        start_time = time.time()
        verbose = self.verbose
        in_folder = self.in_folder
        if inplace is None:
            inplace = self.inplace

        fl = engine(in_folder, name_contains=self.name_contains, subfolders=self.subfolders)
        for f in fl:
            batchdisp('rotating dcm segment {} in file {}'.format(ch, f), level=2, verbose=verbose)
            data = zload(f)
            data = rotate_dcm_data(data, ch=ch, axis=axis, degrees=degrees)
            zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
        method_name = inspect.currentframe().f_code.co_name
        batchdisp(
            '{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl),
                                                                       time.time() - start_time),
            level=1, verbose=self.verbose)
        batchdisp('all files saved to: {}'.format(out_folder), level=1, verbose=verbose)
        self._update_folder(out_folder, inplace, in_folder)
