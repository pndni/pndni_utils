#!/bin/env python
import argparse
import nibabel
import numpy as np
from .utils import safeintload, copy_forms


# from BEP011 (https://docs.google.com/document/d/1YG2g4UkEio4t_STIBOqYOwneLEs1emHIXbGKynx7V0Y/edit#heading=h.mqkmyp254xh6)
BIDS_LABELS = [('Background', 'BG'),
               ('Grey Matter', 'GM'),
               ('White Matter', 'WM'),
               ('Cerebrospinal Fluid', 'CSF'),
               ('Grey and White Matter', 'GWM'),
               ('Bone', 'B'),
               ('Soft Tissue', 'ST'),
               ('Non-brain', 'NB'),
               ('Lesion', 'L'),
               ('Coritcal Grey Matter', 'CGM'),
               ('Subcortical Grey Matter', 'SCGM'),
               ('Brainstem', 'BS'),
               ('Cerebellum', 'CBM')]


def _get_bids_label(l):
    if l >= len(BIDS_LABELS):
        raise ValueError('label is larger than bids label list')
    return BIDS_LABELS[l][1]
    

def calc_probmaps(input_files, labels=None, bids_labels=False):
    probmaps = {}
    for file_ in input_files:
        x = safeintload(file_)
        if labels is None or len(labels) == 0:
            labels = np.unique(x)
        for l in labels:
            labelmask = (x == l).astype(np.double)
            if bids_labels:
                key = _get_bids_label(l)
            else:
                key = l
            if key in probmaps.keys():
                probmaps[key] += labelmask
            else:
                probmaps[key] = labelmask
    for mask in probmaps.values():
        mask /= len(input_files)
    return probmaps

    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('out_template', type=str)
    parser.add_argument('input_file', type=str, nargs='+')
    parser.add_argument('--labels', type=int, nargs='*', help='Labels to use for probability map calculation. If not specified use all labels')
    parser.add_argument('--bids_labels', action='store_true',
                        help='Assume label numbers correspond to then standard anatomical labels in BEP011'
                             'use "labels2probmap --show_bids_labels" for a list')
    parser.add_argument('--show_bids_labels', action='store_true', help='show the standard bids labels from BEP011')
    args = parser.parse_args()
    if args.show_bids_labels:
        for i, (fullname, abbr) in enumerate(BIDS_LABELS):
            print(f'{i}\t{fullname}\t{abbr}')
    probmaps = calc_probmaps(args.input_file, labels=args.labels, bids_labels=args.bids_labels)
    header_template = nibabel.load(args.input_file[0])
    for key, mask in probmaps.items():
        outfile = args.out_template.format(label=key)
        out = nibabel.Nifti1Image(mask, None)
        copy_forms(header_template, out)
        out.to_filename(outfile)


if __name__ == '__main__':
    main()
