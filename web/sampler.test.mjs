import test from "node:test";
import assert from "node:assert/strict";
import { isingEnergy, sampleIsing } from "./sampler.mjs";

test("known energy and one-spin ground state", () => {
  assert.equal(isingEnergy([1, -1], [0.5, -1], {"0,1": -2}), 3.5);
  const result = sampleIsing([1], {}, {numReads: 8, sweeps: 100, seed: 42, tempEnd: 0.001});
  assert.equal(result.best_energy, -1);
  assert.deepEqual(result.best_spins, [-1]);
});
test("seed reproducibility and consistent counts", () => {
  const a = sampleIsing([0.2, -0.4], {"0,1": -1}, {numReads: 80, sweeps: 30, seed: 100});
  const b = sampleIsing([0.2, -0.4], {"0,1": -1}, {numReads: 80, sweeps: 30, seed: 100});
  assert.deepEqual(a, b);
  assert.equal(a.samples.reduce((n, s) => n + s.count, 0), 80);
  for (const sample of a.samples) assert.ok(Math.abs(sample.energy - isingEnergy(sample.spins, [0.2, -0.4], {"0,1": -1})) < 1e-12);
});
test("invalid models and schedules are rejected", () => {
  assert.throws(() => sampleIsing([], {}));
  assert.throws(() => sampleIsing([0, 0], {"0,0": 2}));
  assert.throws(() => sampleIsing([0, 0], {"0,1": 2, "1,0": 3}));
  assert.throws(() => sampleIsing([0], {}, {numReads: 0}));
  assert.throws(() => sampleIsing([0], {}, {tempEnd: 0}));
});
