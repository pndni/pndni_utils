import argparse
import nibabel
import numpy as np
from pathlib import Path


def get_parser():
    parser = argparse.ArgumentParser(
        description=main.__doc__
        )
    parser.add_argument('input_file', type=Path,
                        help='Input file')
    parser.add_argument('output_file', type=Path,
                        help='Output file')
    parser.add_argument('--maxangle', type=float, default=1e-6,
                        help='The maximum permissible angle (in radians) that '
                             'the differences in the coordinate axes are permitted '
                             'to deviate from 90 degres. In other words limits '
                             'the shearing in the input affine (The qform cannot '
                             'encode shear.')
    return parser


def _ang(v1, v2):
    return np.abs(np.arccos(np.dot(v1, v2) / np.linalg.norm(v1, ord=2) / np.linalg.norm(v2, ord=2)) - np.pi / 2.0)


def _check_ang(R, maxang):
    angs = np.array([_ang(R[:, i], R[:, j]) for i, j in [(0, 1), (0, 2), (1, 2)]])
    if np.any(angs > maxang):
        raise RuntimeError('Too much shear present. Try increasing maxangle')


def forceqform(input_file, output_file, maxangle=1e-6):
    """
    Ensure that only qform is set. Because ANTs only uses the qform, this will
    force other applications to use the qform as well, keeping everything consistent.

    * If the qform code is > 0 and the sform code is 0, change nothing.
    * If both codes are > 0, set the sform code to 0
    * if the qform is 0 and the sform code is > 0, set the qform based on the
      affine matrix as determined by nibabel (which will be based on the sform),
      and set sform code to 0. Uses the function :py:func:`set_sform` from :py:mod:`nibabel`
    * If both codes are 0, raise a RuntimeError
    """
    img = nibabel.load(str(input_file))
    qcode = img.get_qform(coded=True)[1]
    scode = img.get_sform(coded=True)[1]
    if qcode > 0 and scode == 0:
        # already the way we want it
        pass
    elif qcode > 0 and scode > 0:
        img.set_sform(None)
    elif qcode == 0 and scode > 0:
        _check_ang(img.affine[:3, :3], maxangle)
        img.set_qform(img.affine, code=scode)
        img.set_sform(None)
    else:
        raise RuntimeError('Neither sform and qform set')
    img.to_filename(str(output_file))


def main():
    args = get_parser().parse_args()
    forceqform(args.input_file, args.output_file, maxangle=args.maxangle)


if __name__ == '__main__':
    main()
