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


def _run(fnames, tmpfile, should_pass=True):
    inputs = [os.path.join(os.path.dirname(__file__), file_)
              for file_ in fnames]
    truth = os.path.join(os.path.dirname(__file__), 'fsstats_small_out.txt')
    out = subprocess.run(['fscombine'] + inputs + [tmpfile])
    if should_pass:
        out = subprocess.run(['cmp', tmpfile, truth])
        assert out.returncode == 0
    else:
        assert out.returncode != 0


def test_combine_stats_cmd(tmpfile):
    _run(['aparc_area_lh_small.txt',
          'testdup.txt',
          'aseg_mean_small.txt',
          'aseg_volume_small.txt'],
         tmpfile)


def test_combine_stats_cmd2(tmpfile):
    _run(['aparc_area_lh_small.txt',
          'testdup2.txt',
          'aseg_mean_small.txt',
          'aseg_volume_small.txt'],
         tmpfile)


def test_combine_stats_cmd_fail(tmpfile):
    _run(['aparc_area_lh_small.txt',
          'testdup_f1.txt',
          'aseg_mean_small.txt',
          'aseg_volume_small.txt'],
         tmpfile,
         should_pass=False)


def test_combine_stats_cmd_fail2(tmpfile):
    _run(['aparc_area_lh_small.txt',
          'testdup_f2.txt',
          'aseg_mean_small.txt',
          'aseg_volume_small.txt'],
         tmpfile,
         should_pass=False)


def test_combine_stats_cmd_fail3(tmpfile):
    _run(['aparc_area_lh_small.txt',
          'testdup_f3.txt',
          'aseg_mean_small.txt',
          'aseg_volume_small.txt'],
         tmpfile,
         should_pass=False)
