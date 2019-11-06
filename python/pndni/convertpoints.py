import argparse
import csv
from collections import namedtuple
import re
import os


SinglePoint = namedtuple('SinglePoint', ['x', 'y', 'z', 'index'])


class Points(object):
    _FCSV_HEADER = ['# Markups fiducial file version = 4.10.2',
                    '# CoordinateSystem = 0',  # RAS
                    '# columns = id,x,y,z,label']

    def __init__(self, points):
        """points is a list or tuple of SinglePoints"""
        self.points = tuple(points)

    @classmethod
    def from_file(cls, infile):
        """Initialize points from file, choosing the format based on the extension"""
        ext = os.path.splitext(infile)[1]
        if ext == '.tsv':
            return cls.from_tsv(infile)
        elif ext == '.csv':
            return cls.from_ants_csv(infile)
        elif ext == '.tag':
            return cls.from_minc_tag(infile)
        elif ext == '.fcsv':
            return cls.from_fcsv(infile)
        else:
            raise RuntimeError('Unsupported file type')

    def to_file(self, outfile):
        """Write to file, choosing the type based on the extension"""
        ext = os.path.splitext(outfile)[1]
        if ext == '.tsv':
            return self.to_tsv(outfile)
        elif ext == '.csv':
            return self.to_ants_csv(outfile)
        elif ext == '.tag':
            return self.to_minc_tag(outfile)
        elif ext == '.fcsv':
            return self.to_fcsv(outfile)
        else:
            raise RuntimeError('Unsupported file type')

    def to_fcsv(self, outfile):
        """Write data to a Slicer fidicial file
        https://www.slicer.org/wiki/Documentation/Nightly/Modules/Markups#Load_From_File
        """
        with open(outfile, 'w', newline='') as f:
            f.write('\n'.join(self._FCSV_HEADER) + '\n')
            writer = csv.writer(f)
            for i, point in enumerate(self.points):
                writer.writerow([i, point.x, point.y, point.z, point.index])

    @classmethod
    def from_fcsv(cls, infile):
        with open(infile, 'r', newline='') as f:
            l1 = f.readline().strip()
            if l1.split('=')[0] != cls._FCSV_HEADER[0].split('=')[0]:
                raise RuntimeError('First line of fcsv must be slicer version line')
            for i in [1, 2]:
                lt = f.readline().strip()
                if lt != cls._FCSV_HEADER[i]:
                    raise RuntimeError(f'Line {i + 1} of fcsv must be {cls._FCSV_HEADER[i]}')
            reader = csv.reader(f)
            points = [SinglePoint(float(row[1]),
                                  float(row[2]),
                                  float(row[3]),
                                  int(row[4]))
                      for row in reader]
            return cls(points)

    def to_tsv(self, outfile):
        """Write the data to a TSV file"""
        with open(outfile, 'w', newline='') as f:
            writer = csv.DictWriter(f, delimiter='\t', fieldnames=SinglePoint._fields)
            writer.writeheader()
            for point in self.points:
                writer.writerow(point._asdict())

    @classmethod
    def from_tsv(cls, infile):
        """Initialize Points object from a TSV file with "x", "y", "z", and "index"
        columns (of types float, float, float, and int, respectively). All other
        columns will be ignored"""
        with open(infile, 'r', newline='') as f:
            reader = csv.DictReader(f, delimiter='\t')
            points = [SinglePoint(float(row['x']),
                                  float(row['y']),
                                  float(row['z']),
                                  int(row['index']))
                      for row in reader]
        return cls(points)

    def to_ants_csv(self, outfile):
        """Write an ANTS style CSV file. The t column is set to 0.0.
        The x and y columns will be multiplied by -1.0
        (ants uses LPS while this class uses RAS).
        """
        with open(outfile, 'w', newline='') as f:
            writer = csv.DictWriter(f, delimiter=',', fieldnames=list(SinglePoint._fields) + ['t'])
            writer.writeheader()
            for point in self.points:
                writer.writerow({'x': -1.0 * point.x,
                                 'y': -1.0 * point.y,
                                 'z': point.z,
                                 'index': point.index,
                                 't': 0.0})

    @classmethod
    def from_ants_csv(cls, infile):
        """Initialize Points object from a CSV file with "x", "y", "z", and "index"
        columns (of types float, float, float, and int, respectively). All other
        columns will be ignored. The x and y columns will be multiplied by -1.0
        (ants uses LPS while this class uses RAS)."""
        with open(infile, 'r', newline='') as f:
            reader = csv.DictReader(f, delimiter=',')
            points = []
            for row in reader:
                points.append(SinglePoint(-1.0 * float(row['x']),
                                          -1.0 * float(row['y']),
                                          float(row['z']),
                                          int(row['index'])))
        return cls(points)

    def to_minc_tag(self, outfile):
        """Write a
        '`minc tag file <https://en.wikibooks.org/wiki/MINC/SoftwareDevelopment/Tag_file_format_reference>`_'.
        the weight, structure ID, and patient ID are set to 0, -1, and -1, respectively"""
        with open(outfile, 'w') as f:
            f.write('MNI Tag Point File\nVolumes = 1;\nPoints =')
            for i, point in enumerate(self.points):
                f.write(f'\n {point.x} {point.y} {point.z} 0 -1 -1 "{point.index}"')
            f.write(';\n')

    @classmethod
    def from_minc_tag(cls, infile):
        """Initialize Points object from a
        '`minc tag file <https://en.wikibooks.org/wiki/MINC/SoftwareDevelopment/Tag_file_format_reference>`_'.
        In this case, we assume each point has 7 parameters, and that the text label is quoted. Therefore
        it is more restrictive than the linked specification. All information besides x, y, z, and label
        are ignored.
        """
        points = []
        with open(infile, 'r') as f:
            contents = f.read()
            # remove comments
            contents = re.sub('[#%][^\n]*\n', '\n', contents)
            match = re.match(r'MNI Tag Point File\n+Volumes = [12];\n+\s*Points =([^;]*);', contents)
            pointsstr = match.group(1)
            pointssplit = pointsstr.split()
            npoints = len(pointssplit) // 7
            if npoints != len(pointssplit) / 7.0:
                raise RuntimeError('MNI Tags file must have 7 fields per point')
            for i in range(npoints):
                row = pointssplit[i * 7:(i + 1) * 7]
                index = row[6]
                if index[0] != '"' or index[-1] != '"':
                    raise RuntimeError("index must be surrounded by quotes")
                index = index[1:-1]
                points.append(SinglePoint(float(row[0]),
                                          float(row[1]),
                                          float(row[2]),
                                          int(index)))
        return cls(points)

    def __len__(self):
        return len(self.points)

    def __eq__(self, other):
        return len(self) == len(other) and self.points == other.points


