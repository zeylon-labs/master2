const test = require('node:test');
const assert = require('node:assert/strict');
const {queue, route, NODES} = require('../model.js');

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
