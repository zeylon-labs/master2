const test = require('node:test');
const assert = require('node:assert/strict');
const {queue, route, NODES, scaling} = require('../model.js');

test('La charge augmente l’attente sans modifier la durée de traitement', () => {
  const normal = queue(50, 10), busy = queue(90, 10);
  assert.equal(normal.response, 20);
  assert.ok(Math.abs(busy.response - 100) < 1e-8);
  assert.equal(normal.response - normal.wait, 10);
  assert.equal(busy.response - busy.wait, 10);
  assert.ok(busy.wait > normal.wait);
});
test('Le modèle distingue charge nulle et régime instable', () => {
  assert.equal(queue(0, 10).wait, 0);
  assert.equal(queue(100, 10).stable, false);
  assert.equal(queue(100, 10).response, Infinity);
});
test('Le routage reproduit le parcours du support et le retour au début de l’anneau', () => {
  assert.deepEqual(route(9, 3).path, [9, 28, 1, 4]);
  assert.equal(route(9, 30).owner, 1);
  assert.deepEqual(route(14, 14).path, [14]);
  assert.equal(route(1, 12).owner, 14);
});
test('Chaque recherche rejoint le bon responsable sans revisiter un nœud', () => {
  for (const start of NODES) for (let key = 0; key < 32; key++) {
    const result = route(start, key);
    const expected = NODES.filter(n => n >= key).sort((a,b) => a-b)[0] ?? 1;
    assert.equal(result.path.at(-1), expected);
    assert.equal(new Set(result.path).size, result.path.length);
  }
});

test('Une capacité totale identique ne signifie pas une latence identique', () => {
  const {vertical, horizontal} = scaling(80,100,2,2);
  assert.equal(vertical.capacity,200);
  assert.equal(horizontal.capacity,200);
  assert.equal(horizontal.perNode,40);
  assert.equal(vertical.utilisation,horizontal.utilisation);
  assert.ok(Math.abs(vertical.response-8.3333333333)<1e-6);
  assert.ok(Math.abs(horizontal.response-16.6666666667)<1e-6);
});
test('La comparaison signale la saturation de chaque configuration', () => {
  const saturated=scaling(200,100,2,2);
  assert.equal(saturated.vertical.stable,false);
  assert.equal(saturated.horizontal.stable,false);
  assert.equal(saturated.horizontal.response,Infinity);
  const mixed=scaling(300,100,2,4);
  assert.equal(mixed.vertical.stable,false);
  assert.equal(mixed.horizontal.stable,true);
  assert.equal(mixed.horizontal.utilisation,.75);
});
test('Une seule machine de référence retrouve le modèle de départ', () => {
  const r=scaling(80,100,1,1);
  assert.ok(Math.abs(r.vertical.response-50)<1e-8);
  assert.equal(r.vertical.response,r.horizontal.response);
  assert.throws(()=>scaling(80,100,2,0),RangeError);
});
