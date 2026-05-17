// ÆM player — multi-pista debug player.
// Web Audio API: AudioContext compartido; cada track tiene un AudioBuffer
// pre-decodeado y al reproducir se crea un AudioBufferSourceNode + GainNode.
// Sync play: todas las sources se programan al mismo audioCtx.currentTime + lookahead.

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// transmission activa — soporta override por URL: /player/?tx=02
const TX = (new URLSearchParams(location.search).get('tx')) || '01';
const BASE = `/transmissions/${TX}/out/`;

// ---------- estado global ----------
const state = {
  ctx: null,                 // AudioContext (lazy init en primer play)
  masterGain: null,
  composition: null,         // { id, manifest, stems_dir, tracks: [TrackState] }
  duration: 0,               // segundos
  isPlaying: false,
  startedAtCtx: 0,           // ctx.currentTime cuando arrancó la sesión actual
  startOffset: 0,            // segundos dentro del tema desde donde arrancó la sesión
  currentTime: 0,            // último valor mostrado (para pausa)
  index: null,               // contenido del index.json de la transmission
  rafId: null,
};

// TrackState = {
//   meta: {name, file, gain, pan, color, peak, rms},
//   buffer: AudioBuffer,
//   source: AudioBufferSourceNode | null,
//   gainNode: GainNode,
//   panNode: StereoPannerNode,
//   muted: bool,
//   soloed: bool,
//   userGain: number,           // multiplicador del slider (1.0 default)
//   row: HTMLElement,
//   canvas: HTMLCanvasElement,
//   playhead: HTMLElement,
//   peaks: Float32Array,        // peaks por bucket para dibujo
// }

// ---------- bootstrap ----------
async function init() {
  setStatus(`cargando index de transmission ${TX}…`);
  try {
    const res = await fetch(`${BASE}index.json`, { cache: 'no-store' });
    state.index = await res.json();
  } catch (err) {
    setStatus(`error cargando ${BASE}index.json: ${err.message}`);
    return;
  }

  const select = $('#comp-select');
  state.index.compositions.forEach((c) => {
    const opt = document.createElement('option');
    opt.value = c.id;
    opt.textContent = c.label || c.id;
    select.appendChild(opt);
  });

  select.addEventListener('change', () => loadComposition(select.value));
  $('#reload').addEventListener('click', () => loadComposition(select.value));

  bindTransport();
  bindKeyboard();

  if (state.index.compositions.length > 0) {
    select.value = state.index.compositions[0].id;
    await loadComposition(select.value);
  }
}

