/* Welcome Page */

const welcomePage = document.getElementById("welcome-page");

document.getElementById("welcome-btn").addEventListener("click", () => {
  welcomePage.classList.add("leaving");          // fades out (see style.css)
  setTimeout(() => welcomePage.remove(), 300);   // then removed once invisible
});

document.getElementById("quit-btn").addEventListener("click", () => {
  window.pywebview.api.quit();
});