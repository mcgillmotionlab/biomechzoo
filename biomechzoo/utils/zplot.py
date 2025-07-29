import matplotlib.pyplot as plt


def zplot(data, ch, xlabel='frames', ylabel='angles (deg)'):
    """
    Plot a single channel of a zoo file, along with any existing events.

    Parameters
    ----------
    data : dict
        Loaded zoo file.
    ch : str
        Name of the channel to plot, e.g., 'RkneeAngles'.
    xlabel : str
        Label for x-axis. Default is 'frames'.
    ylabel : str
        Label for y-axis. Default is 'angles (deg)'.

    Returns
    -------
    None
    """

    if ch not in data:
        raise KeyError(f"Channel '{ch}' not found in data.")

    y = data[ch]['line']
    x = range(len(y))

    plt.figure(figsize=(10, 4))
    plt.plot(x, y, label='Signal', linewidth=2)
    plt.title(ch)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)

    # Plot events if available
    events = data[ch].get('event', {})
    for name, coords in events.items():
        evtx, evty = coords[0], coords[1]
        plt.plot(evtx, evty, 'ro')
        plt.text(evtx, evty, name, fontsize=8, color='red', ha='left', va='bottom')

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    # -------TESTING--------
    import os
    from biomechzoo.utils.zload import zload

    # get path to sample zoo file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    fl = os.path.join(project_root, 'data', 'other', 'HC030A05.zoo')

    # load  zoo file
    data = zload(fl)
    ch = 'SACR'
    zplot(data, ch)
