/* Unit-test the browser-local exact calculations with Node's built-in assertions. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
global.document={addEventListener(){}};
const {syndrome,pure,joint}=require('../assets/interactives.js');
for(let s=0;s<8;s++)assert.equal(syndrome(pure(s)),s);
const result=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/neural-results.json'),'utf8'));
const w=joint(result.p,result.alpha);
assert.ok(Math.abs(w.flat().reduce((x,y)=>x+y,0)-1)<1e-12);
assert.deepEqual(w.map(x=>x[1]>x[0]?1:0),result.decisions);
assert.ok(Math.abs(w.reduce((x,y)=>x+Math.min(...y),0)-result.oracle_risk)<1e-12);
for(const p of [0,.01,.3,.5,1])for(const a of [0,.18,1]){
  const v=joint(p,a);assert.ok(Math.abs(v.flat().reduce((x,y)=>x+y,0)-1)<1e-12);
  assert.ok(v.flat().every(x=>x>=0));
}
console.log('Interactive algebra, posterior, oracle decisions, and probability endpoints pass.');
