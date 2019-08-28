#!/bin/env python
import argparse
import nibabel
import numpy as np
import os
import subprocess
import sys
import tempfile


def _copy_forms(tmp, out):
    aff, code = tmp.get_qform(coded=True)
    out.set_qform(aff, code=code)
    aff, code = tmp.get_sform(coded=True)
    out.set_sform(aff, code=code)
def get_parser():
    parser = argparse.ArgumentParser(description="""
Converts a minc file to a nifti file using ``mnc2nii``, then rounds all the data 
to the nearest integer and converts the nifti file to an unsigned integer type. Checks that
all the values are within 0.1 of the nearest integer.
""")
    parser.add_argument('input_file', type=str)
    parser.add_argument('output_file', type=str)
    return parser


def main():
    args = get_parser().parse_args()
    input_file = args.input_file
    output_file = args.output_file
    (tmpfd, tmp) = tempfile.mkstemp(suffix='.nii', prefix='mnclabel2niilabel')
    os.close(tmpfd)
    try:
        subprocess.check_call(['mnc2nii', input_file, tmp])
        x = nibabel.load(tmp)
        xf = x.get_fdata()
        xfr = np.around(xf)
        if np.any(np.abs(xf - xfr) > 1e-1):
            print(np.max(np.abs(xf - xfr)))
            print('input image values not close enough to integers. exiting')
            return 1
        outtype = np.min_scalar_type(int(np.max(xfr)))
        niout = nibabel.Nifti1Image(xfr.astype(outtype), None)
        _copy_forms(x, niout)
        niout.to_filename(output_file)
    finally:
        os.remove(tmp)
    return 0


if __name__ == '__main__':
    sys.exit(main())
