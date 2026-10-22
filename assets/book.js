document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('main table').forEach(table => {
    const box=table.parentElement;
    if(box&&box.classList.contains('cell-output-display')) box.setAttribute('tabindex','0');
  });
});
