from pndni import all_equal
import nibabel
import numpy as np
import pytest


def test_simple():
    x = nibabel.Nifti1Image(np.arange(24).reshape(2, 3, 4), np.eye(4))
    y = nibabel.Nifti1Image(np.arange(24).reshape(2, 3, 4), np.eye(4))
    assert all_equal.compare(x, y)
    assert all_equal.compare(x, y, close=True)


def test_offset1():
    xarr = np.arange(24).reshape(2, 3, 4)
    xarr[:1] = 0
    xarr[:, :1] = 0
    xarr[:, :, :1] = 0
    x = nibabel.Nifti1Image(xarr, np.eye(4))
    y = x.slicer[1:, 1:, 1:]
    assert isinstance(all_equal.compare(x, y), all_equal.Equal)
    assert all_equal.compare(x, y)
    xarr[0, 0, 0] = 1
    x = nibabel.Nifti1Image(xarr, np.eye(4))
    assert isinstance(all_equal.compare(x, y), all_equal.NotEqual)
    assert not all_equal.compare(x, y)
    assert isinstance(all_equal.compare(x, y, intersection_only=True), all_equal.Equal)
    assert all_equal.compare(x, y, intersection_only=True)


def test_offset2():
    xarr = np.arange(24).reshape(2, 3, 4)
    xarr[:1] = 0
    xarr[:, :2] = 0
    xarr[:, :, :2] = 0
    x = nibabel.Nifti1Image(xarr, np.eye(4))
    y = x.slicer[1:, 2:, 2:]
    assert all_equal.compare(x, y)
    xarr[0, 0, 0] = 1
    x = nibabel.Nifti1Image(xarr, np.eye(4))
    assert not all_equal.compare(x, y)
    assert all_equal.compare(x, y, intersection_only=True)


def test_offset2():
    xarr = np.arange(24).reshape(2, 3, 4)
    xarr[-1:] = 0
    xarr[:, -2:] = 0
    xarr[:, :, -2:] = 0
    x = nibabel.Nifti1Image(xarr, np.eye(4))
    y = x.slicer[:-1, :-2, :-2]
    assert all_equal.compare(x, y)
    xarr[-1, -1, -1] = 1
    x = nibabel.Nifti1Image(xarr, np.eye(4))
    assert not all_equal.compare(x, y)
    assert all_equal.compare(x, y, intersection_only=True)


def test_offset3():

    xarr = np.array([[[0, 0, 1, 2, 3],
                      [0, 0, 4, 5, 6],
                      [0, 0, 7, 8, 9],
                      [0, 0, 0, 0, 0]]]).astype(np.float)
    yarr = np.array([[[0, 0, 0, 0],
                      [1, 2, 3, 0],
                      [4, 5, 6, 0],
                      [7, 8, 9, 0]]]).astype(np.float)
    xaff = np.array([[1, 0, 0, 0],
                     [0, 1, 0, 0],
                     [0, 0, 2, -4],
                     [0, 0, 0, 1]]).astype(np.float)
    yaff = np.array([[1, 0, 0, 0],
                     [0, 1, 0, -1],
                     [0, 0, 2, 0],
                     [0, 0, 0, 1]]).astype(np.float)
    x = nibabel.Nifti1Image(xarr, xaff)
    y = nibabel.Nifti1Image(yarr, yaff)
    assert all_equal.compare(x, y)
    yaff2 = yaff.copy()
    yaff2[:3, -1] += 0.2
    assert not all_equal.compare(x, nibabel.Nifti1Image(yarr, yaff2))
    res = all_equal.compare(x, nibabel.Nifti1Image(yarr, yaff2), round_offset=True)
    assert res
    assert np.allclose(res.extra, [-0.2, -0.2, -0.2])
    yaff2 = yaff.copy()
    yaff2[0, 0] = 1.1
    assert not all_equal.compare(x, nibabel.Nifti1Image(yarr, yaff2))
    yarr2 = yarr.copy()
    yarr2[0, 0, 2] = 1
    assert not all_equal.compare(x, nibabel.Nifti1Image(yarr2, yaff))
    assert all_equal.compare(x, nibabel.Nifti1Image(yarr2, yaff), intersection_only=True)
    yarr2 = yarr.copy()
    yarr2[0, -1, 1] = 1
    assert not all_equal.compare(x, nibabel.Nifti1Image(yarr2, yaff))
    yarr2 = yarr.copy()
    yarr2[0, 1, -1] = 1
    assert not all_equal.compare(x, nibabel.Nifti1Image(yarr2, yaff))
    assert all_equal.compare(x, nibabel.Nifti1Image(yarr2, yaff), intersection_only=True)


def test_crooked_affine():

    xarr = np.array([[[0, 0, 1, 2, 3],
                      [0, 0, 4, 5, 6],
                      [0, 0, 7, 8, 9],
                      [0, 0, 0, 0, 0]]]).astype(np.float)
    yarr = np.array([[[0, 0, 0, 0],
                      [1, 2, 3, 0],
                      [4, 5, 6, 0],
                      [7, 8, 9, 0]]]).astype(np.float)
    affbase = np.array([[1.2, 3, .2, 0],
                        [5, 2.1, .1, 0],
                        [1., 2., 3., 0],
                        [0., 0, 0, 1]])
    xaff = affbase.copy()
    xaff[:3, -1] = [-.4, -.2, -6]
    yaff = affbase.copy()
    yaff[:3, -1] = [-3., -2.1, -2]
    x = nibabel.Nifti1Image(xarr, xaff)
    y = nibabel.Nifti1Image(yarr, yaff)
    assert all_equal.compare(x, y)


def test_round():
    x = nibabel.Nifti1Image(np.arange(24).reshape(2, 3, 4).astype(np.float), np.eye(4))
    ydata = np.arange(24).reshape(2, 3, 4).astype(np.float)
    ydata += (np.random.random_sample(size=(2, 3, 4)) - 0.5) * 0.9
    y = nibabel.Nifti1Image(ydata, np.eye(4))
    assert not all_equal.compare(x, y)
    assert not all_equal.compare(x, y, close=True)
    assert all_equal.compare(x, y, round_=True)
    with pytest.raises(ValueError):
        all_equal.compare(x, y, round_=True, close=True)
