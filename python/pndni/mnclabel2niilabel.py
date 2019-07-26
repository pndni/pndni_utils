#!/bin/env python
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


def main():
    if len(sys.argv) != 3:
        print('Usage: input output')
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
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
            sys.exit(1)
        outtype = np.min_scalar_type(int(np.max(xfr)))
        niout = nibabel.Nifti1Image(xfr.astype(outtype), None)
        _copy_forms(x, niout)
        niout.to_filename(output_file)
    finally:
        os.remove(tmp)


if __name__ == '__main__':
    main()