def get_parser():
    parser = argparse.ArgumentParser(prog='convertpoints',
                                     description='Convert a points file to a different format')
    parser.add_argument('infile', type=str,
                        help="""Input file. Format determined by extension. May be

a TSV file with (extension .tsv) "x", "y", "z", and "index"
columns (of types float, float, float, and int, respectively). All other
columns will be ignored. Coordinates are in RAS.

A CSV file (extension .csv) with "x", "y", "z", and "index"
columns (of types float, float, float, and int, respectively). All other
columns will be ignored. Coordinates are in LPS.

A `minc tag file <https://en.wikibooks.org/wiki/MINC/SoftwareDevelopment/Tag_file_format_reference>`_ (extension .tag).
In this case, we assume each point has 7 parameters, and that the text label is quoted. Therefore
it is more restrictive than the linked specification. All information besides x, y, z, and label
are ignored. Coordinates are in RAS.

A `slicer fiducial file <https://www.slicer.org/wiki/Documentation/Nightly/Modules/Markups#File_Format>`_ (extension .fcsv')
Containing only the columns id, x, y, z, label (int, float, float, float, and int, respectively). Id is ignored.
Coordinates are in RAS.
                        """)
    parser.add_argument('outfile', type=str,
                        help='Output file. Format determined by extension. See infile.')
    return parser


def main():
    args = get_parser().parse_args()
    Points.from_file(args.infile).to_file(args.outfile)


if __name__ == '__main__':
    main()
