"""A fully explicit NumPy neural decoder, with independent test data and an exact oracle.

This is a seven-qubit pedagogical model; no scalability or threshold claim is made.
Run from the repository root: python examples/neural_coset.py
"""
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]

def syndrome(e):
    s=0
    for j in range(7):
        if (int(e)>>j)&1: s ^= j+1
    return s

def pure(s):
    return 0 if s==0 else 1<<(s-1)

def label(e):
    return (int(e)^pure(syndrome(e))).bit_count()%2

def distribution(p,alpha):
    if not(0<=p<=1 and 0<=alpha<=1): raise ValueError("invalid noise parameters")
    prob=np.array([(1-alpha)*p**e.bit_count()*(1-p)**(7-e.bit_count())
                   +alpha*(e==3) for e in range(128)])
    assert np.isclose(prob.sum(),1)
    return prob

def joint(prob):
    w=np.zeros((8,2))
    for e,q in enumerate(prob): w[syndrome(e),label(e)]+=q
    return w

def sigmoid(a):
    a=np.clip(a,-50,50)
    return 1/(1+np.exp(-a))

def main():
    seed=7123; rng=np.random.default_rng(seed)
    p,alpha=.06,.18
    prob=distribution(p,alpha); w=joint(prob)
    train=rng.choice(128,20_000,p=prob)
    # Aggregate identical inputs; equivalent to full-batch training on all samples.
    counts=np.zeros((8,2))
    for e in train: counts[syndrome(e),label(e)]+=1
    mass=counts.sum(axis=1)/len(train)
    target=counts[:,1]/np.maximum(counts.sum(axis=1),1)
    x=2*np.array([[(s>>i)&1 for i in range(3)] for s in range(8)])-1
    W1=rng.normal(0,.3,(3,16)); b1=np.zeros(16)
    W2=rng.normal(0,.3,16); b2=0.
    losses=[]
    for step in range(4000):
        h=np.tanh(x@W1+b1); z=h@W2+b2; y=sigmoid(z)
        loss=np.sum(mass*(np.logaddexp(0,z)-target*z))
        dz=mass*(y-target)
        dW2=h.T@dz; db2=dz.sum()
        dh=dz[:,None]*W2[None,:]*(1-h*h)
        W1-=.8*(x.T@dh); b1-=.8*dh.sum(axis=0)
        W2-=.8*dW2; b2-=.8*db2
        if step%100==0: losses.append([step,float(loss)])
    prediction=(sigmoid(np.tanh(x@W1+b1)@W2+b2)>.5).astype(int)
    oracle=w.argmax(axis=1)
    exact_risk=float(w.min(axis=1).sum())
    learned_risk=float(sum(w[s,1-prediction[s]] for s in range(8)))
    baseline_risk=float(w[:,1].sum())
    test_rng=np.random.default_rng(seed+1)
    test=test_rng.choice(128,100_000,p=prob)
    test_fail=sum(prediction[syndrome(e)]!=label(e) for e in test)
    assert learned_risk>=exact_risk-1e-12
    assert learned_risk<baseline_risk
    assert np.array_equal(prediction,oracle),"Training did not reach oracle decisions"
    result=dict(seed=seed,p=p,alpha=alpha,train_shots=len(train),test_shots=len(test),
                test_failures=int(test_fail),test_rate=test_fail/len(test),
                minimum_weight_risk=baseline_risk,learned_exact_risk=learned_risk,
                oracle_risk=exact_risk,decisions=prediction.tolist(),
                posterior=(w[:,1]/w.sum(axis=1)).tolist(),losses=losses,
                numpy_version=np.__version__)
    (ROOT/'data'/'neural-results.json').write_text(json.dumps(result,indent=2)+'\n')
    np.savez(ROOT/'data'/'neural-model.npz',W1=W1,b1=b1,W2=W2,b2=b2)
    print(json.dumps({k:v for k,v in result.items() if k not in ['losses','posterior']},indent=2))

if __name__=='__main__': main()
