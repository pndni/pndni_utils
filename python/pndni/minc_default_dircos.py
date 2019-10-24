import argparse
import h5py
import numpy as np
import shutil


def get_parser():
    parser = argparse.ArgumentParser(
        description='If direction_cosines for xpsace, yspace, and zspace are not set, '
        'set them to the default values.')
    parser.add_argument('in_file', type=str, help='Input minc2.0 file')
    parser.add_argument('out_file', type=str, help='Output minc2.0 file')
    return parser


def update_direction_cosines(mincfile):
    """For each of xspace, yspace, and zspace dimensions,
    if direction_cosines is not set, set it to
    [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]
    respectively
    """
    base_array = np.zeros((3, ), dtype=np.float)
    with h5py.File(mincfile, 'a') as f:
        for dimind, dim in enumerate(['/minc-2.0/dimensions/xspace',
                                      '/minc-2.0/dimensions/yspace',
                                      '/minc-2.0/dimensions/zspace']):
            if dim not in f:
                raise RuntimeError(f'{mincfile} does not have {dim}')
            grp = f[dim]
            if grp.ndim != 0 or grp.attrs['spacing'] == 'irregular':
                raise RuntimeError('Irregular sampling not supported')
            if 'direction_cosines' not in grp.attrs:
                dc = base_array.copy()
                dc[dimind] = 1.0
                grp.attrs['direction_cosines'] = dc


def main():
    parser = get_parser()
    args = parser.parse_args()
    shutil.copyfile(args.in_file, args.out_file)
    update_direction_cosines(args.out_file)


if __name__ == '__main__':
    main()
