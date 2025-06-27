def findfield(data, target_event):
    """ searches in zoo data for the event value and channel name associated with target_event"""
    for channel, content in data.items():
        if channel == 'zoosystem':
            continue
        events = content.get('event', {})
        if target_event in events:
            return events[target_event], channel
    return None, None


