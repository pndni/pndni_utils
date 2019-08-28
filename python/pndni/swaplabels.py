import argparse
import nibabel
import numpy as np
from .utils import copy_forms


def parse_mapstr(mapstr):
    mapstr.strip('"\'')
    pairs = mapstr.split(',')
    outmap = {}
    for p in pairs:
        keystr, valstr = p.split(':')
        outmap[int(keystr)] = int(valstr)
    return outmap


def get_parser():
    parser = argparse.ArgumentParser(description="""
Swap/remap labels in an image. For example, to change all the values of 2 in the image to 1 and all the values of 5 to 10

.. code-block:: bash

   swaplabels "2: 1, 5: 10" input.nii output.nii

Any unspecified value will be set to 0.
""")
    parser.add_argument('map', type=str,
                        help="Mapping string of the form 'inval1: outval1, inval2: outval2, ...' "
                        "All values must be integers.")
    parser.add_argument('input', type=str)
    parser.add_argument('output', type=str)
    return parser


def main():
    args = get_parser().parse_args()
    label_map = parse_mapstr(args.map)
    x = nibabel.load(args.input)
    xdata = np.asarray(x.dataobj)
    ydata = np.zeros(xdata.shape, np.min_scalar_type(max(label_map.values())))
    for key, val in label_map.items():
        ydata[xdata == key] = val
    y = nibabel.Nifti1Image(ydata, None)
    copy_forms(x, y)
    y.to_filename(args.output)
