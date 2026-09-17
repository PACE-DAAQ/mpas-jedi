"""Compare a controlled analysis replay with its unclipped reference output."""
import argparse
import json
import numpy as np
from netCDF4 import Dataset

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('reference')
parser.add_argument('clipped')
parser.add_argument('--allow-reference-extras', action='store_true',
                    help='Allow carryover fields present only in a workflow-augmented reference')
args = parser.parse_args()
names = [f'q{x}{mode}' for x in ('bc', 'br', 'oc')
         for mode in ('phobic', 'philic')]
names += [f'qdust{i}' for i in range(1, 6)]
names += [f'qseas{i}' for i in range(1, 6)]
names += [f'qni{i}' for i in range(1, 4)] + ['qso4']
report = {'aerosols': {}, 'other_fields_unchanged': []}
with Dataset(args.reference) as reference, Dataset(args.clipped) as clipped:
    missing = set(reference.variables) - set(clipped.variables)
    if set(clipped.variables) - set(reference.variables):
        raise AssertionError('Unexpected replay fields')
    if (not args.allow_reference_extras) and missing:
        raise AssertionError('Field sets differ')
    report['reference_only_fields_not_compared'] = sorted(missing)
    for name in clipped.variables:
        x = reference[name][:]
        y = clipped[name][:]
        if x.shape != y.shape:
            raise AssertionError(name)
        if not np.array_equal(np.ma.getmaskarray(x), np.ma.getmaskarray(y)):
            raise AssertionError(name)
        if name in names:
            if np.ma.getmaskarray(x).any():
                raise AssertionError(name)
            if not (np.isfinite(x).all() and np.isfinite(y).all()):
                raise AssertionError(name)
            if not np.array_equal(y, np.maximum(x, 0)):
                raise AssertionError(name)
            report['aerosols'][name] = {'negative_entries_removed': int((x < 0).sum())}
        else:
            equal = (np.array_equal(x, y, equal_nan=True) if x.dtype.kind in 'fc'
                     else np.array_equal(x, y))
            if not equal:
                raise AssertionError('Unexpected change in ' + name)
            report['other_fields_unchanged'].append(name)
if set(report['aerosols']) != set(names):
    raise AssertionError('Missing configured aerosol fields')
print(json.dumps(report, indent=2))
