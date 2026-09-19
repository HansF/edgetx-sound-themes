const { test } = require('node:test');
const assert = require('node:assert/strict');
const { RATE, smartTrim, render, wav } = require('../../site/assets/mix-audio.js');
function signal(duration, spans = [], noise = 0) {
  const samples = new Float32Array(Math.round(duration * RATE));
  for (let i = 0; i < samples.length; i++) {
    const t = i / RATE;
    samples[i] = Math.sin(i * 1.73) * noise;
    for (const [start, end, gain = .2] of spans) if (t >= start && t < end) samples[i] += Math.sin(2 * Math.PI * 400 * t) * gain;
  }
  return samples;
}
test('trims only outer silence, with padding and preserved internal pauses', () => {
  const result = smartTrim(signal(3, [[.5, 1], [1.8, 2.4]]));
  assert.equal(result.confident, true);
  assert.ok(Math.abs(result.start - .42) < .011);
  assert.ok(Math.abs(result.end - 2.55) < .011);
});
test('silence and steady background keep the full take', () => {
  for (const samples of [signal(2), signal(2, [], .02)]) assert.deepEqual(smartTrim(samples), { start: 0, end: 2, confident: false });
});
test('an isolated click is not a sound boundary', () => {
  const samples = signal(2); samples[100] = 1;
  assert.equal(smartTrim(samples).confident, false);
  const speech = signal(3, [[1, 2]]); speech[100] = 1;
  assert.ok(smartTrim(speech).start > .8);
});
test('quiet speech is detected over a low noise floor', () => {
  const result = smartTrim(signal(3, [[.8, 1.8, .015]], .001));
  assert.equal(result.confident, true);
  assert.ok(result.start > .6 && result.start < .8);
  assert.ok(result.end > 1.8 && result.end < 2);
});
test('audio touching either boundary is not clipped', () => {
  assert.equal(smartTrim(signal(3, [[0, 1]])).start, 0);
  assert.equal(smartTrim(signal(3, [[2, 3]])).end, 3);
  assert.equal(smartTrim(signal(1, [[0, 1]])).confident, false);
});
test('render keeps original samples, fades boundaries and limits peaks', () => {
  const samples = signal(2, [[0, 2, 1.4]]), original = samples.slice();
  const output = render(samples, .2, 1.8);
  assert.deepEqual(samples, original);
  assert.equal(output.length, 25600);
  assert.equal(output[0], 0); assert.equal(Math.abs(output.at(-1)), 0);
  assert.ok(output.every(x => Number.isFinite(x) && Math.abs(x) <= .89126));
});
test('invalid and overlong selections are rejected without silently truncating', () => {
  const samples = signal(20);
  for (const [start, end] of [[0, 11], [-1, 1], [1, 1], [2, 1], [0, 21], [NaN, 1]]) assert.throws(() => render(samples, start, end));
  assert.equal(render(samples, 0, 10).length, RATE * 10);
});
test('WAV is mono little-endian 16-bit PCM at 16 kHz', async () => {
  const blob = wav(new Float32Array([-2, -.5, 0, .5, 2]));
  const buffer = await blob.arrayBuffer(), v = new DataView(buffer);
  assert.equal(blob.type, 'audio/wav');
  assert.equal(Buffer.from(buffer).subarray(0, 4).toString(), 'RIFF');
  assert.equal(v.getUint32(4, true), buffer.byteLength - 8);
  assert.equal(v.getUint16(20, true), 1); assert.equal(v.getUint16(22, true), 1);
  assert.equal(v.getUint32(24, true), RATE); assert.equal(v.getUint32(28, true), RATE * 2);
  assert.equal(v.getUint16(34, true), 16); assert.equal(v.getUint32(40, true), 10);
  assert.equal(v.getInt16(44, true), -32767); assert.equal(v.getInt16(52, true), 32767);
});
