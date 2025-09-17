// lightmode.js

const THEME_KEY = "theme";
const DARK = "dark";
const LIGHT = "sunlight";

// Get the <html> element and theme toggle button
const html = document.documentElement;
const button = document.getElementById("theme-switch");

// Get saved theme or fall back to system preference
function getPreferredTheme() {
  const stored = localStorage.getItem(THEME_KEY);
  if (stored) return stored;

  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  return prefersDark ? DARK : LIGHT;
}

// Apply theme to <html> tag and update icon if needed
function applyTheme(theme) {
  if (theme === LIGHT) {
    html.classList.add("sunlight");
  } else {
    html.classList.remove("sunlight");
  }
  html.setAttribute("data-theme", theme);
}

// Toggle between themes
function toggleTheme() {
  const current = html.getAttribute("data-theme") || getPreferredTheme();
  const newTheme = current === DARK ? LIGHT : DARK;

  applyTheme(newTheme);
  localStorage.setItem(THEME_KEY, newTheme);
}

// Listen for theme switch button click
button.addEventListener("click", toggleTheme);

// Sync across tabs
window.addEventListener("storage", (e) => {
  if (e.key === THEME_KEY) {
    applyTheme(e.newValue);
  }
});

// On initial load, apply saved or preferred theme
document.addEventListener("DOMContentLoaded", () => {
  const theme = getPreferredTheme();
  applyTheme(theme);
});
