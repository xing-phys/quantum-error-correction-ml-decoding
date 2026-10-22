"""Build original vector illustrations and plots from the checked-in lab data."""
from pathlib import Path
import csv, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle

ROOT=Path(__file__).resolve().parents[1]; FIG=ROOT/'figs'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,
    'axes.spines.right':False,'svg.fonttype':'none','savefig.bbox':'tight'})
C=['#087e8b','#c16321','#4456a5','#a33158']
def save(fig,name):
    for ext in ['svg','pdf','png']: fig.savefig(FIG/f'{name}.{ext}',dpi=180)
    svg=FIG/f'{name}.svg'
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines())+"\n")
    plt.close(fig)
def box(ax,xy,w,h,text,color=C[0],size=11):
    ax.add_patch(FancyBboxPatch(xy,w,h,boxstyle='round,pad=.02',facecolor='#f0f6f8',edgecolor=color,lw=1.5))
    ax.text(xy[0]+w/2,xy[1]+h/2,text,ha='center',va='center',fontsize=size,color='#173548')
def arrow(ax,start,end,color='#526b7b'):
    ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=13,color=color,lw=1.5))

# Information flow, preserving the logical-class distinction.
fig,ax=plt.subplots(figsize=(11,3.5));ax.set(xlim=(0,11),ylim=(0,3.3));ax.axis('off')
for x,t in zip([.1,2.9,5.7,8.5],['Physical noise\nPauli / circuit / analog','Measurements\nsyndromes and detectors','Inference\nlogical-class posterior','Classical frame\nlogical action / feedback']):box(ax,(x,1.3),2.3,1.1,t)
for x in [2.4,5.2,8]:arrow(ax,(x,1.85),(x+.5,1.85))
ax.text(5.5,.5,'Many physical errors share a syndrome. Many also have the same logical action.',ha='center',fontsize=12,color=C[0])
save(fig,'decoding-pipeline')

# Hamming/Steane parity-check factor graph.
fig,ax=plt.subplots(figsize=(9,3.7));ax.axis('off');ax.set(xlim=(-.6,6.6),ylim=(-.6,3.5))
for j in range(7):
    for i in range(3):
        if ((j+1)>>i)&1:ax.plot([j,1+2*i],[2.7,.4],color=C[i],alpha=.6,lw=1.5)
for j in range(7):
    ax.add_patch(Circle((j,2.7),.21,color='#16324a'));ax.text(j,3.15,f'q{j+1}',ha='center')
for i in range(3):
    ax.add_patch(Rectangle((.8+2*i,.2),.4,.4,color=C[i]));ax.text(1+2*i,-.2,f'check {i+1}',ha='center',color=C[i])
ax.text(3,3.6,'Column j is the binary representation of j',ha='center',fontsize=12)
save(fig,'parity-factor-graph')

# Three orthogonal syndrome sectors in repetition code (conceptual).
fig,ax=plt.subplots(figsize=(10,3.6));ax.axis('off');ax.set(xlim=(0,10),ylim=(0,3.7))
box(ax,(.2,1.15),2.1,1.2,'Encoded qubit\nα|000⟩ + β|111⟩')
for y,t in [(2.75,'00: no X error'),(1.85,'10: X₁ subspace'),(.95,'11: X₂ subspace'),(.05,'01: X₃ subspace')]:
    box(ax,(4,y),2.3,.65,t,size=10);arrow(ax,(2.35,1.75),(3.95,y+.325))
box(ax,(7.8,1.15),2,1.2,'Conditional recovery\nα and β preserved')
for y in [3.075,2.175,1.275,.375]:arrow(ax,(6.35,y),(7.75,1.75))
ax.text(5,3.65,'Measure an error label, not the logical amplitudes',ha='center',color=C[0],fontsize=12)
save(fig,'syndrome-subspaces')

# Torus shown as a periodic square fundamental domain.
fig,ax=plt.subplots(figsize=(6.7,5));ax.set_aspect('equal');ax.axis('off')
for x in range(5):ax.plot([x,x],[0,4],color='#a2b6c0',lw=1)
for y in range(5):ax.plot([0,4],[y,y],color='#a2b6c0',lw=1)
for x in range(5):
    for y in range(5):ax.plot(x,y,'o',color='#406071',ms=4)
ax.add_patch(Rectangle((1,1),1,1,facecolor='#087e8b',alpha=.17,edgecolor='none'))
ax.plot([1,2,2,1,1],[1,1,2,2,1],color=C[0],lw=5,label='Contractible stabilizer loop')
ax.plot([0,4],[3,3],color=C[1],lw=5,label='Noncontractible logical loop')
ax.text(2,4.35,'Top and bottom identified',ha='center',fontsize=10)
ax.text(-.4,2,'Left and right identified',rotation=90,va='center',fontsize=10)
ax.legend(loc='upper center',bbox_to_anchor=(.5,-.03),frameon=False,fontsize=10)
ax.set(xlim=(-.7,4.3),ylim=(-.1,4.6));save(fig,'surface-homology')

