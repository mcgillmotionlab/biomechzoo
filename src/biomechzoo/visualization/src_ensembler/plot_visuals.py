import re

def _assign_subject_colors(subject_list, str_pattern):
    """Creates subject specific colors"""

    if str_pattern:
        unique_subjects = get_unique_subjects(str_pattern)
    elif subject_list:
        unique_subjects = subject_list
    else:
        raise ValueError('No subject pattern or subject list specified')

    subject_colors = {}
    for idx, subj in enumerate(unique_subjects):
        line_color, shade_color, marker_color = _assign_colors(idx)
        subject_colors[subj] = {
            "line": line_color,
            "shade": shade_color,
            "event": marker_color
        }
    return subject_colors


def get_unique_subjects(ens, str_pattern):
    """
    Extract unique subject names from subject pattern initialized in __init__()

    Parameters
    ----------
    ens : Class
        The ensembler class
    str_pattern : list of string
        the regular expression pattern to find in the zoo_files.

    Returns
    -------
    unique_subjects : list

    Notes
    -----
    Maximum length of the list is 3.
    """

    subjects = set()
    for fl in ens.zoo_files:
        match = re.search(str_pattern[0], fl)
        if match:
            subjects.add(match.group(0))
        elif match is None:
            match = re.search(str_pattern[1], fl)
            if match:
                subjects.add(match.group(0))
            elif match is None:
                match = re.search(str_pattern[2], fl)
                if match:
                    subjects.add(match.group(0))
                else:
                    subjects.add("unknown")

    return sorted(subjects)


def  _assign_colors(i, color_library=None):
    """
    Assign colors to each subject automatically.

    Parameters
    ----------
        i: integer
            The index associated with the subject pattern

    Returns
    --------
        hex_code: string
            The ith hex-code from pc.qualitative.D3 library.
        shade_color: string
            The associated shade color

        marker_color: string
            The complementary marker color
    """
    if color_library is None:
        color_library = pc.qualitative.D3

    hex_code = color_library[i % len(color_library)]
    h = hex_code.lstrip('#')
    rgb =tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    #shade color with opacity
    opacity = 0.3
    shade_color = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {opacity})"

    #Get complementary color for marker
    comp = ['%02X' % (255 - a) for a in rgb]
    marker_color =  '#' + ''.join(comp)

    return hex_code, shade_color, marker_color


def _assign_condition_colors(conditions):
    NotImplementedError()