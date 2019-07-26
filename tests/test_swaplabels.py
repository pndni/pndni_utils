import subprocess
import nibabel
import numpy as np


def wrapper(x, mapping, tmpdir):
    inname = str(tmpdir / 'in.nii')
    outname = str(tmpdir / 'out.nii')
    mapstr = ', '.join(f'{key}: {val}' for key, val in mapping.items())
    nibabel.Nifti1Image(np.atleast_3d(x), None).to_filename(inname)
    subprocess.check_call(['swaplabels', mapstr, inname, outname])
    out = nibabel.load(outname)
    return np.asarray(out.dataobj).ravel()


def test_swaplabels1(tmpdir):
    x = np.array([0, 1, 2, 3, 4])
    m = {1: 2, 2: 5}
    truth = np.array([0, 2, 5, 0, 0])
    out = wrapper(x, m, tmpdir)
    assert np.all(out == truth)


def test_swaplabels2(tmpdir):
    x = np.array([0, 1, 2, 3, 4], dtype=np.uint8)
    m = {1: 2, 2: 500}
    truth = np.array([0, 2, 500, 0, 0])
    out = wrapper(x, m, tmpdir)
    assert np.all(out == truth)
    assert out.dtype == np.uint16
