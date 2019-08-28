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


def get_parser():
    parser = argparse.ArgumentParser(description="""Combine multiple label files into one, where output labels are the intersection
of the input labels. For example, if labelfile1.nii and labelfile2.nii have the following
labels:

========================= =====
labelfile1.nii label name Value
========================= =====
Grey matter                   1
White matter                  2
========================= =====

========================= =====
labelfile2.nii label name Value
========================= =====
Left hemisphere               1
Right hemisphere              2
========================= =====

the command

.. code-block:: bash

   combinelabels out.nii labelfile1.nii labelfile2.nii

will result in

========================== =====
out.nii label name         Value
========================== =====
Grey matter + left hemi.       1
White matter + left hemi.      2
Grey matter + right hemi.      3
White matter + right hemi.     4
========================== =====

A value of 0 in any label file will result in 0 in the output.

More than two label files may be used. For example

.. code-block:: bash

   combinelabels out.nii labelfile1.nii labelfile2.nii labelfile3.nii

is equivalent to
    
.. code-block:: bash

   combinelabels tmp.nii labelfile1.nii labelfile2.nii
   combinelabels out.nii tmp.nii labelfile3.nii
""")
    parser.add_argument('output_file', type=str, help='Output file name')
    input_files_help = ("input label files. each image must be of integer values >= 0")
    parser.add_argument('input_files', type=str, nargs='+', help=input_files_help)
    return parser


def main():
    args = get_parser().parse_args()
    label_images = (safeintload(file_) for file_ in args.input_files)
    out = reduce(combine2labels, label_images)
    # reduce to smallest type possible
    out = out.astype(np.min_scalar_type(out.max()), copy=False)
    outnifti = nibabel.Nifti1Image(out, None)
    copy_forms(nibabel.load(args.input_files[0]), outnifti)
    outnifti.to_filename(args.output_file)


if __name__ == '__main__':
    main()
