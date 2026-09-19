const test = require('node:test'), assert = require('node:assert');
const { wavBytes } = require('../../site/assets/voicepack.js');

test('wavBytes writes a valid mono 16-bit header and round-trips int16 samples exactly', () => {
  const ints = [0, 1, -1, 32767, -32768, 12345];
  const b = wavBytes([Float32Array.from(ints, (i) => i / 32768)], 16000), v = new DataView(b);
  assert.strictEqual(String.fromCharCode(...new Uint8Array(b, 0, 4)), 'RIFF');
  assert.strictEqual(v.getUint32(24, true), 16000);
  assert.strictEqual(v.getUint16(22, true), 1);
  assert.strictEqual(v.getUint32(40, true), ints.length * 2);
  assert.deepStrictEqual(ints.map((_, i) => v.getInt16(44 + i * 2, true)), ints);
});

test('wavBytes interleaves stereo', () => {
  const v = new DataView(wavBytes([Float32Array.of(0.5, 0), Float32Array.of(-0.5, 0.25)], 16000));
  assert.strictEqual(v.getUint16(22, true), 2);
  assert.deepStrictEqual([0, 1, 2, 3].map((i) => v.getInt16(44 + i * 2, true)), [16384, -16384, 0, 8192]);
});
