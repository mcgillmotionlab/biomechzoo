import time
import inspect
import os

from biomechzoo.utils import batchdisp
from biomechzoo.utils.engine import engine
from biomechzoo.utils.zload import zload
from biomechzoo.utils.zsave import zsave
from biomechzoo.utils.batchdisp import batchdisp

from src.analysis.signal_analysis_data import signal_analysis_data


def signal_analysis(in_folder, channels, etype, ename,  name_contains=None, subfolders=None,
                    verbose=None, out_folder=None, inplace=False, single_channel=True, save_channel=None):
    """
    Call function for linear and non-linear signal analysis.


    Parameters
    ----------
    in_folder : str
        Path to the root folder containing the zoo files.
    channels : str or list[str]
        Names of channel(s) to analyze
    etype : str
        Name of the function to call
    ename : str
        Event name of saving purposes.
    name_contains : bool default=None
        To only target zoo files that contain this name
    subfolders: str, default=None
    verbose : str, default=None
    out_folder : str, default=None
    inplace : bool, default=False
    single_channel=True
    save_channel=None

    Returns
    -------
    None. Automatically saves the zoo-files in the specified out-folder.
    """
    start_time = time.time()

    fl = engine(in_folder, name_contains=name_contains, subfolders=subfolders)
    for f in fl:
        batchdisp('Computing {} for {}'.format(etype, f), level=2, verbose=verbose)
        data = zload(f)
        data = signal_analysis_data(data, channels=channels, ename=ename, etype=etype, single_channel=single_channel,
                                    save_channel=save_channel)
        zsave(f, data, inplace=inplace, out_folder=out_folder, root_folder=in_folder)
    method_name = inspect.currentframe().f_code.co_name
    batchdisp(
        '{} process complete for {} file(s) in {:.2f} secs'.format(method_name, len(fl), time.time() - start_time),
        level=1, verbose=verbose)
