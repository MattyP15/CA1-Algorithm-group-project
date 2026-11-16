// ---------- Layers for the search (on the "search" pane, above the roads) ----------
const exploredLayer = L.polyline([], {
  pane: "search", color: COLOURS.explored, weight: 2.2, opacity: 0.85, interactive: false,
}).addTo(map);
const frontierLayer = L.polyline([], {
  pane: "search", color: COLOURS.frontier, weight: 2, opacity: 0.95, interactive: false,
}).addTo(map);
const routeLayer = L.polyline([], {
  pane: "search", color: COLOURS.route, weight: 5, opacity: 1, interactive: false,
}).addTo(map);
const currentMarker = L.circleMarker([0, 0], {
  pane: "points", radius: 5, color: COLOURS.current, weight: 2,
  fillColor: COLOURS.current, fillOpacity: 0.9, interactive: false,
});

// ---------- Playback state ----------
const playback = {
  result: null,          // the whole run_search() result
  index: 0,              // how many steps have been shown
  playing: false,
  frameId: null,
  lastTime: 0,
  budget: 0,             // part-steps owed since the last frame
  stepsPerSecond: 20,
  exploredSegments: [],  // road shapes already explored
  exploredNodes: new Set(),
  frontier: new Map(),   // node ID -> road shapes leading to it
};

// ---------- One step of A* ----------
function applyStep(step) {
  playback.exploredNodes.add(step.node);

  // The road we arrived along turns teal.
  if (step.parent !== null) {
    playback.exploredSegments.push(edgeCoords(step.parent, step.node));
  }

  // This junction is explored, no longer waiting in the frontier.
  playback.frontier.delete(step.node);

  // Roads to newly found neighbours turn amber.
  for (const next of step.discovered) {
    if (playback.exploredNodes.has(next)) continue;
    if (!playback.frontier.has(next)) playback.frontier.set(next, []);
    playback.frontier.get(next).push(edgeCoords(step.node, next));
  }
}

// Redraw once per frame (not once per step) so fast speeds stay smooth.
function renderPlayback() {
  exploredLayer.setLatLngs(playback.exploredSegments);
  frontierLayer.setLatLngs([...playback.frontier.values()].flat(1));

  const total = playback.result.steps.length;
  const last = playback.result.steps[playback.index - 1];
  if (last) {
    currentMarker.setLatLng(nodeLatLng(last.node));
    if (!map.hasLayer(currentMarker)) currentMarker.addTo(map);
    document.getElementById("g-value").textContent = Math.round(last.g);
    document.getElementById("h-value").textContent = Math.round(last.h);
    document.getElementById("f-value").textContent = Math.round(last.f);
  }
  document.getElementById("progress-value").textContent =
    `${playback.index.toLocaleString()} / ${total.toLocaleString()}`;
  document.getElementById("progress-bar").style.width = `${(playback.index / total) * 100}%`;
}

// ---------- The playback loop (runs every screen frame, ~60 times a second) ----------
function playbackFrame(time) {
  const seconds = (time - playback.lastTime) / 1000;
  playback.lastTime = time;

  //Keep the leftover fraction for next time.
  playback.budget += seconds * playback.stepsPerSecond;
  let due = Math.floor(playback.budget);
  playback.budget -= due;

  const steps = playback.result.steps;
  while (due > 0 && playback.index < steps.length) {
    applyStep(steps[playback.index]);
    playback.index++;
    due--;
  }
  renderPlayback();

  if (playback.index >= steps.length) {
    finishPlayback();
  } else if (playback.playing) {
    playback.frameId = requestAnimationFrame(playbackFrame);
  }
}

function startLoop() {
  playback.playing = true;
  playback.lastTime = performance.now();
  playback.frameId = requestAnimationFrame(playbackFrame);
  refreshPlaybackButtons();
}

function stopLoop() {
  playback.playing = false;
  if (playback.frameId !== null) cancelAnimationFrame(playback.frameId);
  playback.frameId = null;
}