// ---------- carga de composición ----------
async function loadComposition(id) {
  // limpiar estado previo
  stopPlayback();
  state.currentTime = 0;
  state.startOffset = 0;
  $('#seek').value = 0;
  $('#time-current').textContent = '00:00';
  $('#tracks').innerHTML = '';
  state.composition = null;
  showLoading(true);

  const compInfo = state.index.compositions.find((c) => c.id === id);
  if (!compInfo) { setStatus(`composición no encontrada: ${id}`); showLoading(false); return; }

  setStatus(`cargando manifest de ${id}…`);
  let manifest;
  try {
    const res = await fetch(`${BASE}${compInfo.manifest}`, { cache: 'no-store' });
    manifest = await res.json();
  } catch (err) {
    setStatus(`error manifest: ${err.message}`);
    showLoading(false);
    return;
  }

  // crear ctx si no existe
  if (!state.ctx) {
    state.ctx = new (window.AudioContext || window.webkitAudioContext)();
    state.masterGain = state.ctx.createGain();
    state.masterGain.gain.value = parseFloat($('#master-gain').value);
    state.masterGain.connect(state.ctx.destination);
  }

  state.composition = {
    id,
    info: compInfo,
    manifest,
    duration: manifest.duration,
    tracks: [],
  };
  state.duration = manifest.duration;

  // crear filas DOM en orden y arrancar fetch+decode en paralelo
  const tracksEl = $('#tracks');
  const tpl = $('#track-row');

  for (const meta of manifest.tracks) {
    const trackIdx = state.composition.tracks.length;
    const numStr = String(trackIdx + 1).padStart(2, '0');
    const row = tpl.content.firstElementChild.cloneNode(true);
    row.dataset.trackName = meta.name;
    row.dataset.trackNumber = numStr;
    const nameEl = row.querySelector('.track-name');
    nameEl.innerHTML = `<span class="track-num">${numStr}</span><span class="track-label">${meta.name}</span>`;
    row.querySelector('.track-meta').textContent =
      `gain ${meta.gain.toFixed(2)} · pan ${meta.pan.toFixed(2)} · peak ${meta.peak.toFixed(3)} · rms ${meta.rms.toFixed(4)}`;
    if (meta.color) {
      row.style.borderLeft = `3px solid ${meta.color}`;
    }
    tracksEl.appendChild(row);

    const trackState = {
      meta,
      buffer: null,
      source: null,
      gainNode: state.ctx.createGain(),
      panNode: state.ctx.createStereoPanner(),
      muted: false,
      soloed: false,
      userGain: 1.0,
      row,
      canvas: row.querySelector('.waveform'),
      playhead: row.querySelector('.playhead'),
      peaks: null,
    };
    trackState.panNode.pan.value = 0; // ya esta paneado en el WAV
    trackState.gainNode.connect(trackState.panNode);
    trackState.panNode.connect(state.masterGain);

    bindTrackControls(trackState);
    state.composition.tracks.push(trackState);
  }

  // fetch + decode en paralelo
  setStatus(`cargando ${manifest.tracks.length} stems…`);
  await Promise.all(state.composition.tracks.map((t) => loadTrackBuffer(t)));

  // dibujar todas las waveforms una vez decodeadas
  for (const t of state.composition.tracks) {
    drawWaveform(t);
  }
  // redibujar en resize
  if (!state._resizeBound) {
    state._resizeBound = true;
    window.addEventListener('resize', () => {
      if (!state.composition) return;
      for (const t of state.composition.tracks) drawWaveform(t);
    });
  }

  $('#time-total').textContent = formatTime(state.duration);
  $('#time-current').textContent = formatTime(0);
  $('#seek').value = 0;
  setStatus(`listo · ${manifest.tracks.length} stems · ${formatTime(state.duration)} total`);
  showLoading(false);
}

function showLoading(on) {
  const sp = document.getElementById('loading-spinner');
  if (sp) sp.style.display = on ? 'inline-block' : 'none';
  document.body.classList.toggle('loading', !!on);
}

async function loadTrackBuffer(trackState) {
  const url = `${BASE}${state.composition.info.stems_dir}/${trackState.meta.file}`;
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const arr = await res.arrayBuffer();
    trackState.buffer = await state.ctx.decodeAudioData(arr);
    trackState.peaks = computePeaks(trackState.buffer, 1500);
  } catch (err) {
    console.error(`load ${trackState.meta.name}:`, err);
    setStatus(`error cargando ${trackState.meta.name}: ${err.message}`);
  }
}

// ---------- waveforms ----------
function computePeaks(buffer, targetWidth) {
  const ch0 = buffer.getChannelData(0);
  const ch1 = buffer.numberOfChannels > 1 ? buffer.getChannelData(1) : ch0;
  const samplesPerBucket = Math.max(1, Math.floor(ch0.length / targetWidth));
  const buckets = Math.floor(ch0.length / samplesPerBucket);
  // 2 floats por bucket: min, max (mezcla L+R)
  const peaks = new Float32Array(buckets * 2);
  for (let b = 0; b < buckets; b++) {
    let mn = Infinity, mx = -Infinity;
    const start = b * samplesPerBucket;
    const end = start + samplesPerBucket;
    for (let i = start; i < end; i++) {
      const v = (ch0[i] + ch1[i]) * 0.5;
      if (v < mn) mn = v;
      if (v > mx) mx = v;
    }
    peaks[b * 2] = mn;
    peaks[b * 2 + 1] = mx;
  }
  return peaks;
}

