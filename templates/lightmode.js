// lightmode.js

const THEME_KEY = "theme";
const DARK = "dark";
const LIGHT = "sunlight";

const html = document.documentElement;
const button = document.getElementById("theme-switch");

// Get saved theme or system preference
function getPreferredTheme() {
  const stored = localStorage.getItem(THEME_KEY);
  if (stored) return stored;

  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  return prefersDark ? DARK : LIGHT;
}

// Apply theme and update class/attribute
function applyTheme(theme) {
  if (theme === LIGHT) {
    html.classList.add("sunlight");
  } else {
    html.classList.remove("sunlight");
  }
  html.setAttribute("data-theme", theme);
}

// Toggle theme on button click
function toggleTheme() {
  const current = html.getAttribute("data-theme") || getPreferredTheme();
  const newTheme = current === DARK ? LIGHT : DARK;

  applyTheme(newTheme);
  localStorage.setItem(THEME_KEY, newTheme);
}

// Sync theme across tabs/windows
window.addEventListener("storage", (e) => {
  if (e.key === THEME_KEY) {
    applyTheme(e.newValue);
  }
});

// On load, apply saved or preferred theme
document.addEventListener("DOMContentLoaded", () => {
  applyTheme(getPreferredTheme());
  button.addEventListener("click", toggleTheme);
});
