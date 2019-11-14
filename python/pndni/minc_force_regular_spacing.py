import argparse
import h5py
import netCDF4
import numpy as np
import shutil
import os


def get_parser():
    parser = argparse.ArgumentParser(
        description='If xspace, yspace, and/or zspace is set to irregular spacing, '
                    'check that the actually spacing is close enough to nominal ("step"), '
                    'and if so set the "spacing" parameter to regular.')
    parser.add_argument('in_file', type=str, help='Input minc file')
    parser.add_argument('out_file', type=str, help='Output minc file')
    parser.add_argument('--atol', type=float, help='passed to numpy.allclose when comparing spacing to nominal', default=1e-8)
    parser.add_argument('--rtol', type=float, help='passed to numpy.allclose when comparing spacing to nominal', default=1e-5)
    return parser


def _hdf5rootkeys(fname):
    with h5py.File(fname, 'r') as f:
        return list(f.keys())


def force_regular_spacing(mincfile, atol=1e-8, rtol=1e-5):
    if h5py.is_hdf5(mincfile) and 'minc-2.0' in _hdf5rootkeys(mincfile):
        with h5py.File(mincfile, 'a') as f:
            dims = ['/minc-2.0/dimensions/xspace',
                    '/minc-2.0/dimensions/yspace',
                    '/minc-2.0/dimensions/zspace']
            for dim in dims:
                if f[dim].attrs['spacing'] == b'irregular':
                    if not np.allclose(f[dim].attrs['step'], np.diff(f[dim][:]), atol=atol, rtol=rtol):
                        raise RuntimeError('Differences between irregular and nominal step size too large')
                    f[dim].attrs['spacing'] = b'regular__'
    else:
        with netCDF4.Dataset(mincfile, 'a') as f:
            dims = ['xspace',
                    'yspace',
                    'zspace']
            for dim in dims:
                if f[dim].spacing == 'irregular':
                    if not np.allclose(f[dim].step, np.diff(f[dim][:]), atol=atol, rtol=rtol):
                        raise RuntimeError('Differences between irregular and nominal step size too large')
                    f[dim].spacing = 'regular__'


def main():
    parser = get_parser()
    args = parser.parse_args()
    shutil.copyfile(args.in_file, args.out_file)
    try:
        force_regular_spacing(args.out_file, args.atol, args.rtol)
    except:
        os.remove(args.out_file)
        raise


if __name__ == '__main__':
    main()
