/** Classical Metropolis simulated annealing for Ising models; no quantum hardware. */
function finiteNumber(value, name) {
  if (typeof value !== "number" || !Number.isFinite(value)) throw new Error(name + " must be finite");
  return value;
}
export function validateModel(fields, couplings = {}) {
  if (!Array.isArray(fields) || fields.length < 1 || fields.length > 24) throw new Error("Use 1–24 fields");
  fields.forEach((h, i) => finiteNumber(h, "Field " + i));
  if (!couplings || typeof couplings !== "object" || Array.isArray(couplings)) throw new Error("Couplings must be an object");
  const edges = [];
  const seen = new Set();
  for (const [key, value] of Object.entries(couplings)) {
    if (!/^\d+,\d+$/.test(key)) throw new Error("Coupling keys must be 0-based pairs such as 0,1");
    const [a, b] = key.split(",").map(Number);
    if (!Number.isSafeInteger(a) || !Number.isSafeInteger(b) || a >= fields.length || b >= fields.length || a === b) throw new Error("Invalid coupling indices: " + key);
    const id = Math.min(a, b) + "," + Math.max(a, b);
    if (seen.has(id)) throw new Error("Duplicate coupling: " + id);
    seen.add(id);
    edges.push([a, b, finiteNumber(value, "Coupling " + key)]);
  }
  return edges;
}
export function isingEnergy(spins, fields, couplings = {}) {
  const edges = validateModel(fields, couplings);
  if (!Array.isArray(spins) || spins.length !== fields.length || !spins.every(s => s === -1 || s === 1)) throw new Error("Spins must be -1 or +1");
  return spins.reduce((sum, s, i) => sum + s * fields[i], 0) + edges.reduce((sum, [i, j, v]) => sum + v * spins[i] * spins[j], 0);
}
function seededRandom(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
export function sampleIsing(fields, couplings = {}, options = {}) {
  const edges = validateModel(fields, couplings);
  const { numReads = 32, sweeps = 200, tempStart = 5, tempEnd = 0.05, seed = 0 } = options;
  if (!Number.isInteger(numReads) || numReads < 1 || numReads > 200) throw new Error("Reads must be 1–200");
  if (!Number.isInteger(sweeps) || sweeps < 1 || sweeps > 2000) throw new Error("Sweeps must be 1–2000");
  if (!(finiteNumber(tempEnd, "Final temperature") > 0 && finiteNumber(tempStart, "Initial temperature") >= tempEnd)) throw new Error("Require 0 < final temperature ≤ initial temperature");
  if (!Number.isInteger(seed) || seed < 0 || seed > 4294967295) throw new Error("Seed must be a 32-bit unsigned integer");
  const rng = seededRandom(seed);
  const n = fields.length;
  const neighbors = Array.from({ length: n }, () => []);
  for (const [i, j, v] of edges) { neighbors[i].push([j, v]); neighbors[j].push([i, v]); }
  const counts = new Map();
  for (let read = 0; read < numReads; read++) {
    const spins = Array.from({ length: n }, () => rng() < 0.5 ? -1 : 1);
    const order = Array.from({ length: n }, (_, i) => i);
    for (let step = 0; step < sweeps; step++) {
      const temperature = sweeps === 1 ? tempEnd : tempStart * Math.pow(tempEnd / tempStart, step / (sweeps - 1));
      for (let k = n - 1; k > 0; k--) { const j = Math.floor(rng() * (k + 1)); [order[k], order[j]] = [order[j], order[k]]; }
      for (const i of order) {
        const local = fields[i] + neighbors[i].reduce((sum, [j, v]) => sum + v * spins[j], 0);
        const delta = -2 * spins[i] * local;
        if (delta <= 0 || rng() < Math.exp(-delta / temperature)) spins[i] *= -1;
      }
    }
    const key = spins.join(",");
    counts.set(key, (counts.get(key) || 0) + 1);
  }
  const samples = [...counts].map(([key, count]) => {
    const spins = key.split(",").map(Number);
    const energy = spins.reduce((sum, s, i) => sum + fields[i] * s, 0) +
      edges.reduce((sum, [i, j, v]) => sum + v * spins[i] * spins[j], 0);
    return { spins, energy, count, fraction: count / numReads };
  });
  samples.sort((a, b) => a.energy - b.energy || b.count - a.count || a.spins.join(",").localeCompare(b.spins.join(",")));
  return { method: "classical_simulated_annealing", model: "Ising", num_reads: numReads, sweeps,
    best_energy: samples[0].energy, best_spins: samples[0].spins, samples };
}
