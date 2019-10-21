import argparse
import nibabel
from pathlib import Path


def get_parser():
    parser = argparse.ArgumentParser(
        description=main.__doc__
        )
    parser.add_argument('input_file', type=Path,
                        help='Input file')
    parser.add_argument('output_file', type=Path,
                        help='Output file')
    return parser


def main(input_file, output_file):
    """
    Ensure that only qform is set. Because ANTs only uses the qform, this will
    force other applications to use the qform as well, keeping everything consistent.

    * If the qform code is > 0 and the sform code is 0, change nothing.
    * If both codes are > 0, set the sform code to 0
    * if the qform is 0 and the sform code is > 0, set the qform based on the
      affine matrix as determined by nibabel (which will be based on the sform),
      and set sform code to 0. The function :py:func:`set_sform` from :py:mod:`nibabel`
      is used, with the strip_shears option set to False.
    * If both codes are 0, raise a RuntimeError
    """
    img = nibabel.load(str(input_file))
    qcode = img.get_qform(coded=True)[1]
    scode = img.get_sform(coded=True)[1]
    if qcode > 0 and scode == 0:
        # already the way we want it
        pass
    elif qcode > 0 and scode > 0:
        img.set_sform(None)
    elif qcode == 0 and scode > 0:
        img.set_qform(img.affine, code=scode, strip_shears=False)
        img.set_sform(None)
    else:
        raise RuntimeError('Neither sform and qform set')
    img.to_filename(str(output_file))


if __name__ == '__main__':
    args = get_parser().parse_args()
    main(args.input_file, args.output_file)
