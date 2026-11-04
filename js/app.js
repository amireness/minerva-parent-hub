(function () {
  'use strict';
  const chooser = document.getElementById('age-choice');
  const under18 = document.getElementById('under18-guidance');
  const adult = document.getElementById('adult-guidance');
  const status = document.getElementById('selection-status');
  const offline = document.getElementById('offline-notice');

  function updateChoice() {
    const choice = chooser.value;
    under18.hidden = choice !== 'under18';
    adult.hidden = choice !== 'adult';
    status.textContent = choice === 'under18'
      ? 'Under-18 guidance is shown below.'
      : choice === 'adult'
        ? 'Guidance for applicants aged 18 or older is shown below.'
        : 'Choose an age group to see the relevant guidance.';
  }
  function updateConnection() {
    offline.hidden = navigator.onLine;
  }
  chooser.addEventListener('change', updateChoice);
  window.addEventListener('online', updateConnection);
  window.addEventListener('offline', updateConnection);
  window.addEventListener('pageshow', updateChoice);
  document.getElementById('age-control').hidden = false;
  document.getElementById('no-js-guidance').hidden = true;
  updateChoice();
  updateConnection();
})();