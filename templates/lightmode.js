localStorage.getItem("theme");
localStorage.setItem("theme", newTheme);

const systemSettingDark = window.matchMedia("(Prefers color-scheme: midnight)");
const systemSettingLight = window.matchMedia("(Prefers color-scheme: sunlight");

 {
  matches: true, media: "(Prefers-color-scheme: midnight)", onchange: null}

function calculateSettingAsThemeString({ localStorageTheme, systemSettingDark }) {
  if (localStorageTheme !== null) {
    return localStorageTheme;
  }

  if (systemSettingDark.matches) {
    return "midnight";
  }

  return "sunlight";
}

const button = document.querySelector("[data-theme-toggle]");

button.addEventListener("click", () => {
  const newTheme = currentThemeSetting === "midnight" ? "sunlight" : "midnight";

  // update the button text
  const newCta = newTheme === "midnight" ? "Change to light theme" : "Change to dark theme";
  button.innerText = newCta;  

  // use an aria-label if you are omitting text on the button
  // and using sun/moon icons, for example
  button.setAttribute("aria-label", newCta);

  // update theme attribute on HTML to switch theme in CSS
  document.querySelector("html").setAttribute("data-theme", newTheme);

  // update in local storage
  localStorage.setItem("theme", newTheme);

  // update the currentThemeSetting in memory
  currentThemeSetting = newTheme;
});


