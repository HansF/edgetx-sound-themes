/* Pure audio operations shared by the recorder and Node tests. */
(function (root) {
  const RATE = 16000;
  function smartTrim(samples, rate = RATE) {
    const duration = samples.length / rate;
    const full = { start: 0, end: duration, confident: false };
    const width = Math.max(1, Math.round(rate * .01));
    const rms = [];
    for (let i = 0; i < samples.length; i += width) {
      let power = 0;
      const end = Math.min(samples.length, i + width);
      for (let j = i; j < end; j++) power += samples[j] ** 2;
      rms.push(Math.sqrt(power / (end - i)));
    }
    if (rms.length < 3) return full;
    const sorted = [...rms].sort((a, b) => a - b);
    const floor = sorted[Math.floor(sorted.length * .2)];
    const peak = sorted[sorted.length - 1];
    if (peak < .001 || peak < floor * 2.5) return full;
    const threshold = Math.max(.001, Math.min(floor * 3, peak * .3), peak * .025);
    // Three consecutive active windows reject clicks without removing speech pauses.
    let first = -1, last = -1;
    for (let i = 0; i < rms.length - 2; i++) {
      if (rms[i] >= threshold && rms[i + 1] >= threshold && rms[i + 2] >= threshold) {
        if (first < 0) first = i;
        last = i + 3;
      }
    }
    if (first < 0) return full;
    return { start: Math.max(0, first * width / rate - .08),
      end: Math.min(duration, last * width / rate + .15), confident: true };
  }
  function render(samples, start, end, rate = RATE) {
    const duration = samples.length / rate;
    if (![start, end].every(Number.isFinite) || start < 0 || end > duration + .00001 || end <= start || end - start > 10.00001) {
      throw new Error('Choose a selection longer than zero and at most 10 seconds.');
    }
    const out = samples.slice(Math.round(start * rate), Math.min(samples.length, Math.round(end * rate)));
    if (!out.length) throw new Error('The selection is too short.');
    const fade = Math.min(Math.floor(out.length / 2), Math.round(rate * .004));
    for (let i = 0; i < fade; i++) { out[i] *= i / fade; out[out.length - 1 - i] *= i / fade; }
    const loud = Array.from(out, x => Math.abs(x)).sort((a, b) => a - b);
    let power = 0, count = 0;
    for (let i = Math.floor(loud.length / 2); i < loud.length; i++) { power += loud[i] ** 2; count++; }
    const rms = Math.sqrt(power / count);
    const peak = loud[loud.length - 1];
    // Limit boost to 12 dB so very quiet/background-only takes aren't amplified excessively.
    const gain = peak ? Math.min(4, 10 ** (-15 / 20) / (rms || 1), 10 ** (-1 / 20) / peak) : 1;
    for (let i = 0; i < out.length; i++) out[i] *= gain;
    return out;
  }
  function wav(samples, rate = RATE) {
    const bytes = new ArrayBuffer(44 + samples.length * 2), v = new DataView(bytes);
    const str = (at, s) => { for (let i = 0; i < s.length; i++) v.setUint8(at + i, s.charCodeAt(i)); };
    str(0, 'RIFF'); v.setUint32(4, bytes.byteLength - 8, true); str(8, 'WAVE'); str(12, 'fmt ');
    v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true);
    v.setUint32(24, rate, true); v.setUint32(28, rate * 2, true); v.setUint16(32, 2, true); v.setUint16(34, 16, true);
    str(36, 'data'); v.setUint32(40, samples.length * 2, true);
    for (let i = 0; i < samples.length; i++) v.setInt16(44 + i * 2, Math.round(Math.max(-1, Math.min(1, samples[i])) * 32767), true);
    return new Blob([bytes], { type: 'audio/wav' });
  }
  // OfflineAudioContext performs band-limited resampling; the mono original is retained for future edits.
  async function decode(blob, context) {
    const decoded = await context.decodeAudioData(await blob.arrayBuffer());
    if (!decoded.length || decoded.duration > 35) throw new Error('Recording could not be decoded or exceeds 35 seconds. Please record again.');
    const Offline = window.OfflineAudioContext || window.webkitOfflineAudioContext;
    const offline = new Offline(1, Math.ceil(decoded.duration * RATE), RATE);
    const mono = offline.createBuffer(1, decoded.length, decoded.sampleRate);
    const data = mono.getChannelData(0);
    for (let c = 0; c < decoded.numberOfChannels; c++) {
      const channel = decoded.getChannelData(c);
      for (let i = 0; i < data.length; i++) data[i] += channel[i] / decoded.numberOfChannels;
    }
    const src = offline.createBufferSource(); src.buffer = mono; src.connect(offline.destination); src.start();
    return (await offline.startRendering()).getChannelData(0).slice();
  }
  const api = { RATE, smartTrim, render, wav, decode };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.MixAudio = api;
})(typeof window !== 'undefined' ? window : globalThis);
