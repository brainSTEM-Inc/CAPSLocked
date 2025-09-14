document.addEventListener("DOMContentLoaded", function () {
  let sunlight = localStorage.getItem('sunlight');
  const themeSwitch = document.getElementById('theme-switch');

  const enableLightMode = () => {
    document.body.classList.add('sunlight');
    localStorage.setItem('sunlight', 'active');
  };

  const disableLightMode = () => {
    document.body.classList.remove('sunlight');
    localStorage.setItem('sunlight', null);
  };

  if (sunlight === 'active') {
    enableLightMode();
  }

  themeSwitch.addEventListener('click', () => {
    sunlight = localStorage.getItem('sunlight');
    if (sunlight !== 'active') {
      enableLightMode();
    } else {
      disableLightMode();
    }
  });
});
