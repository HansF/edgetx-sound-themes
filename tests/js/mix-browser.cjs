/* Integration checks with real MediaRecorder/Web Audio, isolated storage and synthetic microphone input.
 * npm run test:browser (install browsers with npx playwright install first).
 * Optional: BROWSER=firefox|webkit, BROWSER_EXECUTABLE=/path/to/browser.
 */
const assert = require('node:assert/strict');
const http = require('node:http');
const fs = require('node:fs/promises');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const { chromium, firefox, webkit } = require('playwright');
const JSZip = require('../../site/assets/vendor/jszip.min.js');
const A = require('../../site/assets/mix-audio.js');

(async () => {
  const files = ['SYSTEM/hello', 'armed', ...Array.from({ length: 68 }, (_, i) => `event${i}`)];
  const themes = ['8bit-hero', 'cat-mode'].map((id, i) => ({ id, name: i ? 'Cat Mode' : '8-Bit Hero', category: 'test', clips: Object.fromEntries(files.map(f => [f, 'fixture'])) }));
  const catalogue = { themes, groups: [{ name: 'Events', files }], categories: [{ id: 'test', name: 'Test themes' }], events: files.map(file => ({ file, label: file, role: 'startup', recommendedDuration: 2 })) };
  const voices = { voices: [{ id: 'test-voice', hosted: true, flag: '', name: 'Test Voice', native: 'Dutch', language: 'Dutch', lang: 'nl', packSize: 100, pack: 'fixture-voice.flac.zip' }] };
  const fixtureSamples = new Float32Array(A.RATE / 2).map((_, i) => .1 * Math.sin(i * .1));
  const wav = Buffer.from(await A.wav(fixtureSamples).arrayBuffer());
  // Voice packs ship as 16 kHz FLAC; the page must turn them back into WAV.
  const pcm = wav.subarray(44);
  const flac = execFileSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-f', 's16le', '-ar', '16000', '-ac', '1', '-i', 'pipe:0', '-f', 'flac', 'pipe:1'], { input: pcm, maxBuffer: 1e7 });
  const voiceZip = await new JSZip().file('SOUNDS/nl/SYSTEM/0000.flac', flac).file('README.txt', 'Original voice attribution').generateAsync({ type: 'nodebuffer' });
  const root = path.resolve(__dirname, '../../site');
  const server = http.createServer(async (req, res) => {
    const url = new URL(req.url, 'http://localhost');
    if (url.pathname === '/data/themes.json' || url.pathname === '/data/voices.json') { res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify(url.pathname.includes('themes') ? catalogue : voices)); return; }
    if (url.pathname.startsWith('/wav/')) { res.end(wav); return; }
    if (url.pathname === '/fixture-voice.flac.zip') { res.end(voiceZip); return; }
    const file = path.resolve(root, '.' + url.pathname);
    if (!file.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
    try {
      const data = await fs.readFile(file);
      res.setHeader('Content-Type', ({ '.js': 'text/javascript', '.css': 'text/css', '.html': 'text/html', '.svg': 'image/svg+xml' })[path.extname(file)] || 'application/octet-stream'); res.end(data);
    } catch (_) { res.writeHead(404).end(); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const url = `http://127.0.0.1:${server.address().port}/mix.html`;
  const kind = process.env.BROWSER || 'chromium';
  let browser;
  try {
    browser = await ({ chromium, firefox, webkit })[kind].launch({ headless: true, ...(process.env.BROWSER_EXECUTABLE ? { executablePath: process.env.BROWSER_EXECUTABLE } : {}) });
    const context = await browser.newContext({ acceptDownloads: true });
    await context.route('https://fonts.googleapis.com/**', route => route.abort());
    await context.route('https://fonts.gstatic.com/**', route => route.abort());
    await context.addInitScript(() => {
      window.testStreams = [];
      navigator.mediaDevices.getUserMedia = async () => {
        if (window.denyMic) throw new DOMException('Denied', 'NotAllowedError');
        const ctx = new AudioContext(), oscillator = ctx.createOscillator(), gain = ctx.createGain(), dest = ctx.createMediaStreamDestination();
        oscillator.frequency.value = 440; gain.gain.value = .15; oscillator.connect(gain).connect(dest); oscillator.start(); await ctx.resume();
        window.testStreams.push(dest.stream);
        const track = dest.stream.getAudioTracks()[0], stop = track.stop.bind(track);
        track.stop = () => { stop(); oscillator.stop(); ctx.close(); };
        return dest.stream;
      };
    });
    const page = await context.newPage(), errors = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('dialog', d => d.accept());
    await page.goto(url);
    await page.waitForSelector('tr[data-file]');
    assert.equal(await page.locator('tr[data-file]').count(), 70);
    await page.setViewportSize({ width: 390, height: 844 });
    const first = page.locator('tr[data-file]').first();
    await first.locator('[data-action=record]').click();
    await page.evaluate(() => { window.denyMic = true; });
    await page.locator('#record').click();
    await page.waitForFunction(() => document.querySelector('#editor-status').textContent.includes('denied'));
    await page.evaluate(() => { window.denyMic = false; });
    await page.locator('#record').click();
    await page.waitForFunction(() => !document.querySelector('#stop-record').disabled);
    await page.waitForTimeout(1100);
    await page.locator('#stop-record').click();
    await page.waitForFunction(() => !document.querySelector('#trim-tools').hidden && !document.querySelector('#save-clip').disabled);
    assert.equal(await page.evaluate(() => window.testStreams.every(s => s.getTracks().every(t => t.readyState === 'ended'))), true);
    const previewBox = await page.locator('#preview').boundingBox();
    const editorBox = await page.locator('#editor').boundingBox();
    assert.ok(previewBox.y >= editorBox.y && previewBox.y + previewBox.height <= Math.min(844, editorBox.y + editorBox.height), 'Play recording must be visible after recording without scrolling');
    await page.locator('#preview').click();
    await page.locator('#stop-preview').click();
    await page.locator('#save-clip').click();
    await page.waitForFunction(() => document.querySelector('#saved-state').textContent === 'Saved in this browser.');
    let stored = await page.evaluate(async () => { const p = await MixStore.load(); const c = p.clips.get('SYSTEM/hello'); return { count: p.clips.size, duration: c.end - c.start, original: c.samples.length }; });
    assert.equal(stored.count, 1); assert.ok(stored.duration > .5 && stored.duration < 3);
    await page.reload(); await page.waitForSelector('tr[data-file]');
    assert.match(await first.locator('.clip-state').textContent(), /Your recording/);
    await page.locator('#base').selectOption('cat-mode'); await page.locator('#fill').click();
    assert.match(await first.locator('.clip-state').textContent(), /Your recording/);
    await first.locator('[data-action=edit]').click();
    await page.locator('#trim-start').fill('0.2');
    await page.locator('#trim-end').fill('0.6');
    await page.locator('#save-clip').click();
    await page.waitForFunction(() => document.querySelector('#saved-state').textContent === 'Saved in this browser.');
    stored = await page.evaluate(async () => { const c = (await MixStore.load()).clips.get('SYSTEM/hello'); return { start: c.start, end: c.end, length: c.samples.length, size: c.wav.size }; });
    assert.equal(stored.start, .2); assert.equal(stored.end, .6); assert.ok(stored.length > 9600); assert.equal(stored.size, 44 + 6400 * 2);
    // Cancel must not change the saved take or keep a beforeunload warning alive.
    await first.locator('[data-action=edit]').click(); await page.locator('#trim-start').fill('0.3'); await page.locator('#close-editor').click();
    assert.equal(await page.evaluate(async () => (await MixStore.load()).clips.get('SYSTEM/hello').start), .2);
    // Quota failure leaves the previous transaction intact and permits session export.
    await page.evaluate(() => { window.realSave = MixStore.save; MixStore.save = async () => { throw new DOMException('Full', 'QuotaExceededError'); }; });
    await first.locator('[data-action=edit]').click(); await page.locator('#trim-start').fill('0.1'); await page.locator('#save-clip').click();
    await page.waitForFunction(() => document.querySelector('#saved-state').textContent.startsWith('Not saved'));
    assert.equal(await page.evaluate(async () => (await MixStore.load()).clips.get('SYSTEM/hello').start), .2);
    let downloadPromise = page.waitForEvent('download'); await page.locator('#download').click(); let download = await downloadPromise;
    let zip = await JSZip.loadAsync(await fs.readFile(await download.path()));
    assert.equal(Object.keys(zip.files).filter(f => f.endsWith('.wav')).length, 70);
    let personal = await zip.file('SOUNDS/en/SYSTEM/hello.wav').async('nodebuffer');
    assert.equal(personal.readUInt32LE(24), 16000); assert.equal(personal.readUInt16LE(22), 1); assert.equal(personal.length, 44 + 8000 * 2);
    assert.match(await zip.file('README.txt').async('string'), /Personal recordings: no license/);
    await page.evaluate(() => { MixStore.save = window.realSave; }); await page.locator('#retry-save').click();
    await page.waitForFunction(() => document.querySelector('#saved-state').textContent === 'Saved in this browser.');
    await page.locator('#vbase').selectOption('test-voice');
    downloadPromise = page.waitForEvent('download'); await page.locator('#download').click(); download = await downloadPromise;
    zip = await JSZip.loadAsync(await fs.readFile(await download.path()));
    assert.equal(Object.keys(zip.files).filter(f => f.endsWith('.wav')).length, 71);
    assert.ok(zip.file('SOUNDS/nl/SYSTEM/0000.wav')); assert.ok(zip.file('SOUNDS/nl/SYSTEM/hello.wav'));
    assert.equal(await zip.file('VOICE-README.txt').async('string'), 'Original voice attribution');
    // Legacy links load only theme selections, leaving the local recording untouched.
    await page.goto(url + '#' + '00'.repeat(70)); await page.waitForFunction(() => document.querySelector('#resume') && !document.querySelector('#resume').hidden);
    assert.equal(await first.locator('.clip-state').textContent(), '');
    assert.equal(await page.locator('#resume').isVisible(), true);
    assert.equal(await page.evaluate(async () => (await MixStore.load()).clips.size), 1);
    await page.locator('#resume').click();
    assert.match(await first.locator('.clip-state').textContent(), /Your recording/);
    assert.equal(new URL(page.url()).hash, '');
    await page.setViewportSize({ width: 390, height: 844 });
    await first.locator('[data-action=edit]').click();
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    const box = await page.locator('#editor').boundingBox(); assert.ok(box.width <= 390);
    await page.locator('#trim-start').focus(); await page.keyboard.press('ArrowUp');
    assert.ok(Number(await page.locator('#trim-start').inputValue()) > .1);
    await page.screenshot({ path: `/tmp/stickbeats-mix-${kind}-mobile.png` });
    await page.locator('#close-editor').click();
    await first.locator('[data-action=remove]').click();
    await page.waitForFunction(() => document.querySelector('#saved-state').textContent === 'Saved in this browser.');
    assert.equal(await page.evaluate(async () => (await MixStore.load()).clips.size), 0);
    // Closing while permission is pending must stop a stream that resolves late.
    await first.locator('[data-action=record]').click();
    await page.evaluate(() => {
      window.realGetUserMedia = navigator.mediaDevices.getUserMedia;
      navigator.mediaDevices.getUserMedia = () => new Promise(resolve => { window.finishPermission = resolve; });
    });
    assert.equal(Object.keys(zip.files).filter(f => f.endsWith('.flac')).length, 0);
    assert.deepEqual(new Uint8Array(await zip.file('SOUNDS/nl/SYSTEM/0000.wav').async('uint8array')), new Uint8Array(wav));   // FLAC round trip is lossless
    await page.locator('#record').click();
    await page.waitForFunction(() => !!window.finishPermission);
    await page.locator('#close-editor').click();
    assert.equal(await page.evaluate(async () => {
      let stopped = false;
      window.finishPermission({ getTracks: () => [{ stop: () => { stopped = true; } }] });
      await new Promise(resolve => setTimeout(resolve, 0));
      navigator.mediaDevices.getUserMedia = window.realGetUserMedia;
      return stopped;
    }), true);
    // Keep a long original for retrimming, but never save/export a selection over 10s.
    await page.evaluate(async () => {
      const project = await MixStore.load(), samples = new Float32Array(16000 * 12);
      project.settings.customFiles = ['SYSTEM/hello'];
      project.clips.set('SYSTEM/hello', { samples, start: 0, end: 1, wav: MixAudio.wav(samples.slice(0, 16000)) });
      await MixStore.save(project.settings, project.clips);
    });
    await page.reload(); await page.waitForSelector('tr[data-file]');
    await first.locator('[data-action=edit]').click(); await page.locator('#reset-trim').click();
    assert.equal(await page.locator('#save-clip').isDisabled(), true);
    assert.equal(await page.locator('#download-take').isDisabled(), true);
    await page.locator('#trim-end').fill('10'); assert.equal(await page.locator('#save-clip').isDisabled(), false);
    await page.locator('#close-editor').click();
    await page.route('**/wav/**', route => route.fulfill({ status: 503, body: 'Offline' }));
    await page.locator('#download').click();
    await page.waitForFunction(() => document.querySelector('#status').textContent.startsWith('Download failed'));
    assert.equal(await page.evaluate(async () => (await MixStore.load()).clips.size), 1);
    await page.unroute('**/wav/**');
    // A missing audio record is explicitly reported, with the theme as fallback.
    await page.evaluate(async () => { const project = await MixStore.load(); await MixStore.save(project.settings, new Map()); });
    await page.reload(); await page.waitForSelector('tr[data-file]');
    assert.match(await page.locator('#status').textContent(), /missing or unreadable/);
    assert.equal(await first.locator('.clip-state').textContent(), '');
    assert.deepEqual(errors, []);
    console.log(`${kind}: recording, trim, cancellation, reload, quota recovery, both ZIP modes, shared links and mobile controls passed`);
  } finally { await browser?.close(); await new Promise(resolve => server.close(resolve)); }
})().catch(error => { console.error(error); process.exitCode = 1; });
