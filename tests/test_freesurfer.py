import os
import pytest
import subprocess
import tempfile


@pytest.fixture()
def tmpfile():
    fid, fname = tempfile.mkstemp()
    os.close(fid)
    yield fname
    os.remove(fname)


def test_combine_stats_cmd(tmpfile):
    inputs = [os.path.join(os.path.dirname(__file__), file_)
              for file_ in ['aparc_area_lh_small.txt',
                            'aseg_mean_small.txt',
                            'aseg_volume_small.txt']
              ]
    truth = os.path.join(os.path.dirname(__file__), 'fsstats_small_out.txt')
    subprocess.check_call(['fscombine'] + inputs + [tmpfile])
    subprocess.check_call(['cmp', tmpfile, truth])
