from pndni import forceqform
import nibabel
import numpy as np
import pytest


def test_ang():
    x = np.array([1.0, 0.0, 0.0])
    y = np.array([0.0, 2.0, 0.0])
    z = np.array([0.0, 0.0, 3.0])
    for i in [x, y, z]:
        for j in [x, y, z]:
            if i is j:
                assert np.allclose(forceqform._ang(i, j), np.pi / 2)
            else:
                assert np.allclose(forceqform._ang(i, j), 0)


def test_check_ang():
    R1 = np.array([[1.0, -2.0, 0.0],
                   [1.0, 2.0, 0.0],
                   [0.0, 0.0, 3.0]])
    forceqform._check_ang(R1, 1e-6)
    R2 = np.array([[1.0, 0.0, 0.0],
                   [1.0, 2.0, 0.0],
                   [0.0, 0.0, 3.0]])
    with pytest.raises(RuntimeError):
        forceqform._check_ang(R2, 1e-6)
    with pytest.raises(RuntimeError):
        forceqform._check_ang(R2, np.pi / 4 - 0.01)
    forceqform._check_ang(R2, np.pi / 4 + 0.01)


@pytest.mark.parametrize('testtype,shear,maxang', [('qform', False, None),
                                                   ('sform', False, None),
                                                   ('both', False, None),
                                                   ('none', False, None),
                                                   ('sform', True, None),
                                                   ('sform', True, np.pi)])
def test_forceqform(tmp_path, testtype, shear, maxang):
    i1 = tmp_path / 'image1.nii'
    affine = np.array([[1.0, 0.0, 0.0, -20.0],
                       [0.0, 2.0, 0.0, -30.0],
                       [0.0, 0.0, 4.0, -40.0],
                       [0.0, 0.0, 0.0, 1.0]])
    if shear:
        affine[0, 2] = 2.0
    img = np.arange(24).reshape(2, 3, 4)
    nii = nibabel.Nifti1Image(img, None)

    if testtype == 'qform':
        nii.set_qform(affine)
    elif testtype == 'sform':
        nii.set_sform(affine)
    elif testtype == 'both':
        nii.set_qform(affine)
        nii.set_sform(affine * 2)
    elif testtype == 'none':
        pass
    else:
        raise RuntimeError()
    nii.to_filename(str(i1))
    parser = forceqform.get_parser()
    toparse = [str(i1), str(tmp_path / 'out.nii')]
    if maxang is not None:
        toparse.extend(['--maxangle', str(maxang)])
    args = parser.parse_args(toparse)
    if testtype != 'none' and not (shear and maxang is None):
        forceqform.forceqform(args.input_file, args.output_file, maxangle=args.maxangle)
    else:
        with pytest.raises(RuntimeError):
            forceqform.forceqform(args.input_file, args.output_file, maxangle=args.maxangle)
        return
    nout = nibabel.load(str(args.output_file))
    if maxang is None:
        assert np.all(nout.affine == affine)
        assert np.all(nout.get_qform() == affine)
    assert nout.get_sform(coded=True)[1] == 0
