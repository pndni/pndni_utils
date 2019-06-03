import argparse
import pandas as pd
from pathlib import Path


def combine_stats(inputs):
    df = None
    for d in inputs:
        dft = pd.read_csv(str(d), sep='\t', float_precision='round-trip')
        orig_first_col = dft.columns[0]
        dft = dft.rename(columns={orig_first_col: 'ID'})
        dft = dft.set_index('ID')

        # the aseg results use the same column names, so here
        # we check for an aseg result file and prepend aseg_meas
        # to the column names
        if orig_first_col == 'Measure:mean':
            dft = dft.rename(columns=lambda x: 'aseg_mean_{}'.format(x))
        elif orig_first_col == 'Measure:volume':
            dft = dft.rename(columns=lambda x: 'aseg_volume_{}'.format(x))
        if df is None:
            df = dft
        else:
            duplicate_columns = df.columns.intersection(dft.columns)
            if len(duplicate_columns) > 0:
                raise RuntimeError('Duplicate columns {}'.format(duplicate_columns))
            df = df.join(dft, how='outer')
    return df


def combine_stats_cmd():
    parser = argparse.ArgumentParser(description='Combine FreeSurfer stats files')
    parser.add_argument('inputs', type=Path, nargs='+',
                        help='input files generated with aparcstats2table or asegstats2table')
    parser.add_argument('output', type=Path,
                        help='output file')
    args = parser.parse_args()
    df = combine_stats(args.inputs)
    df.to_csv(args.output, sep='\t')
