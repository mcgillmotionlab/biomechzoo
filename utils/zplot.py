import matplotlib.pyplot as plt


def zplot(data, ch, xlabel='frames', ylabel='angles (deg)'):
    """ helper function to plot a single channel of a zoo file, along with
    any existing events

    Arguments
        data: dict, loaded zoo file
        ch: str, name of branch of a zoo file. e.g. 'RkneeAngles'
        xlabel: str, label for xaxis. Default 'frames'
        ylabel: str, label for yaxis. Default 'angles (deg)'

    Returns
        None
    """
    # todo: complete plotting of events

    # plot line data
    array_to_plot = data[ch]['line']
    plt.figure()
    plt.plot(array_to_plot)
    plt.title(ch)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)

    # plot event data (if any)
    events_to_plot = data[ch]['event']
    for eventname in events_to_plot:
        evtx = events_to_plot[eventname][0]
        evty = events_to_plot[eventname][1]
        plt.plot(evtx, evty)

    plt.show()


if __name__ == '__main__':
    # -------TESTING--------
    import os
    from utils.zload import zload

    # get path to sample zoo file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    fl = os.path.join(project_root, 'data', 'other', 'HC030A05.zoo')

    # load  zoo file
    data = zload(fl)
    data = data['data']
    ch = 'SACR'
    zplot(data, ch)
