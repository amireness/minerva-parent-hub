const search = document.querySelector('#term-search');
if (search) {
  document.querySelector('#term-search-controls').hidden = false;
  const terms = [...document.querySelectorAll('.aid-term')];
  search.addEventListener('input', () => {
    const words = search.value.toLowerCase().trim().split(/\s+/);
    for (const term of terms) {
      const text = `${term.textContent} ${term.dataset.aliases}`.toLowerCase();
      term.hidden = !words.every(word => text.includes(word));
    }
    const visible = terms.filter(term => !term.hidden).length;
    document.querySelector('#term-search-result').textContent =
      visible ? `${visible} ${visible === 1 ? 'term' : 'terms'} found` : 'No matching terms. Try another word.';
  });
}

const converter = document.querySelector('#demo-converter');
if (converter) {
  converter.hidden = false;
  const factors = { USD: 1, EUR: 0.9, GBP: 0.8, CAD: 1.35 };
  const amount = document.querySelector('#demo-amount');
  const from = document.querySelector('#demo-from');
  const to = document.querySelector('#demo-to');
  const result = document.querySelector('#demo-result');
  function convert() {
    const value = amount.valueAsNumber;
    if (!Number.isFinite(value) || !amount.checkValidity()) {
      amount.setAttribute('aria-invalid', 'true');
      result.textContent = 'Enter an example amount between 0 and 1,000,000,000.';
      return;
    }
    amount.removeAttribute('aria-invalid');
    const rate = factors[to.value] / factors[from.value];
    const format = new Intl.NumberFormat('en-US', { maximumFractionDigits: 6 });
    const money = new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    result.textContent = `${format.format(value)} ${from.value} ≈ ${money.format(value * rate)} ${to.value} at 1 ${from.value} = ${format.format(rate)} ${to.value} (example rate).`;
  }
  document.querySelector('#demo-convert').addEventListener('click', convert);
  converter.addEventListener('input', () => {
    amount.removeAttribute('aria-invalid');
    result.textContent = '';
  });
  convert();
}

const preview = document.querySelector('#student-visibility');
if (preview) {
  function reflectPreview() {
    const choices = [...preview.querySelectorAll('input:checked')].map(input => input.value);
    preview.querySelector('output').textContent = choices.length
      ? `Example parent view: ${choices.join(', ')}.`
      : 'Example parent view: public guides only.';
  }
  preview.addEventListener('change', reflectPreview);
  reflectPreview();
}
if (document.querySelector('[data-aid-overview]') && location.hash) {
  const anchor = location.hash.slice(1);
  const legacy = { 'aid-checklist': 'review', 'document-examples': 'documents',
    'official-aid': 'process', glossary: 'glossary', translations: 'translations', currency: 'currency' };
  const view = anchor.startsWith('step-') ? 'step' : anchor.startsWith('term-') ? 'glossary' : legacy[anchor];
  if (view) {
    const destination = new URL(location.href);
    destination.hash = '';
    destination.searchParams.set('view', view);
    if (anchor.startsWith('step-')) destination.searchParams.set('step', anchor.slice(5));
    if (anchor.startsWith('term-')) destination.searchParams.set('term', anchor.slice(5));
    location.replace(destination);
  } else if (anchor === 'aid-tools') {
    document.querySelector('#aid-tools').open = true;
  }
}
