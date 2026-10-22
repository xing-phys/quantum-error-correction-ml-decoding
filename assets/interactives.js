/* Exact, browser-local educational models. No network, analytics, or trained weights. */
(() => {
  'use strict';
  const bitcount = n => { let k=0; for(;n;n>>>=1) k+=n&1; return k; };
  const syndrome = e => { let s=0; for(let j=0;j<7;j++) if((e>>j)&1)s^=j+1; return s; };
  const pure = s => s?1<<(s-1):0;
  const joint = (p,a) => {
    const w=Array.from({length:8},()=>[0,0]);
    for(let e=0;e<128;e++) {
      const k=bitcount(e),s=syndrome(e),l=bitcount(e^pure(s))%2;
      w[s][l]+=(1-a)*p**k*(1-p)**(7-k)+(e===3?a:0);
    } return w;
  };
  const el=(tag,attrs={},content='')=>{
    const n=document.createElement(tag); for(const[k,v]of Object.entries(attrs))n.setAttribute(k,v);
    n.textContent=content; return n;
  };
  const out=box=>{const n=el('div',{'class':'lab-output','role':'status','aria-live':'polite'});box.append(n);return n;};
  function slider(box,text,min,max,value,step,callback) {
    const label=el('label'),input=el('input',{type:'range',min,max,value,step});
    const v=el('span',{},String(value)); label.append(document.createTextNode(text+' '),v,document.createTextNode(' '),input);
    box.append(label);input.addEventListener('input',()=>{v.textContent=Number(input.value).toFixed(3);callback();});return input;
  }
  function steane(box) {
    let error=0;
    const buttons=el('div',{'role':'group','aria-label':'Toggle X errors on seven data qubits'});
    const result=out(box);box.prepend(buttons);
    function draw(){
      const s=syndrome(error),r=error^pure(s),l=bitcount(r)%2;
      [...buttons.children].forEach((b,i)=>b.setAttribute('aria-pressed',String(Boolean((error>>i)&1))));
      result.textContent=`Error bits q1…q7: ${Array.from({length:7},(_,i)=>(error>>i)&1).join(' ')}\nSyndrome integer: ${s}; binary check bits: ${[0,1,2].map(i=>(s>>i)&1).join(' ')}\nReference correction: ${s?'X on q'+s:'identity'}\nResidual weight: ${bitcount(r)}; residual syndrome: ${syndrome(r)}\nLogical class: ${l?'logical X — correction fails':'stabilizer — correction succeeds'}`;
    }
    for(let i=0;i<7;i++){
      const b=el('button',{'type':'button','aria-pressed':'false'},`q${i+1}`);
      b.addEventListener('click',()=>{error^=1<<i;draw();});buttons.append(b);
    }
    const reset=el('button',{type:'button'},'Reset');reset.addEventListener('click',()=>{error=0;draw();});box.append(reset);draw();
  }
  function posterior(box){
    let p,a;const update=()=>{if(!p||!a)return;const w=joint(+p.value,+a.value);
      const risk=w.reduce((x,y)=>x+Math.min(...y),0),base=w.reduce((x,y)=>x+y[1],0);
      result.textContent=' s    P(logical X | s)    best class\n'+w.map((r,s)=>`${s.toString().padStart(2)}       ${(r[1]/(r[0]+r[1])).toFixed(5)}             ${r[1]>r[0]?1:0}`).join('\n')+
      `\n\nMinimum-weight logical failure: ${base.toFixed(6)}\nExact class-ML logical failure: ${risk.toFixed(6)}\nAll 128 X-error patterns are enumerated.`;};
    p=slider(box,'Independent flip probability p',.001,.3,.06,.001,update);
    a=slider(box,'Probability α of the fixed X₁X₂ burst',0,.5,.18,.005,update);
    const result=out(box);update();
  }
  function repeat(box){
    let p;const choose=(n,k)=>{let c=1;for(let i=1;i<=k;i++)c=c*(n-i+1)/i;return c;};
    const update=()=>{if(!p)return;const q=+p.value;result.textContent=' d     exact majority-decoder failure\n'+[1,3,5,7,9,11,15].map(d=>{
      let r=0;for(let k=(d+1)/2;k<=d;k++)r+=choose(d,k)*q**k*(1-q)**(d-k);
      return `${String(d).padStart(2)}     ${r.toExponential(6)}`;
    }).join('\n')+'\n\nPerfect syndrome; independent X noise only. This is not a full quantum-code threshold.';};
    p=slider(box,'Physical X-error probability p',.001,.499,.1,.001,update);const result=out(box);update();
  }
  function toric(box){
    const L=4,selected=new Set();
    const group=el('div',{'role':'group','aria-label':'Toggle edges on a four by four torus'});
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 460 330');
    svg.setAttribute('role','img');svg.setAttribute('aria-label','Periodic square lattice with highlighted errors and syndrome endpoints');
    box.append(svg,group);const result=out(box);
    function endpoints(id){const t=Math.floor(id/16),j=id%16,x=j%4,y=Math.floor(j/4);
      return [j,t?x+4*((y+1)%4):((x+1)%4)+4*y];}
    function draw(){
      const defects=new Set();let wx=0,wy=0;
      selected.forEach(id=>{endpoints(id).forEach(v=>defects.has(v)?defects.delete(v):defects.add(v));const j=id%16;
        if(id<16&&j%4===3)wx^=1;if(id>=16&&Math.floor(j/4)===3)wy^=1;});
      svg.innerHTML='';
      const ns='http://www.w3.org/2000/svg';
      const add=(tag,attrs,text)=>{const n=document.createElementNS(ns,tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v));if(text)n.textContent=text;svg.append(n);};
      for(let id=0;id<32;id++){
        const j=id%16,x=j%4,y=Math.floor(j/4),h=id<16;
        const x1=55+90*x,y1=35+75*y;
        add('line',{x1,y1,x2:h?x1+70:x1,y2:h?y1:y1+55,stroke:selected.has(id)?'#c16321':'#93a8b4','stroke-width':selected.has(id)?6:2,'stroke-dasharray':(h?x===3:y===3)?'5 3':'none'});
      }
      for(let v=0;v<16;v++){const x=55+90*(v%4),y=35+75*Math.floor(v/4);
        add('circle',{cx:x,cy:y,r:9,fill:defects.has(v)?'#c33348':'#087e8b'});
        add('text',{x:x-6,y:y-14,fill:'#536876','font-size':12},String(v));}
      [...group.children].forEach((b,id)=>b.setAttribute('aria-pressed',String(selected.has(id))));
      result.textContent=`Selected Z-error edges: ${selected.size}\nStar-check defects: ${[...defects].sort((a,b)=>a-b).join(', ')||'none'}\nHorizontal/vertical seam parities: ${wx}, ${wy}\n${defects.size?'For an open chain, seam parity depends on the reference correction.':'Closed chain: nonzero seam parity is a nontrivial logical Z winding.'}`;
    }
    for(let id=0;id<32;id++){const j=id%16,b=el('button',{type:'button','aria-pressed':'false'},`${id<16?'h':'v'}(${j%4},${Math.floor(j/4)})`);
      b.addEventListener('click',()=>{selected.has(id)?selected.delete(id):selected.add(id);draw();});group.append(b);}
    const loop=el('button',{type:'button'},'Show horizontal logical loop');loop.addEventListener('click',()=>{selected.clear();[0,1,2,3].forEach(i=>selected.add(i));draw();});
    const reset=el('button',{type:'button'},'Reset');reset.addEventListener('click',()=>{selected.clear();draw();});box.append(loop,reset);draw();
  }
  document.addEventListener('DOMContentLoaded',()=>{
    const widgets={steane,posterior,repeat,toric};
    document.querySelectorAll('[data-qec-widget]').forEach(box=>{const f=widgets[box.dataset.qecWidget];if(f)f(box);});
  });
  if(typeof module!=='undefined')module.exports={syndrome,pure,joint};
})();
