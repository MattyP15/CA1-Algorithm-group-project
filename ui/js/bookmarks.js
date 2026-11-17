// Draw the saved routes
function renderBookmarks(bookmarks) {
  const list = document.getElementById("bookmark-list");
  list.replaceChildren();                  // remove the old list
  document.getElementById("bookmark-empty").hidden = bookmarks.length > 0;

  for (const bookmark of bookmarks) {
    const item = document.createElement("li");

    // Clicking the name loads the route and runs it.
    const open = document.createElement("button");
    open.className = "open";
    open.type = "button";
    open.title = "Load and run this route";

    const name = document.createElement("b");
    name.textContent = bookmark.name;      // textContent, so a name can't inject HTML
    const details = document.createElement("small");
    details.textContent = `Saved ${bookmark.saved_at}`;

    open.append(name, details);
    open.addEventListener("click", () => loadBookmark(bookmark));

    // The × deletes it.
    const remove = document.createElement("button");
    remove.className = "delete";
    remove.type = "button";
    remove.title = "Delete bookmark";
    remove.setAttribute("aria-label", `Delete ${bookmark.name}`);
    remove.textContent = "×";
    remove.addEventListener("click", async () => {
      renderBookmarks(await window.pywebview.api.delete_bookmark(bookmark.id));
    });

    item.append(open, remove);
    list.append(item);
  }
}

// Save the current start and end under the typed name.
async function saveBookmark() {
  if (state.startId === null || state.endId === null) {
    document.getElementById("hint").innerHTML = "Set a <b>start</b> and <b>end</b> before saving.";
    return;
  }

  const input = document.getElementById("bookmark-name");
  const count = document.getElementById("bookmark-list").children.length;
  const name = input.value.trim() || `Route ${count + 1}`;

  const bookmarks = await window.pywebview.api.save_bookmark(name, state.startId, state.endId);
  input.value = "";
  renderBookmarks(bookmarks);
}

// Put a saved route back on the map and run it.
function loadBookmark(bookmark) {
  const startLatLng = state.graph.nodes[String(bookmark.start)];
  const endLatLng = state.graph.nodes[String(bookmark.end)];

  // A bookmark only works on the map it was saved with.
  if (!startLatLng || !endLatLng) {
    document.getElementById("hint").textContent = "That bookmark was saved on a different map.";
    return;
  }

  resetPoints();
  state.startId = bookmark.start;
  state.endId = bookmark.end;
  startMarker = makeMarker(startLatLng, COLOURS.start);
  endMarker = makeMarker(endLatLng, COLOURS.end);
  updateSidebar();
  startRun();
}

// Called once from init() in map.js.
async function setupBookmarks() {
  document.getElementById("bookmark-btn").addEventListener("click", saveBookmark);
  document.getElementById("bookmark-name").addEventListener("keydown", (event) => {
    if (event.key === "Enter") saveBookmark();
  });
  renderBookmarks(await window.pywebview.api.list_bookmarks());
}
