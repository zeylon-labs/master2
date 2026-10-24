const{test}=require('node:test'),assert=require('node:assert/strict');
const M=require('../coordination-model.js');
test('Un événement est reçu par chaque abonné présent',()=>{const s=M.create();M.publish(s);assert.deepEqual(s.received,{email:[1],stock:[1]});});
test('Un abonné absent manque le message, sans rejeu à la reconnexion',()=>{const s=M.create();M.connect(s,false);M.publish(s);M.connect(s,true);assert.deepEqual(s.received.stock,[]);M.publish(s);assert.deepEqual(s.received.stock,[2]);});
test('rd conserve le tuple pour un autre consommateur',()=>{const s=M.create();M.out(s);M.read(s,'A','rd');M.read(s,'B','rd');assert.deepEqual(s.tuples,[1]);assert.match(s.results.A,/T1 lue/);assert.match(s.results.B,/T1 lue/);});
test('Une occurrence ne peut être retirée deux fois',()=>{const s=M.create();M.out(s);M.read(s,'A','in');M.read(s,'B','in');assert.deepEqual(s.tuples,[]);assert.deepEqual(s.pending,[{consumer:'B',operation:'in'}]);M.out(s);assert.match(s.results.B,/T2 retirée/);assert.equal(s.pending.length,0);});
test('Une lecture en attente reprend au dépôt suivant',()=>{const s=M.create();M.read(s,'A','rd');assert.equal(s.pending.length,1);M.out(s);assert.equal(s.pending.length,0);assert.deepEqual(s.tuples,[1]);});
test('Deux dépôts identiques créent deux occurrences',()=>{const s=M.create();M.out(s);M.out(s);M.read(s,'A','in');assert.deepEqual(s.tuples,[2]);});
test('La reprise illustrée peut lire puis retirer le même tuple',()=>{const s=M.create();M.read(s,'A','rd');M.read(s,'B','in');M.out(s);assert.match(s.results.A,/T1 lue/);assert.match(s.results.B,/T1 retirée/);assert.deepEqual(s.tuples,[]);});
