document.addEventListener("DOMContentLoaded", () => {
  const themeSwitch = document.getElementById("theme-switch");
  const root = document.documentElement; // targets <html> for CSS variable scope

  const enableLightMode = () => {
    root.classList.add("sunlight");
    localStorage.setItem("sunlight", "active");
  };

  const disableLightMode = () => {
    root.classList.remove("sunlight");
    localStorage.removeItem("sunlight"); // cleaner than setting to null
  };

  // Apply saved theme on page load
  if (localStorage.getItem("sunlight") === "active") {
    enableLightMode();
  }

  // Toggle theme on button click
  themeSwitch.addEventListener("click", () => {
    if (root.classList.contains("sunlight")) {
      disableLightMode();
    } else {
      enableLightMode();
    }
  });
});
