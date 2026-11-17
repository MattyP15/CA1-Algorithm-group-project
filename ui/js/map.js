// ---------- Colours (kept in sync with css/style.css) ----------
const COLOURS = {
  road: "#4a525e",
  start: "#3ddc84",
  end: "#ff5c5c",
  explored: "#2bb3a3",   
  frontier: "#f5a623",   
  route: "#ff3d7f",      
  current: "#ffffff",
};

//simplified street style
const ROAD_STYLES = {
  path:{ color: "#2c333d", weight: 0.8, dashArray: "2 3" },
  minor:{ color: "#353d48", weight: 1.0 },
  medium:{ color: "#4b5462", weight: 1.6 },
  major:{ color: "#8d8473", weight: 2.8 },
};

// ---------- State shared with the other scripts later ----------
const state = {
  graph: null,      // { nodes, edges, bounds } from Python
  startId: null,    // OSM node ID of the start junction
  endId: null,      // OSM node ID of the end junction
  edgeLookup: null, // "smallerId,largerId" -> road shape, for drawing the search
};

// elements, which keeps 20,000 streets smooth to pan and zoom.
const map = L.map("map", {
  preferCanvas: true,
  zoomControl: true,
  attributionControl: true,
});

// The OpenStreetMap licence requires this credit to be visible.
map.attributionControl.setPrefix(false);
map.attributionControl.addAttribution(
  '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
);

// Layers stacked on top of the roads (Leaflet's roads pane is 400, higher = on top).
map.createPane("search").style.zIndex = 450;   // explored / frontier / route
map.createPane("points").style.zIndex = 460;   // start, end, current junction

// Markers for start/end
let startMarker = null;
let endMarker = null;

// ---------- Helpers for drawing the search ----------
function edgeKey(a, b) {
  return a < b ? `${a},${b}` : `${b},${a}`;
}

function nodeLatLng(id) {
  return state.graph.nodes[String(id)];
}

// shape accounting for junctions

function edgeCoords(a, b) {
  return state.edgeLookup.get(edgeKey(a, b)) || [nodeLatLng(a), nodeLatLng(b)];
}

//the roads
function drawRoads(graph) {
  
const groups = { path: [], minor: [], medium: [], major: [] };
  state.edgeLookup = new Map();
  for (const edge of graph.edges) {
    (groups[edge.kind] || groups.minor).push(edge.coords);
    state.edgeLookup.set(edgeKey(edge.u, edge.v), edge.coords);
  }

  
  for (const kind of ["path", "minor", "medium", "major"]) {
    L.polyline(groups[kind], { ...ROAD_STYLES[kind], interactive: false }).addTo(map);
  }
  map.fitBounds(graph.bounds, { padding: [20, 20] });
}

function addLabels(landmarkNames){
  for (const [nodeId, name] of Object.entries(landmarkNames)) {
    const latlng = state.graph.nodes[String(nodeId)];

    if (!latlng) {
      console.warn(`Landmark node ${nodeId} is missing from the graph.`);
      continue;
    }

    const label = document.createElement("span");
    label.textContent = name;

    L.circleMarker(latlng, {
      pane: "points",
      radius: 4,
      color: "#0f1216",
      weight: 1,
      fillColor: "#f5a623",
      fillOpacity: 1,
    })
      .bindTooltip(label, {
        permanent: true,
        direction: "top",
        offset: [0, -4],
      })
      .addTo(map);
  }
}

// ---------- Start / end selection ----------
function makeMarker(latlng, colour) {
  return L.circleMarker(latlng, {
    pane: "points",
    radius: 7,
    color: "#0f1216",       // dark outline so it stands out on the roads
    weight: 2,
    fillColor: colour,
    fillOpacity: 1,
  }).addTo(map);
}

async function handleMapClick(event) {
  if (isAnimating()) return;   // ignore clicks while a search is playing

  const { lat, lng } = event.latlng;


  const nodeId = await window.pywebview.api.nearest_node(lat, lng);
  const clickedLatLng = state.graph.nodes[String(nodeId)];

  if (state.startId === null || state.endId !== null) {
    
    resetPoints();
    state.startId = nodeId;
    startMarker = makeMarker(clickedLatLng, COLOURS.start);
  } else {
    
    state.endId = nodeId;
    endMarker = makeMarker(clickedLatLng, COLOURS.end);
  }

  updateSidebar();
}

function resetPoints() {
  clearAnimation();
  
  if (startMarker) map.removeLayer(startMarker);
  if (endMarker) map.removeLayer(endMarker);
  startMarker = endMarker = null;
  state.startId = state.endId = null;
  updateSidebar();
}

async function startRun() {
  if (state.startId === null || state.endId === null) {
      document.getElementById("hint").innerHTML = "Set both a <b>start</b> and an <b>end</b> first.";
      return;
    }

  clearAnimation();
  document.getElementById("hint").textContent = "Searching…";

  const result = await window.pywebview.api.run_search(state.startId, state.endId);
  document.getElementById("hint").innerHTML =
    "Watching A* search. <b>Teal</b> = explored, <b>amber</b> = frontier.";
  playAnimation(result);
}

// ---------- Sidebar text ----------
function updateSidebar() {
  document.getElementById("start-value").textContent = state.startId ?? "not set";
  document.getElementById("end-value").textContent = state.endId ?? "not set";
  refreshPlaybackButtons();

  const hint = document.getElementById("hint");
  if (state.startId === null) {
    hint.innerHTML = "Click the map to set the <b>start</b>.";
  } else if (state.endId === null) {
    hint.innerHTML = "Now click to set the <b>end</b>.";
  } else {
    hint.innerHTML = "Ready. Click again to choose a new start.";
  }
}

// ---------- Startup ----------
async function initApp() {
  const graph = await window.pywebview.api.get_graph();
  state.graph = graph;

  drawRoads(graph);

  const landmarkNames = await window.pywebview.api.get_landmarks();
  addLabels(landmarkNames);

  document.getElementById("node-count").textContent =
    Object.keys(graph.nodes).length.toLocaleString();
  document.getElementById("edge-count").textContent =
    graph.edges.length.toLocaleString();

  map.on("click", handleMapClick);
  document.getElementById("reset-btn").addEventListener("click", resetPoints);

  document.getElementById("start-btn").addEventListener("click", startRun);
  setupPlayback();
  await setupBookmarks();
  document.getElementById("loading").classList.add("hidden");
}

// Wait
window.addEventListener("pywebviewready", () => {
  initApp().catch((err) => {
    console.error("Startup failed:", err);   // log first, so the real error always shows
    const message = document.querySelector("#loading p");
    if (message) message.textContent = "Failed to load map: " + err;
  });
});
