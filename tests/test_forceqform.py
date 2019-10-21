from pndni import forceqform
import nibabel
import numpy as np
import pytest


@pytest.mark.parametrize('testtype', ['qform', 'sform', 'both', 'none'])
def test_forceqform(tmp_path, testtype):
    i1 = tmp_path / 'image1.nii'
    affine = np.array([[1.0, 0.0, 0.0, -20.0],
                       [0.0, 2.0, 0.0, -30.0],
                       [0.0, 0.0, 4.0, -40.0],
                       [0.0, 0.0, 0.0, 1.0]])
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
    args = parser.parse_args([str(i1), str(tmp_path / 'out.nii')])
    if testtype != 'none':
        forceqform.forceqform(args.input_file, args.output_file)
    else:
        with pytest.raises(RuntimeError):
            forceqform.forceqform(args.input_file, args.output_file)
        return
    nout = nibabel.load(str(args.output_file))
    assert np.all(nout.affine == affine)
    assert np.all(nout.get_qform() == affine)
    assert nout.get_sform(coded=True)[1] == 0
