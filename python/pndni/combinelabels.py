#!/bin/env python
import argparse
from functools import reduce
import nibabel
import numpy as np
from .utils import safeintload, copy_forms


def combine2labels(l1, l2):
    out = l1 + (l2 - 1) * l1.max()
    out[np.logical_or(l1 == 0, l2 == 0)] = 0
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output_file', type=str)
    input_files_help = ("input label files. each image must be of integer values >= 0")
    parser.add_argument('input_files', type=str, nargs='+', help=input_files_help)
    args = parser.parse_args()
    label_images = (safeintload(file_) for file_ in args.input_files)
    out = reduce(combine2labels, label_images)
    # reduce to smallest type possible
    out = out.astype(np.min_scalar_type(out.max()), copy=False)
    outnifti = nibabel.Nifti1Image(out, None)
    copy_forms(nibabel.load(args.input_files[0]), outnifti)
    outnifti.to_filename(args.output_file)


if __name__ == '__main__':
    main()
