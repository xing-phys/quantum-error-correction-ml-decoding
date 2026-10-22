"""Reproducible circuit-level rotated surface-code memory experiment.

Fixed shots, independent seeds per (distance,p), three distances, Wilson intervals.
The small grid illustrates finite-size behavior; it is not a precise threshold fit.
"""
import argparse, csv, platform, time
from pathlib import Path
import numpy as np
import stim
import pymatching

def wilson(k,n,z=1.959963984540054):
    center=(k/n+z*z/(2*n))/(1+z*z/n)
    radius=z*np.sqrt((k/n)*(1-k/n)/n+z*z/(4*n*n))/(1+z*z/n)
    return center-radius,center+radius

def run(shots=20000):
    rows=[]
    for d in (3,5,7):
        for i,p in enumerate((.001,.003,.005,.007,.009)):
            seed=731000+100*d+i
            c=stim.Circuit.generated('surface_code:rotated_memory_x',distance=d,rounds=d,
                after_clifford_depolarization=p,before_round_data_depolarization=p,
                before_measure_flip_probability=p,after_reset_flip_probability=p)
            dem=c.detector_error_model(decompose_errors=True)
            matching=pymatching.Matching.from_detector_error_model(dem)
            det,obs=c.compile_detector_sampler(seed=seed).sample(shots,separate_observables=True)
            start=time.perf_counter()
            pred=matching.decode_batch(det)
            elapsed=time.perf_counter()-start
            fails=int(np.any(pred!=obs,axis=1).sum())
            lo,hi=wilson(fails,shots)
            rows.append(dict(distance=d,rounds=d,p=p,shots=shots,failures=fails,
                logical_failure=fails/shots,ci_low=lo,ci_high=hi,
                decode_seconds=elapsed,seed=seed,stim=stim.__version__,
                pymatching=pymatching.__version__,python=platform.python_version()))
            print(f'd={d} p={p:.3g}: {fails}/{shots} = {fails/shots:.5f}')
    out=Path(__file__).resolve().parents[1]/'data'/'surface-memory.csv'
    with out.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0],lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    print(f'Saved {out}')

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--shots',type=int,default=20000)
    args=parser.parse_args()
    if args.shots<=0: parser.error('--shots must be positive')
    run(args.shots)