# Detector spacetime example.
fig,ax=plt.subplots(figsize=(7.2,4.2));ax.set(xlim=(-.4,4.6),ylim=(-.4,3.7),xlabel='Check position',ylabel='Syndrome round')
for x in range(5):
    for t in range(4):
        if x<4:ax.plot([x,x+1],[t,t],color='#d9e4e9',lw=1)
        if t<3:ax.plot([x,x],[t,t+1],color='#d9e4e9',lw=1)
        ax.plot(x,t,'o',color='#9fb2bd',ms=4)
ax.plot([1,2],[1,1],color=C[1],lw=5,label='Data fault')
ax.plot([3,3],[1,2],color=C[0],lw=5,label='Measurement fault')
for x,t in [(1,1),(2,1),(3,1),(3,2)]:ax.plot(x,t,'o',color=C[3],ms=11)
ax.set(xticks=range(5),yticks=range(4));ax.legend(frameon=False,loc='upper left');save(fig,'detector-history')

# Exact repetition curve.
from math import comb
fig,ax=plt.subplots(figsize=(7.2,4.5));p=np.linspace(.002,.49,200)
for d,c in zip([3,5,9,15],C):
    rate=sum(comb(d,k)*p**k*(1-p)**(d-k) for k in range((d+1)//2,d+1))
    ax.semilogy(p,rate,label=f'd = {d}',color=c)
ax.plot(p,p,':',color='#79888f',label='Unencoded bit')
ax.set(xlabel='Independent X-error probability p',ylabel='Logical failure probability',ylim=(1e-9,.6));ax.legend(frameon=False);ax.grid(alpha=.2)
save(fig,'repetition-scaling')

neural=json.loads((ROOT/'data'/'neural-results.json').read_text())
fig,axes=plt.subplots(1,2,figsize=(10,3.9))
loss=np.array(neural['losses']);axes[0].plot(loss[:,0],loss[:,1],color=C[0]);axes[0].set(xlabel='Full-batch optimization step',ylabel='Training cross-entropy')
axes[1].bar(range(8),neural['posterior'],color=[C[1] if i==3 else C[0] for i in range(8)])
axes[1].axhline(.5,color='#526b7b',ls='--');axes[1].set(xlabel='Syndrome integer',ylabel='Exact P(logical X | syndrome)',ylim=(0,1),xticks=range(8))
fig.tight_layout();save(fig,'neural-coset')

rows=list(csv.DictReader((ROOT/'data'/'surface-memory.csv').open()))
fig,ax=plt.subplots(figsize=(7.4,4.6))
for d,c in zip([3,5,7],C):
    rr=[r for r in rows if int(r['distance'])==d]
    x=np.array([float(r['p']) for r in rr]);y=np.array([float(r['logical_failure']) for r in rr])
    lo=np.array([float(r['ci_low']) for r in rr]);hi=np.array([float(r['ci_high']) for r in rr])
    ax.errorbar(x,y,yerr=[y-lo,hi-y],fmt='o-',capsize=3,color=c,label=f'd = {d}; rounds = {d}')
ax.set(xlabel='Circuit noise parameter p',ylabel='Logical failure per memory experiment',yscale='log')
ax.legend(frameon=False);ax.grid(alpha=.2);save(fig,'surface-memory')

# Cross-attention: dimensions made explicit.
fig,ax=plt.subplots(figsize=(10,3.8));ax.axis('off');ax.set(xlim=(0,10),ylim=(0,4))
for y,t in [(2.8,'Queries Q: N × dₖ'),(1.65,'Keys K: N × dₖ'),(.5,'Values V: N × dᵥ')]:box(ax,(.1,y),2.1,.8,t,size=10)
box(ax,(3.2,2),2.1,1.2,'Scores QKᵀ / √dₖ\nN × N',size=10)
box(ax,(6.1,2),1.4,1.2,'row softmax\nweights A',size=10)
box(ax,(8.3,1),1.6,1.2,'Output AV\nN × dᵥ',size=10)
arrow(ax,(2.3,3.2),(3.15,2.8));arrow(ax,(2.3,2.05),(3.15,2.4));arrow(ax,(5.35,2.6),(6.05,2.6));arrow(ax,(7.55,2.6),(8.25,1.9));arrow(ax,(2.3,.9),(8.25,1.4))
ax.text(5,3.8,'Each detector token gathers information weighted by compatibility',ha='center',color=C[0],fontsize=12)
save(fig,'attention')

print(f'Generated {len(list(FIG.glob("*.svg")))} vector figures with matching PDF and PNG assets.')
