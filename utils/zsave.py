from scipy.io import savemat
import inspect


def zsave(fl, data):
    # Get the caller function name dynamically
    caller_name = inspect.stack()[1].function

    # Initialize zoosystem.Processing if it doesn't exist
    zoosystem = data.get('zoosystem', {})

    # If Processing field exists, append; else create new list
    processing = zoosystem.get('Processing', [])

    if not isinstance(processing, list):
        # Defensive: if Processing is a single string, make it a list
        processing = [processing]

    processing.append(caller_name)

    # Update the data dict
    zoosystem['Processing'] = processing
    data['zoosystem'] = zoosystem

    # Save the data
    savemat(fl, data)