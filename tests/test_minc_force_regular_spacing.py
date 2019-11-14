import h5py
import netCDF4
import numpy as np
import subprocess
import pytest
import shutil
from pndni import minc_force_regular_spacing


LENGTH = {'xspace': 10, 'yspace': 11, 'zspace': 12}
STEP = {'xspace': 1.0, 'yspace': 2.0, 'zspace': 3.0}
DATA = np.arange(10 * 11 * 12).astype(np.float).reshape((12, 11, 10))


def _simple_minc2(fname, irregular, err):
    with h5py.File(fname, 'w') as f:
        root = f.create_group('minc-2.0')
        dim = root.create_group('dimensions')
        for d in ['xspace', 'yspace', 'zspace']:
            if irregular:
                data = np.arange(LENGTH[d]).astype(np.float) * STEP[d]
                data[1] += err[d]
                grp = dim.create_dataset(d, data=data)
                grp.attrs['spacing'] = b'irregular'
            else:
                grp = dim.create_dataset(d, shape=())
                grp.attrs['spacing'] = b'regular__'
            grp.attrs['step'] = STEP[d]
            grp.attrs['length'] = LENGTH[d]
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


def _simple_minc1(fname, irregular, err):
    with netCDF4.Dataset(fname, 'w') as root:
        for d in ['xspace', 'yspace', 'zspace']:
            root.createDimension(d, LENGTH[d])
            dim = root.createVariable(d, 'f8', (d,))
            if irregular:
                dim[:] = np.arange(LENGTH[d]).astype(np.float) * STEP[d]
                dim[1] += err[d]
                dim.spacing = 'irregular'
            else:
                dim.spacing = 'regular__'
            dim.step = STEP[d]
            dim.length = LENGTH[d]
            dim.vartype = 'dimension____'
            dim.varid = 'MINC standard variable'
            dim.signtype = 'signed__'
            dim.version = 'MINC Version    1.0'
        img = root.createVariable('image', 'f8', ('zspace', 'yspace', 'xspace'))
        img[:] = DATA
        img.vartype = 'group________'
        img.varid = 'MINC standard variable'
        img.parent = ''
        img.children = ''
        img.signtype = 'signed__'
        img.version = 'MINC Version    1.0'
        img.complete = 'true_'
        setattr(img, 'image-max', '--->image-max')
        setattr(img, 'image-min', '--->image-min')
        mx = root.createVariable('image-max', 'f8', ('zspace',))
        mx.vartype = 'var_attribute'
        mx.varid = 'MINC standard variable'
        mx.parent = 'image'
        mx.children = ''
        mx.signtype = 'signed__'
        mx.version = 'MINC Version    1.0'
        mx[:] = np.max(DATA)
        mx = root.createVariable('image-min', 'f8', ('zspace',))
        mx.vartype = 'var_attribute'
        mx.varid = 'MINC standard variable'
        mx.parent = 'image'
        mx.children = ''
        mx.signtype = 'signed__'
        mx.version = 'MINC Version    1.0'
        mx[:] = np.min(DATA)


def _func_wrapper(infile, outfile, atol=1e-8, rtol=1e-5):
    shutil.copyfile(infile, outfile)
    return minc_force_regular_spacing.force_regular_spacing(outfile, atol, rtol)


def _cmd_wrapper(infile, outfile, atol=None, rtol=None):
    cmd = ['minc_force_regular_spacing', infile, outfile]
    if atol:
        cmd.extend(['--atol', str(atol)])
    if rtol:
        cmd.extend(['--rtol', str(rtol)])
    subprocess.check_call(cmd)


@pytest.mark.parametrize('exectype', ['func', 'cmd'])
@pytest.mark.parametrize('ver', [1, 2])
@pytest.mark.parametrize('err', [0, 1e-3])
@pytest.mark.parametrize('errdim', ['xspace', 'yspace', 'zspace'])
def test(tmp_path, exectype, ver, err, errdim):
    if exectype == 'func':
        executor = _func_wrapper
    else:
        executor = _cmd_wrapper
    fname = tmp_path / 'in.mnc'
    out = tmp_path / 'out.mnc'
    errdict = {'xspace': 0, 'yspace': 0, 'zspace': 0}
    errdict[errdim] = err
    if ver == 1:
        _simple_minc1(fname, True, errdict)
    else:
        _simple_minc2(fname, True, errdict)
    if err > 0:
        if exectype == 'func':
            with pytest.raises(RuntimeError):
                executor(str(fname), str(out), atol=err / 2.0, rtol=0)
        else:
            with pytest.raises(subprocess.SubprocessError):
                executor(str(fname), str(out), atol=err / 2.0, rtol=0)
        executor(str(fname), str(out), atol=err + 1e-2, rtol=0)
    else:
        executor(str(fname), str(out))
    if ver == 1:
        with netCDF4.Dataset(str(out), 'r') as f:
            for dim in ['xspace', 'yspace', 'zspace']:
                assert f[dim].spacing == 'regular__'
    else:
        with h5py.File(str(out), 'r') as f:
            for dim in ['/minc-2.0/dimensions/xspace', '/minc-2.0/dimensions/yspace', '/minc-2.0/dimensions/zspace']:
                assert f[dim].attrs['spacing'] == b'regular__'
