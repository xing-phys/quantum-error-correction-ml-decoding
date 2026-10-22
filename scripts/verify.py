"""Scientific and publication checks; run after data generation and Quarto rendering.

The script intentionally does not claim to replace scientific or visual review.
"""
import csv, importlib.util, json, re, sys
from pathlib import Path
from urllib.parse import unquote, urlsplit
import numpy as np
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'examples'))
from neural_coset import distribution,joint,syndrome,pure,label

def source_checks():
    bib=(ROOT/'assets'/'bibliography.bib').read_text()
    keys=re.findall(r'@\w+\s*\{\s*([^,\s]+)',bib)
    assert len(keys)==len(set(keys)), 'Duplicate citation keys'
    sources={p:p.read_text() for p in ROOT.glob('*.qmd')}
    ids=[]
    for p,s in sources.items():
        ids += [(i,p.name) for i in re.findall(r'\{[^}\n]*#([a-zA-Z][\w:-]*)',s)]
        assert s.count('$$')%2==0, f'Unpaired display delimiters: {p}'
        assert 'TODO' not in s and 'PLACEHOLDER' not in s, f'Unfinished source: {p}'
    found={}
    for i,p in ids:
        assert i not in found, f'Duplicate label {i}: {p} and {found.get(i)}'
        found[i]=p
    missing=[]
    for p,s in sources.items():
        # Ignore fenced code when examining Quarto citation syntax.
        clean=re.sub(r'```.*?```','',s,flags=re.S)
        for key in re.findall(r'(?<![\w/])@([A-Za-z][\w:-]*)',clean):
            if key not in keys and key not in found:missing.append((p.name,key))
    assert not missing, f'Unknown citations/references: {missing}'
    print(f'Source: {len(sources)} pages, {len(keys)} references, {len(ids)} unique labels.')

def scientific_checks():
    saved=json.loads((ROOT/'data'/'neural-results.json').read_text())
    w=joint(distribution(saved['p'],saved['alpha']))
    pred=np.array(saved['decisions'])
    assert np.isclose(w.sum(),1)
    oracle_risk=w.min(axis=1).sum()
    risk=sum(w[s,1-pred[s]] for s in range(8))
    assert np.isclose(risk,oracle_risk)
    assert np.isclose(risk,saved['oracle_risk'])
    assert risk<saved['minimum_weight_risk']
    # Independently verify every Steane residual against the row-space span.
    H=np.array([[(j>>i)&1 for j in range(1,8)] for i in range(3)])
    assert not np.any((H@H.T)%2)
    span=set()
    for u in range(8):
        bits=(np.array([(u>>i)&1 for i in range(3)])@H)%2
        span.add(sum(int(v)<<j for j,v in enumerate(bits)))
    for e in range(128):
        residual=e^pure(syndrome(e))
        assert syndrome(residual)==0
        assert (residual in span)==(label(e)==0)
    with (ROOT/'data'/'exact-decoding.csv').open() as f:
        for r in csv.DictReader(f):
            j=joint(distribution(float(r['p']),float(r['alpha'])))
            assert np.isclose(j[:,1].sum(),float(r['minimum_weight_failure']))
            assert np.isclose(j.min(axis=1).sum(),float(r['exact_ml_failure']))
    with (ROOT/'data'/'surface-memory.csv').open() as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==15
    assert sum(int(r['shots']) for r in rows)==300000
    for r in rows:
        rate=int(r['failures'])/int(r['shots'])
        assert np.isclose(rate,float(r['logical_failure']))
        assert float(r['ci_low'])<=rate<=float(r['ci_high'])
        assert int(r['rounds'])==int(r['distance'])
    print('Science: exhaustive Steane classes, Julia/Python probabilities, neural oracle risk, and all Monte Carlo records pass.')

def html_checks():
    site=ROOT/'_site'
    if not (site/'index.html').exists():
        print('HTML: not yet rendered; skipped.'); return
    pages={p:BeautifulSoup(p.read_text(),'html.parser') for p in site.glob('*.html')}
    anchors={p:{x['id'] for x in soup.select('[id]')} for p,soup in pages.items()}
    errors=[]
    for p,soup in pages.items():
        assert soup.find('title'),f'Missing title {p}'
        assert not soup.select('.quarto-xref-unresolved'),f'Unresolved crossref {p}'
        for item in soup.select('[href], img[src], script[src]'):
            raw=item.get('href',item.get('src',''));u=urlsplit(raw)
            if u.scheme or u.netloc or not raw or raw.startswith('data:'):continue
            path=unquote(u.path)
            target=(site/path.lstrip('/')) if path.startswith('/') else (p.parent/path)
            target=target.resolve()
            if not path:target=p
            if target.is_dir():target=target/'index.html'
            if not target.exists():errors.append((p.name,raw,'missing file'));continue
            if u.fragment and target.suffix=='.html':
                if target not in anchors:
                    anchors[target]={x['id'] for x in BeautifulSoup(target.read_text(),'html.parser').select('[id]')}
                if unquote(u.fragment) not in anchors[target]:errors.append((p.name,raw,'missing fragment'))
    assert not errors,f'Broken local URLs: {errors[:30]}'
    pdf=site/'qec-ml-textbook.pdf'
    assert pdf.exists() and pdf.stat().st_size>1000,'Missing PDF download'
    from pypdf import PdfReader
    reader=PdfReader(pdf)
    assert len(reader.pages)>100,'Unexpectedly short combined textbook PDF'
    assert (site/'search.json').exists(),'Missing search index'
    assert len(pages)==20,f'Expected 20 HTML pages, got {len(pages)}'
    print(f'Publication: {len(pages)} HTML pages, all local links/fragments/assets, search, and {len(reader.pages)}-page PDF pass.')

if __name__=='__main__':
    source_checks();scientific_checks();html_checks()
