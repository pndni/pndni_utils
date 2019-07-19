#!/bin/env python
import argparse
from functools import reduce
import nibabel
import numpy as np


def _copy_forms(imagefile, out):
    tmp = nibabel.load(imagefile)
    aff, code = tmp.get_qform(coded=True)
    out.set_qform(aff, code=code)
    aff, code = tmp.get_sform(coded=True)
    out.set_sform(aff, code=code)


def combine2labels(l1, l2):
    out = l1 + (l2 - 1) * l1.max()
    out[np.logical_or(l1 == 0, l2 == 0)] = 0
    return out


def _saveload(file_):
    x = np.asarray(nibabel.load(file_).dataobj)
    xc = x.astype('uint32', copy=False)
    if xc is not x:
        if not np.all(x == xc):
            raise ValueError('input image contained non integer values or values < 0')
    return xc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output_file', type=str)
    input_files_help = ("input label files. each image must be of integer values >= 0")
    parser.add_argument('input_files', type=str, nargs='+', help=input_files_help)
    args = parser.parse_args()
    label_images = (_saveload(file_) for file_ in args.input_files)
    out = reduce(combine2labels, label_images)
    # reduce to smallest type possible
    out = out.astype(np.min_scalar_type(out.max()), copy=False)
    outnifti = nibabel.Nifti1Image(out, None)
    _copy_forms(args.input_files[0], outnifti)
    outnifti.to_filename(args.output_file)


if __name__ == '__main__':
    main()
