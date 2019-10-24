import h5py
import pytest
import numpy as np
import nibabel
import subprocess
from pndni import minc_default_dircos

LENGTH = {'xspace': 10, 'yspace': 11, 'zspace': 12}
STEP = {'xspace': 1.0, 'yspace': 2.0, 'zspace': 3.0}
DIRCOS = {
    'xspace': np.array([1.0, 0.0, 0.0]),
    'yspace': np.array([0.0, 1.0, 0.0]),
    'zspace': np.array([0.0, 0.0, 1.0])
}
SQRT2 = np.sqrt(2)
DIRCOSROT = {
    'xspace': np.array([SQRT2, SQRT2, 0.0]),
    'yspace': np.array([-SQRT2, SQRT2, 0.0]),
    'zspace': np.array([0.0, 0.0, 1.0])
}
DATA = np.arange(10 * 11 * 12).astype(np.float).reshape((12, 11, 10))


def _simple_minc(fname,
                 irregular=False,
                 dircos=True,
                 dircosrotate=False,
                 nodim=False):
    with h5py.File(fname, 'w') as f:
        root = f.create_group('minc-2.0')
        dim = root.create_group('dimensions')
        if not nodim:
            for d in ['xspace', 'yspace', 'zspace']:
                if irregular:
                    grp = dim.create_dataset(d, data=np.arange(LENGTH[d]))
                    grp.attrs['spacing'] = b'irregular'
                else:
                    grp = dim.create_dataset(d, shape=())
                    grp.attrs['step'] = STEP[d]
                    grp.attrs['spacing'] = b'regular__'
                grp.attrs['length'] = LENGTH[d]
                if dircos:
                    if dircosrotate:
                        grp.attrs['direction_cosines'] = DIRCOSROT[d]
                    else:
                        grp.attrs['direction_cosines'] = DIRCOS[d]
                grp.attrs['dimorder'] = b'zspace,yspace,xspace'
                grp.attrs['vartype'] = b'dimension____'
                grp.attrs['varid'] = b'MINC standard variable'
                grp.attrs['version'] = b'MINC Version 1.0'
        img = root.create_dataset('image/0/image', data=DATA)
        img.attrs['complete'] = True
        img.attrs['valid_range'] = np.array([0.0, np.max(DATA)])
        img.attrs['dimorder'] = b'zspace,yspace,xspace'
        img.attrs['vartype'] = b'group________'
        img.attrs['varid'] = b'MINC standard variable'
        img.attrs['version'] = b'MINC Version 1.0'
        imgmin = root.create_dataset('image/0/image-min', data=np.array(0))
        imgmin.attrs['vartype'] = b'var_attribute'
        imgmin.attrs['varid'] = b'MINC standard variable'
        imgmin.attrs['version'] = b'MINC Version 1.0'
        imgmax = root.create_dataset('image/0/image-max', data=np.max(DATA))
        imgmax.attrs['vartype'] = b'var_attribute'
        imgmax.attrs['varid'] = b'MINC standard variable'
        imgmax.attrs['version'] = b'MINC Version 1.0'


@pytest.mark.parametrize('dircos,dircosrot',
                         [[False, False], [True, False], [True, True]])
def test_simple_minc(tmp_path, dircos, dircosrot):
    fname = tmp_path / 'out.mnc'
    _simple_minc(fname, dircos=dircos, dircosrotate=dircosrot)
    x = nibabel.load(str(fname))
    assert np.all(x.get_fdata() == DATA)
    if dircosrot:
        aff = np.array([[0.0, -SQRT2 * 2.0, SQRT2,
                         0.0], [0.0, SQRT2 * 2.0, SQRT2, 0.0],
                        [3.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0]])
    else:
        aff = np.array([[0.0, 0.0, 1.0, 0.0], [0.0, 2.0, 0.0, 0.0],
                        [3.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0]])
    assert np.all(x.affine == aff)


@pytest.mark.parametrize(
    'dircos,dircosrot,irregular,nodim',
    [[False, False, False, False], [True, False, False, False], [
        True, True, False, False
    ], [False, False, False, True], [True, False, True, False]])
def test_minc_default_dircose(tmp_path, dircos, dircosrot, irregular, nodim):
    fname = tmp_path / 'in.mnc'
    _simple_minc(fname,
                 dircos=dircos,
                 dircosrotate=dircosrot,
                 irregular=irregular,
                 nodim=nodim)
    if irregular or nodim:
        with pytest.raises(RuntimeError):
            minc_default_dircos.update_direction_cosines(fname)
        return
    else:
        minc_default_dircos.update_direction_cosines(fname)
    with h5py.File(fname, 'r') as f:
        if dircosrot:
            truth = DIRCOSROT
        else:
            truth = DIRCOS
        for d in ['xspace', 'yspace', 'zspace']:
            assert np.all(f[f'/minc-2.0/dimensions']
                          [d].attrs['direction_cosines'] == truth[d])


@pytest.mark.parametrize('dircos,dircosrot',
                         [[False, False], [True, False], [True, True]])
def test_minc_default_dircose_cmd(tmp_path, dircos, dircosrot):
    fname = tmp_path / 'in.mnc'
    out = tmp_path / 'out.mnc'
    _simple_minc(fname, dircos=dircos, dircosrotate=dircosrot)
    subprocess.check_call(['minc_default_dircos', str(fname), str(out)])
    with h5py.File(out, 'r') as f:
        if dircosrot:
            truth = DIRCOSROT
        else:
            truth = DIRCOS
        for d in ['xspace', 'yspace', 'zspace']:
            assert np.all(f['/minc-2.0/dimensions']
                          [d].attrs['direction_cosines'] == truth[d])
