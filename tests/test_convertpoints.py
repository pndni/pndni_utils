import pytest
import csv
from pndni.convertpoints import Points, SinglePoint
import subprocess


def cmp(f1, f2):
    with open(f1, 'r', newline='') as i1, open(f2, 'r', newline='') as i2:
        return i1.read() == i2.read()


@pytest.fixture
def points_path(tmp_path):
    (tmp_path / 'mni.tag').write_text("""MNI Tag Point File
Volumes = 1;
Points =
 1.1 1.2 1.3 0 -1 -1 "10"
 2.1 2.2 2.3 0 -1 -1 "20";
""")
    with open(tmp_path / 'ants.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['x', 'y', 'z', 'index', 't'])
        writer.writerow([-1.1, -1.2, 1.3, 10, 0.0])
        writer.writerow([-2.1, -2.2, 2.3, 20, 0.0])

    with open(tmp_path / 'simple.tsv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['x', 'y', 'z', 'index'])
        writer.writerow([1.1, 1.2, 1.3, 10, 0.0])
        writer.writerow([2.1, 2.2, 2.3, 20, 0.0])
    with open(tmp_path / 'slicer.fcsv', 'w', newline='') as f:
        f.write('# Markups fiducial file version = 4.10.2\n')
        f.write('# CoordinateSystem = 0\n')
        f.write('# columns = id,x,y,z,label\n')
        writer = csv.writer(f)
        writer.writerow([0, 1.1, 1.2, 1.3, 10])
        writer.writerow([1, 2.1, 2.2, 2.3, 20])
    return tmp_path


def test_Points_read(points_path):
    tsv = Points.from_tsv(points_path / 'simple.tsv')
    tsv2 = Points.from_file(points_path / 'simple.tsv')
    ants = Points.from_ants_csv(points_path / 'ants.csv')
    ants2 = Points.from_file(points_path / 'ants.csv')
    minc = Points.from_minc_tag(points_path / 'mni.tag')
    minc2 = Points.from_file(points_path / 'mni.tag')
    fcsv = Points.from_fcsv(points_path / 'slicer.fcsv')
    fcsv2 = Points.from_file(points_path / 'slicer.fcsv')
    assert tsv == ants == minc == tsv2 == ants2 == minc2 == fcsv == fcsv2


def test_Points_write(points_path):
    p = Points([SinglePoint(1.1, 1.2, 1.3, 10),
                SinglePoint(2.1, 2.2, 2.3, 20)])
    p.to_ants_csv(points_path / 'out_ants.csv')
    assert cmp(points_path / 'ants.csv', points_path / 'out_ants.csv')
    p.to_minc_tag(points_path / 'out_mni.tag')
    assert cmp(points_path / 'mni.tag', points_path / 'out_mni.tag')
    p.to_file(points_path / 'out_ants.csv')
    assert cmp(points_path / 'ants.csv', points_path / 'out_ants.csv')
    p.to_file(points_path / 'out_mni.tag')
    assert cmp(points_path / 'mni.tag', points_path / 'out_mni.tag')
    p.to_fcsv(points_path / 'out_slicer.fcsv')
    assert cmp(points_path / 'slicer.fcsv', points_path / 'out_slicer.fcsv')


def test_convert(points_path):
    for infile in ['ants.csv', 'mni.tag', 'simple.tsv', 'slicer.fcsv']:
        for truefile in ['ants.csv', 'mni.tag', 'slicer.fcsv']:
            outfile = 'out_' + truefile
            subprocess.check_call(['convertpoints', str(points_path / infile), str(points_path / outfile)])
            assert cmp(points_path / outfile, points_path / truefile)
