function updateConnection() {
  const offline = !navigator.onLine;
  document.getElementById('offline-notice').hidden = !offline;
  document.querySelectorAll('form[method="post"] button[type="submit"]').forEach(button => {
    button.disabled = offline;
    if (button.dataset.originalText) button.textContent = button.dataset.originalText;
  });
  document.querySelectorAll('form[aria-busy]').forEach(form => form.removeAttribute('aria-busy'));
}
document.addEventListener('submit', event => {
  const form = event.target;
  if (form.method.toLowerCase() !== 'post') return;
  if (!navigator.onLine) {
    event.preventDefault();
    updateConnection();
    return;
  }
  form.setAttribute('aria-busy', 'true');
  const button = event.submitter || form.querySelector('button[type="submit"]');
  if (button) {
    button.dataset.originalText = button.textContent;
    button.textContent = 'Working…';
    button.disabled = true;
  }
});
window.addEventListener('online', updateConnection);
window.addEventListener('offline', updateConnection);
window.addEventListener('pageshow', updateConnection);
updateConnection();

const countdowns = [...document.querySelectorAll('[data-deadline]')];
function updateCountdowns() {
  for (const label of countdowns) {
    const minutes = Math.ceil((Date.parse(label.dataset.deadline) - Date.now()) / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    const remaining = days > 0 ? `${days}d ${hours % 24}h` : `${hours}h ${minutes % 60}m`;
    label.textContent = minutes <= 0 ? 'Closed' : `${minutes <= 10080 ? 'Due soon · ' : ''}${remaining} left`;
    label.classList.toggle('deadline-soon', minutes > 0 && minutes <= 10080);
    label.closest('.deadline-feature').querySelector('[data-calendar-link]').hidden = minutes <= 0;
  }
}
if (countdowns.length) {
  updateCountdowns();
  window.setInterval(updateCountdowns, 15000);
}
