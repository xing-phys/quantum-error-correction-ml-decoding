"""Merge verified chapter fragments, rejecting duplicate citation keys."""
import re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
fragments=sorted((root/'assets').glob('refs-*.bib'))
seen=set();text=[]
for path in fragments:
    s=path.read_text()
    keys=re.findall(r'@\w+\s*\{\s*([^,\s]+)',s)
    for key in keys:
        if key in seen:raise SystemExit(f'Duplicate bibliography key: {key}')
        seen.add(key)
    text.append(f'% Verified source fragment: {path.name}\n'+s.strip())
(root/'assets'/'bibliography.bib').write_text('\n\n'.join(text)+'\n')
print(f'Merged {len(seen)} references from {len(fragments)} fragments.')
