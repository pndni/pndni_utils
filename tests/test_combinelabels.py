from itertools import product
import subprocess
import nibabel
import numpy as np


def _wrapper(tmpdir, labels):
    fnames = []
    for i, l in enumerate(labels):
        fnames.append(str(tmpdir / f'l{i}.nii'))
        nibabel.Nifti1Image(np.atleast_3d(l), None).to_filename(fnames[-1])
    outname = str(tmpdir / 'out.nii')
    subprocess.check_call(['combinelabels', outname] + fnames)
    out = nibabel.load(outname)
    return np.asarray(out.dataobj).ravel()

        
def test_combinelabels1(tmpdir):
    l1 = np.array([1, 2, 3, 1, 2, 3])
    l2 = np.array([1, 1, 1, 2, 2, 2])
    out = _wrapper(tmpdir, [l1, l2])
    assert np.all(out == [1, 2, 3, 4, 5, 6])
    assert out.dtype == 'uint8'

        
def test_combinelabels2(tmpdir):
    l1 = np.array([1, 2, 0, 1, 2, 3])
    l2 = np.array([1, 1, 1, 2, 0, 2])
    out = _wrapper(tmpdir, [l1, l2])
    assert np.all(out == [1, 2, 0, 4, 0, 6])
    assert out.dtype == 'uint8'

        
def test_combinelabels3(tmpdir):
    l1 = np.array([1, 2, 3, 1, 2, 3])
    l2 = np.array([1, 1, 1, 2, 2, 2])
    l3 = np.array([4, 5, 4, 5, 4, 4])
    out = _wrapper(tmpdir, [l1, l2, l3])
    assert np.all(out == [19, 26, 21, 28, 23, 24])
    assert out.dtype == 'uint8'


def test_combinelabels4(tmpdir):
    l1 = np.arange(10)
    l2 = np.arange(10)
    l3 = np.arange(10)
    out = _wrapper(tmpdir, [l1, l2, l3])
    truth = l1 + (l2 - 1) * 9 + (l3 - 1) * 81
    truth *= l1 > 0
    truth *= l2 > 0
    truth *= l3 > 0
    assert np.all(out == truth)
    assert out.dtype == 'uint16'

        
def test_combinelabels5(tmpdir):
    l1 = np.array([1, 2, 3, 1, 2, 3])
    l2 = np.array([1, 1, 1, 2, 2, 2])
    l3 = np.array([4, 5, 4, 5, 4, 4])
    out = _wrapper(tmpdir, [l1, l2])
    out2 = _wrapper(tmpdir, [out, l3])
    assert np.all(out2 == [19, 26, 21, 28, 23, 24])
    assert out2.dtype == 'uint8'
