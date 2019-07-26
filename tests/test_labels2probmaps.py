from itertools import product
import subprocess
import nibabel
import numpy as np


def _wrapper(tmpdir, labels, label_names, label_names_out, bids_labels=False):
    fnames = []
    for i, l in enumerate(labels):
        fnames.append(str(tmpdir / f'l{i}.nii'))
        nibabel.Nifti1Image(np.atleast_3d(l), None).to_filename(fnames[-1])
    outtemplate = str(tmpdir / 'out_{label}.nii')
    subprocess.check_call(['labels2probmaps', outtemplate] + fnames + (['--bids_labels'] if bids_labels else []) + ['--labels'] +
                          [str(ln) for ln in label_names])
    outlist = []
    for l in label_names_out:
        out = nibabel.load(outtemplate.format(label=l))
        outlist.append(out.get_fdata().ravel())
    return outlist

        
def test_combinelabels1(tmpdir):
    l1 = np.array([1, 2, 3, 1, 2, 3])
    l2 = np.array([1, 1, 1, 2, 2, 2])
    outlist = _wrapper(tmpdir, [l1, l2], [1, 2, 3], [1, 2, 3])
    assert np.all(outlist[0] == [1, 0.5, 0.5, 0.5, 0, 0])
    assert np.all(outlist[1] == [0, 0.5, 0, 0.5, 1, 0.5])
    assert np.all(outlist[2] == [0, 0, 0.5, 0, 0, 0.5])

        
def test_combinelabels2(tmpdir):
    l1 = np.array([1, 2, 3, 1, 2, 3])
    l2 = np.array([1, 1, 1, 2, 2, 2])
    outlist = _wrapper(tmpdir, [l1, l2], [1, 2, 3], ['GM', 'WM', 'CSF'], bids_labels=True)
    assert np.all(outlist[0] == [1, 0.5, 0.5, 0.5, 0, 0])
    assert np.all(outlist[1] == [0, 0.5, 0, 0.5, 1, 0.5])
    assert np.all(outlist[2] == [0, 0, 0.5, 0, 0, 0.5])

        
def test_combinelabels3(tmpdir):
    l1 = np.array([1, 2, 3, 1, 2, 3])
    l2 = np.array([1, 1, 1, 2, 2, 2])
    l3 = np.array([1, 0, 1, 0, 1, 3])
    outlist = _wrapper(tmpdir, [l1, l2, l3], [1, 2, 3], [1, 2, 3])
    assert np.all(outlist[0] == [1, 1/3, 2/3, 1/3, 1/3, 0])
    assert np.all(outlist[1] == [0, 1/3, 0, 1/3, 2/3, 1/3])
    assert np.all(outlist[2] == [0, 0, 1/3, 0, 0, 2/3])

        
def test_combinelabels4(tmpdir):
    l1 = np.array([1, 2, 3, 1, 2, 3])
    l2 = np.array([1, 1, 1, 2, 2, 2])
    outlist = _wrapper(tmpdir, [l1, l2], [2], ['WM'], bids_labels=True)
    assert np.all(outlist[0] == [0, 0.5, 0, 0.5, 1, 0.5])

        
def test_combinelabels5(tmpdir):
    l1 = np.array([1, 2, 3, 1, 2, 3])
    l2 = np.array([1, 1, 1, 2, 2, 2])
    l3 = np.array([1, 0, 1, 0, 1, 3])
    outlist = _wrapper(tmpdir, [l1, l2, l3], [1, 3], [1, 3])
    assert np.all(outlist[0] == [1, 1/3, 2/3, 1/3, 1/3, 0])
    assert np.all(outlist[1] == [0, 0, 1/3, 0, 0, 2/3])
