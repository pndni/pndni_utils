import argparse
import nibabel
import numpy as np
import sys


class _Result(object):

    def __init__(self, desc=None, extra=None):
        if desc is None:
            self.desc = ''
        else:
            self.desc = desc
        self.extra = extra
        self.name = type(self).__name__  # https://www.w3resource.com/python-exercises/class-exercises/python-class-exercise-12.php


    def __repr__(self):
        extrastr = f', {self.extra}' if self.extra else ''
        return f'{self.name}({self.desc}{extrastr})'

    def __str__(self):
        return '{}{}'.format(self.name, ': ' + self.desc if self.desc else '')

    
class _SuccessResult(_Result):

    def __bool__(self):
        return True


class _ErrorResult(_Result):

    def __bool__(self):
        return False


class Equal(_SuccessResult):
    status_code = 0

class NotEqual(_ErrorResult):
    status_code = 1

class AffineMismatch(_ErrorResult):
    status_code = 2


ORIENTATION = [[0, 1],
               [1, 1],
               [2, 1]]


def alleq(x, y):
    return np.all(x == y)


def alleq_round(x, y):
    return np.all(np.around(x) == np.around(y))


def orient(x):
    orn = nibabel.orientations.io_orientation(x.affine)
    difforn = nibabel.orientations.ornt_transform(orn, ORIENTATION)
    y = x.as_reoriented(difforn)
    assert nibabel.orientations.aff2axcodes(y.affine) == ('R', 'A', 'S')
    return y


def get_parser():
    parser = argparse.ArgumentParser(description='Compare two images after lining them up in '
                                                 'world coordinates. May be used to compare images '
                                                 'with different data layouts, or where one is a cropped '
                                                 'version of the other (so long as the image orientations '
                                                 'in world coordinates are consistent).')
    parser.add_argument('image1', help='Filename of first image to be compared')
    parser.add_argument('image2', help='Filename of first image to be compared')
    mogroup = parser.add_mutually_exclusive_group()
    mogroup.add_argument('--close', action='store_true',
                         help='Use numpy.allclose instead of checking for strict equality.')
    mogroup.add_argument('--round', action='store_true',
                         help='Round each image to the nearest int before comparing.')
    parser.add_argument('--intersection_only', action='store_true',
                        help='Only compare data where the images overlap in world coordinates')
    parser.add_argument('--round_offset', action='store_true',
                        help='If the images are not offset by an integer amount, this flag '
                             'rounds the offset value. This can help if the calculated offset '
                             'is a non-integer due to rounding errors.')
    parser.add_argument('--verbose', action='store_true')
    return parser


def main():
    args = get_parser().parse_args()
    result  = compare(nibabel.load(args.image1), nibabel.load(args.image2),
                      close=args.close, round_=args.round,
                      intersection_only=args.intersection_only,
                      round_offset=args.round_offset)
    if args.verbose:
        print(result)
    return result.status_code


def compare(im1, im2, close=False, round_=False, intersection_only=False, round_offset=False):
    if close and round_:
        raise ValueError('Only one of "close" and "round_" may be specified')
    checkoutside = not intersection_only
    if close:
        eqfunc = np.allclose
        eqfuncstr = 'np.allclose'
    elif round_:
        eqfunc = alleq_round
        eqfuncstr = 'rounding'
    else:
        eqfunc = alleq
        eqfuncstr = 'strict equality'
    if not (np.allclose(im1.affine, im2.affine) and im1.shape == im2.shape):
        im1 = orient(im1)
        im2 = orient(im2)
        if not np.allclose(im1.affine[:3, :3], im2.affine[:3, :3]):
            return AffineMismatch('Rotation and scaling do not match.')
        im1_to_im2 = np.linalg.solve(im2.affine, im1.affine)
        for axes, offset in enumerate(im1_to_im2[:3, -1]):
            if not round_offset and not np.allclose(offset, int(np.around(offset))):
                return AffineMismatch('Images are not offset an integer amount. Use the "round_offset" flag to ignore.')
            offset = int(np.around(offset))
            if offset < 0:
                if checkoutside and not eqfunc(np.asarray(im1.dataobj)[tuple(slice(-offset) if axes == i else slice(None) for i in range(3))], 0):
                    return NotEqual('Data outside the overlap is not zero. Use the "checkoutside" flag to ignore.')
                im1 = im1.slicer[tuple(slice(-offset, None) if axes == i else slice(None) for i in range(3))]
            elif offset > 0:
                if checkoutside and not eqfunc(np.asarray(im2.dataobj)[tuple(slice(offset) if axes == i else slice(None) for i in range(3))], 0):
                    return NotEqual('Data outside the overlap is not zero. Use the "checkoutside" flag to ignore.')
                im2 = im2.slicer[tuple(slice(offset, None) if axes == i else slice(None) for i in range(3))]
        shapediff = np.array(im2.shape) - np.array(im1.shape)
        for axes, offset in enumerate(shapediff):
            if offset < 0:
                if checkoutside and not eqfunc(np.asarray(im1.dataobj)[tuple(slice(im2.shape[axes], None)
                                                                             if axes == i else slice(None)
                                                                             for i in range(3))],
                              0):
                    return NotEqual('Data outside the overlap is not zero. Use the "checkoutside" flag to ignore.')
                im1 = im1.slicer[tuple(slice(None, im2.shape[axes]) if axes == i else slice(None) for i in range(3))]
            elif offset > 0:
                if checkoutside and not eqfunc(np.asarray(im2.dataobj)[tuple(slice(im1.shape[axes], None)
                                                                             if axes == i else slice(None)
                                                                             for i in range(3))],
                              0):
                    return NotEqual('Data outside the overlap is not zero. Use the "checkoutside" flag to ignore.')
                im2 = im2.slicer[tuple(slice(None, im1.shape[axes]) if axes == i else slice(None) for i in range(3))]
        assert np.allclose(im1.affine[:3, :3], im2.affine[:3, :3])  # use allclose in case of floating point error
        if round_offset:
            assert np.all(np.around(im1.affine[:3, -1]) == np.around(im2.affine[:3, -1]))
        else:
            assert np.allclose(im1.affine[:3, -1], im2.affine[:3, -1])
    if eqfunc(np.asarray(im1.dataobj), np.asarray(im2.dataobj)):
        if round_offset:
            misalignment = im1.affine[:3, -1] - im2.affine[:3, -1]
            return Equal('Images equal (using {}). Misaligned by {}, {}, {} (in RAS).'.format(eqfuncstr, *misalignment),
                         extra=misalignment)
        else:
            return Equal('Images equal (using {}).'.format(eqfuncstr))
    else:
        return NotEqual('Images NOT equal (using {})'.format(eqfuncstr))
                

if __name__ == '__main__':
    sys.exit(main())
