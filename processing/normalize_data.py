from biomechzoo.processing.normalize_line import normalize_line

def normalize_data(data, target_length):
    '''
    File-level: normalize all channels in the loaded zoo dict to target_length.
    '''
    data_new = data.copy()
    normalized_channels = {}
    for ch_name, ch_data in data_new['channels'].items():
        normalized_channels[ch_name] = normalize_line(ch_data, target_length)
    data_new['channels'] = normalized_channels
    return data_new