// ---------- End of the search: draw the route ----------
function finishPlayback() {
  stopLoop();
  if (map.hasLayer(currentMarker)) map.removeLayer(currentMarker);
  frontierLayer.setLatLngs([]);          // search is over, nothing is waiting

  const result = playback.result;
  const hint = document.getElementById("hint");
  if (result.found) {
    const segments = [];
    for (let i = 1; i < result.path.length; i++) {
      segments.push(edgeCoords(result.path[i - 1], result.path[i]));
    }
    routeLayer.setLatLngs(segments);

    const km = (result.cost / 1000).toFixed(2);
    hint.innerHTML = `Done: <b>${km} km</b>, ${result.nodes_expanded.toLocaleString()} ` +
                     `junctions explored in ${result.time_ms.toFixed(1)} ms.`;
  } else {
    hint.textContent = "No route exists between these points. Try two other junctions.";
  }
  refreshPlaybackButtons();
}

// ---------- Functions map.js and the buttons use ----------
function playAnimation(result) {
  clearAnimation();
  playback.result = result;
  playback.budget = 1;                   // show the first step straight away
  startLoop();
}

function clearAnimation() {
  stopLoop();
  Object.assign(playback, {
    result: null, index: 0, exploredSegments: [],
    exploredNodes: new Set(), frontier: new Map(),
  });
  exploredLayer.setLatLngs([]);
  frontierLayer.setLatLngs([]);
  routeLayer.setLatLngs([]);
  if (map.hasLayer(currentMarker)) map.removeLayer(currentMarker);
  for (const id of ["g-value", "h-value", "f-value", "progress-value"]) {
    document.getElementById(id).textContent = "–";
  }
  document.getElementById("progress-bar").style.width = "0";
  refreshPlaybackButtons();
}

// true while a search still has steps to show (playing or paused)
function isAnimating() {
  return playback.result !== null && playback.index < playback.result.steps.length;
}

function pauseOrResume() {
  if (playback.playing) {
    stopLoop();
    refreshPlaybackButtons();
  } else if (isAnimating()) {
    startLoop();
  }
}

function stepOnce() {
  if (!isAnimating()) return;
  stopLoop();
  applyStep(playback.result.steps[playback.index]);
  playback.index++;
  renderPlayback();
  if (!isAnimating()) finishPlayback();
  refreshPlaybackButtons();
}

function skipToEnd() {
  if (!isAnimating()) return;
  stopLoop();
  while (playback.index < playback.result.steps.length) {
    applyStep(playback.result.steps[playback.index]);
    playback.index++;
  }
  renderPlayback();
  finishPlayback();
}

// Enable/disable buttons to match what can be done right now.
function refreshPlaybackButtons() {
  const running = isAnimating();
  const pointsSet = state.startId !== null && state.endId !== null;

  document.getElementById("start-btn").disabled = !pointsSet || running;
  document.getElementById("pause-btn").disabled = !running;
  document.getElementById("pause-btn").textContent =
    running && !playback.playing ? "Resume" : "Pause";
  document.getElementById("step-btn").disabled = !running;
  document.getElementById("finish-btn").disabled = !running;
}

// ---------- Speed slider ----------
// Slider 0-100 -> 1 to about 3,000 steps per second. It's logarithmic,
// so the slow end (good for explaining g, h and f) is easy to control.
function sliderToSpeed(value) {
  return Math.pow(10, (value / 100) * 3.5);
}

function formatSpeed(stepsPerSecond) {
  if (stepsPerSecond < 1.05) return "1 step/s";
  const n = stepsPerSecond < 10
    ? stepsPerSecond.toFixed(1)
    : Math.round(stepsPerSecond).toLocaleString();
  return `${n} steps/s`;
}

// Called once from init() in map.js.
function setupPlayback() {
  const slider = document.getElementById("speed-slider");
  const applySpeed = () => {
    playback.stepsPerSecond = sliderToSpeed(Number(slider.value));
    document.getElementById("speed-value").textContent = formatSpeed(playback.stepsPerSecond);
  };
  slider.addEventListener("input", applySpeed);   // takes effect even mid-animation
  applySpeed();

  document.getElementById("pause-btn").addEventListener("click", pauseOrResume);
  document.getElementById("step-btn").addEventListener("click", stepOnce);
  document.getElementById("finish-btn").addEventListener("click", skipToEnd);
  refreshPlaybackButtons();
}