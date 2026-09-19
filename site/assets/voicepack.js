/* Voice packs are stored as lossless 16 kHz FLAC to stay small; EdgeTX wants WAV.
   voiceZip() fetches a pack and returns a JSZip of ready-to-copy SOUNDS/<lang>/*.wav files. */
(function () {
  const RATE = 16000;

  /** 16-bit PCM WAV from per-channel float arrays. FLAC decodes to i/32768, so this round-trips exactly. */
  function wavBytes(channels, rate) {
    const n = channels[0].length, nch = channels.length, bytes = new ArrayBuffer(44 + n * nch * 2), v = new DataView(bytes);
    const str = (at, s) => { for (let i = 0; i < s.length; i++) v.setUint8(at + i, s.charCodeAt(i)); };
    str(0, 'RIFF'); v.setUint32(4, bytes.byteLength - 8, true); str(8, 'WAVE'); str(12, 'fmt ');
    v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, nch, true);
    v.setUint32(24, rate, true); v.setUint32(28, rate * nch * 2, true); v.setUint16(32, nch * 2, true); v.setUint16(34, 16, true);
    str(36, 'data'); v.setUint32(40, n * nch * 2, true);
    for (let i = 0, at = 44; i < n; i++) {
      for (let c = 0; c < nch; c++, at += 2) v.setInt16(at, Math.max(-32768, Math.min(32767, Math.round(channels[c][i] * 32768))), true);
    }
    return bytes;
  }

  const api = { RATE, wavBytes };
  if (typeof module !== 'undefined' && module.exports) { module.exports = api; return; }

  const SB = window.SB;
  /** fetch a voice pack, decode every FLAC to WAV. progress(text) is optional. */
  SB.voiceZip = async (v, progress = () => {}) => {
    progress(`Fetching the ${v.name} voice pack…`);
    const r = await fetch(v.pack); if (!r.ok) throw new Error(`Voice pack: HTTP ${r.status}`);
    const src = await JSZip.loadAsync(await r.arrayBuffer());
    const Offline = window.OfflineAudioContext || window.webkitOfflineAudioContext;
    if (!Offline) throw new Error('this browser cannot decode the voice pack (no Web Audio)');
    const ctx = new Offline(1, 1, RATE);      // decodeAudioData resamples to the context rate
    const out = new JSZip(), names = Object.keys(src.files).filter((n) => !src.files[n].dir);
    let next = 0, done = 0;
    await Promise.all(Array.from({ length: 4 }, async () => {
      while (next < names.length) {
        const name = names[next++], data = await src.file(name).async('arraybuffer');
        if (name.endsWith('.flac')) {
          let audio;
          try { audio = await ctx.decodeAudioData(data); }
          catch (_) { throw new Error(`${name}: this browser cannot decode FLAC. Try Chrome, Firefox or a recent Safari.`); }
          out.file(name.replace(/\.flac$/, '.wav'), wavBytes(Array.from({ length: audio.numberOfChannels }, (_, c) => audio.getChannelData(c)), audio.sampleRate));
        } else out.file(name, data);
        progress(`Converting ${v.name} to WAV… ${++done}/${names.length}`);
      }
    }));
    return out;
  };

  /** the plain "download this voice" button */
  SB.downloadVoice = async (v, progress = () => {}) => {
    const zip = await SB.voiceZip(v, progress);
    progress('Compressing…');
    const blob = await zip.generateAsync({ type: 'blob', compression: 'DEFLATE', compressionOptions: { level: 6 } });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = `edgetx-${v.id}.zip`;
    document.body.appendChild(a); a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 10000);
    progress(`Downloaded ${a.download} (${SB.size(blob.size)}).`);
  };
})();
