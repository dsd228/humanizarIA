// scripts.js — Funcionalidad para HumanizarIA Estático (GitHub Pages)

// Utilidades
function showSpinner(id, show = true) {
  const spinner = document.getElementById(id);
  if (spinner) spinner.classList.toggle('d-none', !show);
}
function showMessage(text, type = "info") {
  const container = document.getElementById('messages-container');
  if (!container) return;
  container.innerHTML = `<div class="alert alert-${type} alert-dismissible fade show" role="alert">
    ${text}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
  </div>`;
}
function copyToClipboard(elementId, btnId) {
  const el = document.getElementById(elementId);
  const btn = document.getElementById(btnId);
  if (!el || !navigator.clipboard) {
    showMessage('No se pudo copiar. Navegador no compatible.', 'danger');
    return;
  }
  navigator.clipboard.writeText(el.value || el.innerText).then(() => {
    if (btn) {
      const icon = btn.querySelector('i');
      const original = icon.className;
      icon.className = 'fas fa-check';
      setTimeout(() => { icon.className = original; }, 1200);
    }
    showMessage('¡Texto copiado al portapapeles!', 'success');
  }).catch(() => showMessage('Error al copiar.', 'danger'));
}
function limpiarCampos(ids) {
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = '';
  });
}
function limpiarResultados(ids) {
  ids.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = '';
  });
}

// Humanizar y Analizar (simulado)
document.getElementById('humanize-btn').addEventListener('click', () => {
  showSpinner('spinner-humanize', true);
  setTimeout(() => {
    document.getElementById('humanized-text').value = 'Este es un texto humanizado de ejemplo.';
    document.getElementById('sentiment-result').innerHTML =
      '<span class="badge bg-success"><i class="fas fa-smile"></i> Sentimiento: Positivo (0.87)</span>';
    showSpinner('spinner-humanize', false);
    showMessage('¡Texto procesado con éxito!', 'success');
  }, 1300);
});

// Extraer palabras clave (simulado)
document.getElementById('keywords-btn').addEventListener('click', () => {
  showSpinner('spinner-keywords', true);
  setTimeout(() => {
    document.getElementById('keywords-result').innerHTML =
      '<strong>Palabras Clave:</strong> <span class="badge bg-info text-dark">IA</span> <span class="badge bg-info text-dark">Ética</span> <span class="badge bg-info text-dark">Trabajo</span>';
    showSpinner('spinner-keywords', false);
    showMessage('¡Palabras clave extraídas!', 'success');
  }, 1000);
});

// Limpiar sección Humanizar
document.getElementById('clear-humanize').addEventListener('click', () => {
  limpiarCampos(['text-original', 'humanized-text']);
  limpiarResultados(['sentiment-result', 'keywords-result']);
});

// Resumir texto (simulado)
document.getElementById('summary-btn').addEventListener('click', () => {
  showSpinner('spinner-summary', true);
  setTimeout(() => {
    document.getElementById('summary-output').value = 'Este es un resumen de ejemplo generado automáticamente.';
    showSpinner('spinner-summary', false);
    showMessage('¡Resumen generado!', 'success');
  }, 1200);
});

// Limpiar sección Resumir
document.getElementById('clear-summary').addEventListener('click', () => {
  limpiarCampos(['summary-input', 'summary-output']);
});

// Copiar textos
document.getElementById('copy-humanized').addEventListener('click', () => {
  copyToClipboard('humanized-text', 'copy-humanized');
});
document.getElementById('copy-summary').addEventListener('click', () => {
  copyToClipboard('summary-output', 'copy-summary');
});

// Captura de pantalla (simulada)
document.getElementById('screenshot-btn').addEventListener('click', () => {
  document.getElementById('screenshot-result').innerHTML =
    '<img src="https://placekitten.com/400/200" alt="Captura simulada" class="img-fluid rounded border" style="max-width:400px;">';
  showMessage('¡Captura simulada generada!', 'info');
});
document.getElementById('clear-capture').addEventListener('click', () => {
  limpiarResultados(['screenshot-result']);
});

// Limpiar toda la interfaz
document.getElementById('clear-all').addEventListener('click', () => {
  limpiarCampos([
    'text-original', 'humanized-text', 'summary-input', 'summary-output'
  ]);
  limpiarResultados([
    'sentiment-result', 'keywords-result', 'screenshot-result'
  ]);
  showMessage('Interfaz limpiada.', 'secondary');
});

// Opcional: Cerrar alertas automáticamente después de unos segundos
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('messages-container');
  if (container) {
    container.addEventListener('DOMNodeInserted', () => {
      setTimeout(() => {
        if (container.firstChild) container.firstChild.classList.remove('show');
      }, 2500);
    });
  }
});

/*
  INSTRUCCIONES PARA GITHUB PAGES:
  1. Sube index.html en la raíz del repositorio.
  2. Sube este archivo JS en assets/js/scripts.js.
  3. Ve a Settings > Pages, selecciona la rama y carpeta raíz, y guarda.
  4. Accede a tu web en https://tuusuario.github.io/tu-repo/
*/
