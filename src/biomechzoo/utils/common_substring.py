def common_substring_join(strings):
    # Split each string into parts
    split_lists = [s.split('_') for s in strings]

    # Transpose so we compare column-wise
    common_parts = []
    for parts in zip(*split_lists):
        if len(set(parts)) == 1:   # All strings share this part
            common_parts.append(parts[0])
        else:
            # As soon as one position differs, skip but keep checking further ones
            continue

    return "_".join(common_parts)

if __name__ == '__main__':
    # Example
    a = [
        'a_pelvis_antpost_tilt_corr',
        'a_pelvis_ml_tilt_corr',
        'a_pelvis_vert_tilt_corr'
    ]

    print(common_substring_join(a))