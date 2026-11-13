// ---------- Colours (kept in sync with css/style.css) ----------
const COLOURS = {
  road: "#4a525e",
  start: "#3ddc84",
  end: "#ff5c5c",
};

// ---------- State shared with the other scripts later ----------
const state = {
  graph: null,      // { nodes, edges, bounds } from Python
  startId: null,    // OSM node ID of the start junction
  endId: null,      // OSM node ID of the end junction
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

// Markers for the two chosen points (created when first needed).
let startMarker = null;
let endMarker = null;
let solutionPath = null;

// ---------- Draw the road network ----------
function drawRoads(graph) {
  // One polyline holding every street is far faster than 20,000 separate ones.
  const allStreets = graph.edges.map((edge) => edge.coords);

  L.polyline(allStreets, {
    color: COLOURS.road,
    weight: 1.2,
    opacity: 0.9,
    interactive: false,   // clicks go to the map, not the lines
  }).addTo(map);

  map.fitBounds(graph.bounds, { padding: [20, 20] });
}

function drawSolution(coords) {
    if (solutionPath) map.removeLayer(solutionPath);

    solutionPath = L.polyline(coords, { color: "#4da3ff", weight: 5 }).addTo(map);


}


// ---------- Start / end selection ----------
function makeMarker(latlng, colour) {
  return L.circleMarker(latlng, {
    radius: 7,
    color: "#0f1216",       // dark outline so it stands out on the roads
    weight: 2,
    fillColor: colour,
    fillOpacity: 1,
  }).addTo(map);
}

async function handleMapClick(event) {
  const { lat, lng } = event.latlng;

  // Ask Python which junction is closest to where the user clicked.
  const nodeId = await window.pywebview.api.nearest_node(lat, lng);
  const nodeLatLng = state.graph.nodes[String(nodeId)];

  if (state.startId === null || state.endId !== null) {
    // First click, or both are already set: (re)start with a new start point.
    resetPoints();
    state.startId = nodeId;
    startMarker = makeMarker(nodeLatLng, COLOURS.start);
  } else {
    // Second click: set the end point.
    state.endId = nodeId;
    endMarker = makeMarker(nodeLatLng, COLOURS.end);
  }

  updateSidebar();
}

function resetPoints() {
  if (solutionPath) map.removeLayer(solutionPath);
  solutionPath = null;
  
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

  const coords = await window.pywebview.api.find_path(state.startId, state.endId);
  if (coords === null) {
      document.getElementById("hint").textContent = "No route found.";
      return;
    }
  drawSolution(coords);
}

// ---------- Sidebar text ----------
function updateSidebar() {
  document.getElementById("start-value").textContent = state.startId ?? "not set";
  document.getElementById("end-value").textContent = state.endId ?? "not set";

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
async function init() {
  const graph = await window.pywebview.api.get_graph();
  state.graph = graph;

  drawRoads(graph);

  document.getElementById("node-count").textContent =
    Object.keys(graph.nodes).length.toLocaleString();
  document.getElementById("edge-count").textContent =
    graph.edges.length.toLocaleString();

  map.on("click", handleMapClick);
  document.getElementById("reset-btn").addEventListener("click", resetPoints);

  document.getElementById("start-btn").addEventListener("click", startRun);

  document.getElementById("loading").classList.add("hidden");
}

// Wait until pywebview has connected the Python API, then start.
window.addEventListener("pywebviewready", () => {
  init().catch((err) => {
    document.querySelector("#loading p").textContent = "Failed to load map: " + err;
    console.error(err);
  });
});
