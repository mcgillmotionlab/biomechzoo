from filter_line import filter_line


def filter_data(data, ch, filt=None):
    """ filter all channels in ch according to filt properties
    Arguments:
        data: dict, loaded zoo file
        ch: list, channels to filter
        filt: dict, contains filter instructions
    """
    # raise NotImplementedError
    # # set filter type

    for channel in ch:
            ch_data_line = data[channel]['line']
            data[channel]['line'] = filter_line(ch_data_line, filt)

    return data


