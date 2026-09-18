/* Stickbeats shared runtime: data, audio player, skins. No framework, no build step. */
(function () {
  const SB = (window.SB = {});
  const PLAY_SVG = '<svg viewBox="0 0 10 12" aria-hidden="true"><path d="M0 0L10 6L0 12Z" fill="currentColor"/></svg>';
  const STOP_SVG = '<svg viewBox="0 0 10 10" aria-hidden="true"><rect width="10" height="10" fill="currentColor"/></svg>';
  SB.PLAY_SVG = PLAY_SVG;

  // ---------------------------------------------------------------- data
  let dataP;
  SB.data = () => (dataP = dataP || fetch("data/themes.json").then((r) => r.json()).then((d) => {
    d.byId = Object.fromEntries(d.themes.map((t) => [t.id, t]));
    d.eventBy = Object.fromEntries(d.events.map((e) => [e.file, e]));
    d.catName = Object.fromEntries(d.categories.map((c) => [c.id, c.name]));
    return d;
  }));
  SB.param = (k) => new URLSearchParams(location.search).get(k);
  SB.size = (b) => (b > 1e6 ? (b / 1e6).toFixed(1) + " MB" : Math.round(b / 1e3) + " KB");
  SB.esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  // ---------------------------------------------------------------- fonts & skins
  const loadedFonts = new Set(["Archivo", "Instrument Sans", "JetBrains Mono"]);
  SB.loadFonts = (fonts) => {
    const need = [...new Set(fonts)].filter((f) => f && !loadedFonts.has(f));
    if (!need.length) return;
    need.forEach((f) => loadedFonts.add(f));
    for (let i = 0; i < need.length; i += 12) {
      const l = document.createElement("link");
      l.rel = "stylesheet";
      l.href = "https://fonts.googleapis.com/css2?" + need.slice(i, i + 12).map((f) => "family=" + encodeURIComponent(f).replace(/%20/g, "+")).join("&") + "&display=swap";
      document.head.appendChild(l);
    }
  };
  function lum(hex) {
    const c = hex.replace("#", "");
    const v = [0, 2, 4].map((i) => parseInt(c.length === 3 ? c[i / 2] + c[i / 2] : c.substr(i, 2), 16) / 255)
      .map((x) => (x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4));
    return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2];
  }
  SB.contrast = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
  /** best text colour on `bg`: the preferred colours if readable, else black/white */
  SB.readable = (bg, ...prefer) => {
    for (const p of prefer) if (p && SB.contrast(p, bg) >= 4.5) return p;
    return SB.contrast("#ffffff", bg) >= SB.contrast("#111111", bg) ? "#ffffff" : "#111111";
  };
  SB.skinVars = (sk) => {
    const onBg = SB.readable(sk.bg, sk.ink, sk.surface);
    const ink = SB.readable(sk.surface, sk.ink);
    return `--t-bg:${sk.bg};--t-surface:${sk.surface};--t-ink:${ink};--t-muted:${sk.muted};--t-accent:${sk.accent};--t-on-bg:${onBg};--t-font:'${sk.font}'`;
  };
  SB.fontStack = (f) => `'${f}', var(--display)`;

  // ---------------------------------------------------------------- audio
  let ctx, cur = null, token = 0;
  const bufs = {};
  const listeners = new Set();
  SB.onPlay = (fn) => listeners.add(fn);
  const emit = (state) => listeners.forEach((fn) => fn(state));
  const actx = () => (ctx = ctx || new (window.AudioContext || window.webkitAudioContext)());
  SB.buffer = (hash) => (bufs[hash] = bufs[hash] || fetch(`audio/${hash}.mp3`).then((r) => r.arrayBuffer()).then((a) => actx().decodeAudioData(a)));

  SB.stop = () => {
    token++;
    if (cur) { try { cur.src.stop(); } catch (e) {} }
    cur = null;
    document.querySelectorAll(".playing").forEach((b) => b.classList.remove("playing"));
    emit({ state: "stop" });
  };
  /** play one clip; resolves when it ends (or is interrupted) */
  SB.play = async (hash, info = {}, el = null, keepQueue = false) => {
    if (!keepQueue) SB.stop();
    const my = token;
    actx().resume();
    const buf = await SB.buffer(hash);
    if (my !== token) return;
    if (cur) { try { cur.src.stop(); } catch (e) {} }
    document.querySelectorAll(".playing").forEach((b) => b.classList.remove("playing"));
    const src = ctx.createBufferSource();
    src.buffer = buf;
    src.connect(ctx.destination);
    const t0 = ctx.currentTime;
    src.start();
    cur = { src, buf, t0, info };
    if (el) el.classList.add("playing");
    emit({ state: "play", buf, t0, info, ctx });
    return new Promise((res) => (src.onended = () => {
      if (cur && cur.src === src) { el && el.classList.remove("playing"); cur = null; emit({ state: "end" }); }
      res();
    }));
  };
  /** items: [{hash, info, el}] played back to back */
  SB.queue = async (items, gap = 260) => {
    SB.stop();
    const my = token;
    for (const it of items) {
      if (my !== token) return;
      await SB.play(it.hash, it.info, it.el, true);
      if (my !== token) return;
      await new Promise((r) => setTimeout(r, gap));
    }
  };
  SB.progress = () => (cur ? Math.min(1, (ctx.currentTime - cur.t0) / cur.buf.duration) : 1);

  // ---------------------------------------------------------------- waveform
  SB.scope = (canvas, colors) => {
    const g = canvas.getContext("2d");
    const size = () => { const r = canvas.getBoundingClientRect(); canvas.width = Math.max(1, r.width * devicePixelRatio); canvas.height = Math.max(1, r.height * devicePixelRatio); };
    size();
    addEventListener("resize", size);
    let buf = null, raf;
    const col = (k) => (typeof colors === "function" ? colors()[k] : colors[k]);
    function draw() {
      const w = canvas.width, h = canvas.height, px = Math.max(2, Math.round(3 * devicePixelRatio));
      g.clearRect(0, 0, w, h);
      if (!buf) { g.fillStyle = col("dim"); for (let x = 0; x < w; x += px) g.fillRect(x, h / 2 - 1, px - 1, 2); return; }
      const d = buf.getChannelData(0), step = d.length / w, p = SB.progress();
      for (let x = 0; x < w; x += px) {
        let m = 0;
        for (let i = Math.floor(x * step); i < Math.floor((x + px) * step); i += 4) m = Math.max(m, Math.abs(d[i] || 0));
        const bh = Math.max(2, Math.min(h, m * h * 1.25));
        g.fillStyle = x / w <= p ? col("ink") : col("dim");
        g.fillRect(x, (h - bh) / 2, px - 1, bh);
      }
      if (p < 1) raf = requestAnimationFrame(draw);
    }
    SB.onPlay((s) => { if (s.state === "play") { buf = s.buf; cancelAnimationFrame(raf); draw(); } else draw(); });
    draw();
  };

  // ---------------------------------------------------------------- UI helpers
  SB.playButton = (label) => `<button class="play" aria-label="${SB.esc(label)}">${PLAY_SVG}</button>`;
  SB.nowbar = () => {
    const bar = document.createElement("div");
    bar.className = "nowbar";
    bar.innerHTML = `<div class="np" aria-live="polite"></div><canvas aria-hidden="true"></canvas><button type="button">Stop</button>`;
    document.body.appendChild(bar);
    bar.querySelector("button").onclick = SB.stop;
    SB.scope(bar.querySelector("canvas"), { ink: "#e9e8e3", dim: "#5d6168" });
    let hide;
    SB.onPlay((s) => {
      if (s.state === "play") { clearTimeout(hide); bar.classList.add("show"); bar.querySelector(".np").textContent = s.info.text || ""; }
      else hide = setTimeout(() => bar.classList.remove("show"), 1600);
    });
  };
  SB.markNav = () => {
    const page = location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll(".nav a").forEach((a) => { if (a.getAttribute("href") === page) a.setAttribute("aria-current", "page"); });
  };
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") SB.stop(); });
})();
