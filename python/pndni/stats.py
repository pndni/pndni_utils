import argparse
from functools import partial
import nibabel
import numpy as np
from scipy.ndimage import labeled_comprehension
from scipy.stats import skew, kurtosis


def std(x):
    # this seems to mimic the fslstats std calculation
    if x.size == 1:
        return 0.0
    else:
        return np.std(x, ddof=1)


class Append(argparse.Action):

    def __init__(self, option_strings, dest, nargs=0, function=None, **kwargs):
        if nargs != 0:
            raise ValueError('nargs must be 0 for Append action')
        if function is None:
            raise ValueError('function must be specified')
        self.function = function
        super().__init__(option_strings, dest, nargs=nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string):
        if not hasattr(namespace, 'statslist'):
            setattr(namespace, 'statslist', [])
        namespace.statslist.append(self.function)


def get_parser():
    parser = argparse.ArgumentParser(description='Behaves like fslstats, but with different statistics.')
    parser.add_argument('-K', help='Label mask', nargs='?')
    parser.add_argument('input', help='Input image (nii or nii.gz)')
    parser.add_argument('-m', help='Mean', action=Append, function=np.mean)
    parser.add_argument('-s', help='Standard deviation', action=Append, function=std)
    parser.add_argument('--skew', action=Append, function=partial(skew, axis=None))
    parser.add_argument('--kurtosis', action=Append, function=partial(kurtosis, axis=None))
    parser.add_argument('--median', action=Append, function=np.median)
    return parser


def main():
    args = get_parser().parse_args()
    out = stats(args.input, args.statslist, K=args.K)
    if out is not None:
        print(' '.join([str(o) for o in out]))


def stats(input, statslist, K=None):

    input = nibabel.load(input).get_fdata()

    if K:
        mask = nibabel.load(K).get_fdata()
        # mask = np.asanyarray(nibabel.load(args.K).dataobj)
        uniq = np.unique(mask)
        if not np.all(uniq == uniq.astype(np.int)):
            raise RuntimeError("mask must have only integer values")
        mask = mask.astype(np.int)
        labels = np.arange(1, np.max(mask) + 1)
        out = []
        for l in labels:
            out.extend([labeled_comprehension(input, mask, l, func, np.float, 0.0) for func in statslist])
    else:
        out = [func(input) for func in statslist]
    return out


if __name__ == '__main__':
    main()
