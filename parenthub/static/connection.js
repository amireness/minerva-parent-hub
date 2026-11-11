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