function drawWaveform(trackState) {
  const cv = trackState.canvas;
  const dpr = window.devicePixelRatio || 1;
  const cssW = cv.clientWidth;
  const cssH = cv.clientHeight;
  cv.width = Math.floor(cssW * dpr);
  cv.height = Math.floor(cssH * dpr);
  const ctx = cv.getContext('2d');
  ctx.scale(dpr, dpr);

  // fondo
  ctx.fillStyle = '#141821';
  ctx.fillRect(0, 0, cssW, cssH);

  if (!trackState.peaks) return;

  // linea del cero
  ctx.strokeStyle = '#232a39';
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(0, cssH / 2);
  ctx.lineTo(cssW, cssH / 2);
  ctx.stroke();

  // waveform: escalar peaks a cssW
  const peaks = trackState.peaks;
  const buckets = peaks.length / 2;
  const color = trackState.meta.color || '#6ad0e0';
  ctx.fillStyle = color;
  ctx.globalAlpha = 0.85;

  // Auto-scale moderado: peak local llena el ~70% del alto (deja respiracion)
  // y cap a 5x para no exagerar tracks muy bajos. Asi:
  //   - tracks con peak 0.30 → scale 2.3x → ocupa ~70% del alto
  //   - tracks con peak 0.05 → scale 5x (cap) → ocupa ~25% del alto
  //   - tracks con peak 0.70+ → scale 1x → forma natural
  let localMax = 0;
  for (let b = 0; b < buckets; b++) {
    const a = Math.abs(peaks[b * 2]);
    const c = Math.abs(peaks[b * 2 + 1]);
    if (a > localMax) localMax = a;
    if (c > localMax) localMax = c;
  }
  const TARGET_FILL = 0.70;     // peak local llena 70% del alto
  const MAX_SCALE = 5.0;        // cap anti-exageracion
  let scale = 1;
  if (localMax > 0.001) {
    scale = Math.min(TARGET_FILL / localMax, MAX_SCALE);
    if (scale < 1) scale = 1;   // no comprimir si el peak ya supera target
  }

  const mid = cssH / 2;
  for (let x = 0; x < cssW; x++) {
    const b = Math.floor((x / cssW) * buckets);
    const mn = peaks[b * 2] * scale;
    const mx = peaks[b * 2 + 1] * scale;
    const y1 = mid - mx * mid * 0.95;
    const y2 = mid - mn * mid * 0.95;
    ctx.fillRect(x, y1, 1, Math.max(1, y2 - y1));
  }
  ctx.globalAlpha = 1;
}

// ---------- transport ----------
function bindTransport() {
  $('#play').addEventListener('click', togglePlay);
  $('#stop').addEventListener('click', stopPlayback);
  $('#restart').addEventListener('click', () => {
    const wasPlaying = state.isPlaying;
    stopPlayback();
    state.currentTime = 0;
    updateTimeDisplay(0);
    if (wasPlaying) startPlayback(0);
  });

  const seek = $('#seek');
  seek.addEventListener('input', () => {
    if (!state.duration) return;
    const t = (parseFloat(seek.value) / 1000) * state.duration;
    state.currentTime = t;
    updateTimeDisplay(t);
    if (state.isPlaying) {
      stopPlayback({ keepTime: true });
      startPlayback(t);
    }
  });

  const masterGain = $('#master-gain');
  const mgValue = $('#master-gain-value');
  masterGain.addEventListener('input', () => {
    const v = parseFloat(masterGain.value);
    mgValue.textContent = v.toFixed(2);
    if (state.masterGain) state.masterGain.gain.value = v;
  });

  $('#unmute-all').addEventListener('click', () => {
    if (!state.composition) return;
    for (const t of state.composition.tracks) {
      t.muted = false;
      t.row.querySelector('.mute').classList.remove('active');
      t.row.classList.remove('muted');
    }
    applyMuteSolo();
  });
  $('#unsolo-all').addEventListener('click', () => {
    if (!state.composition) return;
    for (const t of state.composition.tracks) {
      t.soloed = false;
      t.row.querySelector('.solo').classList.remove('active');
    }
    applyMuteSolo();
  });
}

function togglePlay() {
  if (state.isPlaying) {
    stopPlayback();
    return;
  }
  // Si el playhead quedo al final del track, rebobinar a 0 antes de play
  if (state.currentTime >= state.duration - 0.01) {
    state.currentTime = 0;
    updateTimeDisplay(0);
  }
  startPlayback(state.currentTime);
}

function startPlayback(offset) {
  if (!state.composition) return;
  if (!state.ctx) return;
  // resume si estaba suspended
  if (state.ctx.state === 'suspended') state.ctx.resume();

  const startAt = state.ctx.currentTime + 0.05;
  state.startedAtCtx = startAt;
  state.startOffset = offset;
  state.currentTime = offset;

  for (const t of state.composition.tracks) {
    if (!t.buffer) continue;
    const src = state.ctx.createBufferSource();
    src.buffer = t.buffer;
    src.connect(t.gainNode);
    try {
      src.start(startAt, offset);
    } catch (e) {
      console.error('start error', t.meta.name, e);
    }
    t.source = src;
  }

  applyMuteSolo();

  state.isPlaying = true;
  $('#play').textContent = '❚❚';
  $('#play').classList.remove('btn-primary');
  setStatus(`reproduciendo desde ${formatTime(offset)}`);
  loop();
}

