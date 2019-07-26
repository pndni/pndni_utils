import numpy as np
import nibabel


def copy_forms(tmp, out):
    aff, code = tmp.get_qform(coded=True)
    out.set_qform(aff, code=code)
    aff, code = tmp.get_sform(coded=True)
    out.set_sform(aff, code=code)


def safeintload(file_):
    x = np.asarray(nibabel.load(file_).dataobj)
    xc = x.astype('uint32', copy=False)
    if xc is not x:
        if not np.all(x == xc):
            raise ValueError('input image contained non integer values or values < 0')
    return xc
