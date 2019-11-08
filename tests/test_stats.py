import numpy as np
import nibabel
import subprocess
from pndni.stats import stats, std


def wrap(basecmd, inputfile, statslist, maskfile=None):
    cmd = [basecmd]
    if maskfile is not None:
        cmd.append('-K')
        cmd.append(maskfile)
    cmd.append(inputfile)
    cmd.extend(statslist)
    out = subprocess.check_output(cmd).decode().split()
    return [float(o) for o in out]


def statswrap(inputfile, statslist, maskfile=None):
    return wrap('stats', inputfile, statslist, maskfile=maskfile)


def fslstats(inputfile, statslist, maskfile=None):
    return wrap('fslstats', inputfile, statslist, maskfile=maskfile)


def test(tmp_path):

    inputfile = str(tmp_path / 'in.nii')
    maskfile = str(tmp_path / 'out.nii')
    input = np.arange(3 * 4 * 5).reshape(3, 4, 5).astype(np.float)
    mask = np.zeros(input.shape, dtype=np.int)
    mask[:2, 0, -1] = 1
    mask[1, 1:3, 1:3] = 2
    mask[2, 1, 1] = 4
    assert tuple(np.unique(mask)) == (0, 1, 2, 4)
    nibabel.Nifti1Image(input, np.eye(4)).to_filename(inputfile)
    nibabel.Nifti1Image(mask, np.eye(4)).to_filename(maskfile)
    statsmap = {'-m': np.mean, '-s': std}

    for m in [None, maskfile]:
        for statslist in [['-m'], ['-s'], ['-m', '-s'], ['-s', '-m']]:
            truth = fslstats(inputfile, statslist, m)
            cmd = statswrap(inputfile, statslist, m)
            py = stats(inputfile, [statsmap[stat] for stat in statslist], K=m)
            assert np.allclose(truth, py)
            assert np.allclose(truth, cmd)