function stopPlayback({ keepTime = false } = {}) {
  if (!state.composition) {
    state.isPlaying = false;
    return;
  }
  if (!keepTime && state.isPlaying) {
    state.currentTime = currentPlaybackTime();
  }
  for (const t of state.composition.tracks) {
    if (t.source) {
      try { t.source.stop(); } catch (e) {}
      try { t.source.disconnect(); } catch (e) {}
      t.source = null;
    }
  }
  state.isPlaying = false;
  $('#play').textContent = '▶';
  $('#play').classList.add('btn-primary');
  if (state.rafId) { cancelAnimationFrame(state.rafId); state.rafId = null; }
  setStatus(`pausado en ${formatTime(state.currentTime)}`);
}

function currentPlaybackTime() {
  if (!state.isPlaying) return state.currentTime;
  const elapsed = state.ctx.currentTime - state.startedAtCtx;
  return state.startOffset + Math.max(0, elapsed);
}

function loop() {
  const t = currentPlaybackTime();
  if (t >= state.duration) {
    stopPlayback();
    state.currentTime = state.duration;
    updateTimeDisplay(state.duration);
    return;
  }
  updateTimeDisplay(t);
  state.rafId = requestAnimationFrame(loop);
}

function updateTimeDisplay(t) {
  $('#time-current').textContent = formatTime(t);
  if (state.duration > 0) {
    $('#seek').value = Math.round((t / state.duration) * 1000);
  }
  // playheads
  if (state.composition) {
    for (const tr of state.composition.tracks) {
      const w = tr.canvas.clientWidth;
      const x = (t / state.duration) * w;
      tr.playhead.style.left = `${x}px`;
    }
  }
}

// ---------- mute/solo ----------
function bindTrackControls(trackState) {
  const muteBtn = trackState.row.querySelector('.mute');
  const soloBtn = trackState.row.querySelector('.solo');
  muteBtn.addEventListener('click', () => {
    trackState.muted = !trackState.muted;
    muteBtn.classList.toggle('active', trackState.muted);
    trackState.row.classList.toggle('muted', trackState.muted);
    applyMuteSolo();
  });
  soloBtn.addEventListener('click', () => {
    trackState.soloed = !trackState.soloed;
    soloBtn.classList.toggle('active', trackState.soloed);
    applyMuteSolo();
  });

  const slider = trackState.row.querySelector('.gain-slider');
  const valueEl = trackState.row.querySelector('.gain-value');
  slider.addEventListener('input', () => {
    trackState.userGain = parseFloat(slider.value);
    valueEl.textContent = trackState.userGain.toFixed(2);
    applyMuteSolo();
  });

  // click waveform → seek
  const wf = trackState.row.querySelector('.track-waveform-wrap');
  wf.addEventListener('click', (e) => {
    if (!state.duration) return;
    const rect = wf.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const t = (x / rect.width) * state.duration;
    state.currentTime = t;
    updateTimeDisplay(t);
    if (state.isPlaying) {
      stopPlayback({ keepTime: true });
      startPlayback(t);
    }
  });
}

function applyMuteSolo() {
  if (!state.composition) return;
  const anySolo = state.composition.tracks.some((t) => t.soloed);
  for (const t of state.composition.tracks) {
    let g = t.userGain;
    if (anySolo) {
      g = t.soloed ? g : 0;
    } else if (t.muted) {
      g = 0;
    }
    t.gainNode.gain.setTargetAtTime(g, state.ctx.currentTime, 0.01);
  }
}

// ---------- keyboard shortcuts ----------
function bindKeyboard() {
  document.addEventListener('keydown', (e) => {
    if (e.target.matches('input, select, textarea')) return;
    if (e.code === 'Space') {
      e.preventDefault();
      togglePlay();
    }
  });
}

// ---------- helpers ----------
function formatTime(sec) {
  if (!isFinite(sec) || sec < 0) sec = 0;
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function setStatus(msg) {
  $('#status').textContent = msg;
}

window.addEventListener('DOMContentLoaded', init);
