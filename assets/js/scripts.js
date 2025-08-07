// assets/js/scripts.js

document.addEventListener('DOMContentLoaded', () => {
  // Backend URL configuration
  const backendUrl = 'http://localhost:5000'; // Change if backend is deployed elsewhere

  // Function to make API calls to backend
  async function postData(endpoint, payload) {
    try {
      const response = await fetch(`${backendUrl}${endpoint}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      if (!response.ok) throw new Error('Error en la respuesta del servidor');
      return await response.json();
    } catch (error) {
      showMessage('Error: ' + error.message, 'danger');
      return null;
    }
  }
  // Utils para mostrar/ocultar spinner
  function toggleSpinner(spinnerId, show) {
    const spinner = document.getElementById(spinnerId);
    if (spinner) {
      spinner.classList.toggle('d-none', !show);
    }
  }

  // Utils para mostrar mensajes flash temporales
  function showMessage(message, type = 'success', timeout = 3000) {
    const container = document.getElementById('messages-container');
    if (!container) return;
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    alert.textContent = message;

    const btnClose = document.createElement('button');
    btnClose.type = 'button';
    btnClose.className = 'btn-close';
    btnClose.setAttribute('data-bs-dismiss', 'alert');
    btnClose.setAttribute('aria-label', 'Close');

    alert.appendChild(btnClose);
    container.appendChild(alert);

    setTimeout(() => {
      alert.classList.remove('show');
      alert.classList.add('hide');
      setTimeout(() => container.removeChild(alert), 500);
    }, timeout);
  }

  // Función para copiar texto a portapapeles
  function copyTextFromElement(elementId) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const text = el.value || el.textContent;
    if (!text) {
      showMessage('No hay texto para copiar', 'warning');
      return;
    }
    navigator.clipboard.writeText(text).then(() => {
      showMessage('Texto copiado al portapapeles');
    }).catch(() => {
      showMessage('Error al copiar texto', 'danger');
    });
  }

  // Función para limpiar campos de texto y resultados
  function clearFields(fieldIds) {
    fieldIds.forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;
      if (el.tagName === 'TEXTAREA' || el.tagName === 'INPUT') {
        el.value = '';
      } else {
        el.textContent = '';
        el.innerHTML = '';
      }
    });
  }

  // Simula un proceso asincrónico con spinner y luego muestra resultado
  function simulateProcess(spinnerId, callback, delay = 1500) {
    toggleSpinner(spinnerId, true);
    setTimeout(() => {
      toggleSpinner(spinnerId, false);
      callback();
    }, delay);
  }

  // -------- HUMANIZAR Y ANALIZAR --------
  const humanizeBtn = document.getElementById('humanize-btn');
  humanizeBtn.addEventListener('click', async () => {
    const originalText = document.getElementById('text-original').value.trim();
    if (!originalText) {
      showMessage('Por favor, ingresa texto original.', 'warning');
      return;
    }

    toggleSpinner('spinner-humanize', true);
    
    const data = await postData('/humanize', { texto: originalText });
    
    toggleSpinner('spinner-humanize', false);
    
    if (data) {
      document.getElementById('humanized-text').value = data.humanizado;
      
      // Keep the simulated sentiment analysis for now (backend doesn't provide this)
      const sentimentResult = document.getElementById('sentiment-result');
      sentimentResult.innerHTML = `<span class="badge bg-success">Sentimiento: Positivo</span>`;
      showMessage('Texto humanizado correctamente.');
    }
  });

  // -------- EXTRAER PALABRAS CLAVE --------
  const keywordsBtn = document.getElementById('keywords-btn');
  keywordsBtn.addEventListener('click', () => {
    const originalText = document.getElementById('text-original').value.trim();
    if (!originalText) {
      showMessage('Por favor, ingresa texto original para extraer palabras clave.', 'warning');
      return;
    }

    simulateProcess('spinner-keywords', () => {
      // Simular extracción de palabras clave
      const keywordsResult = document.getElementById('keywords-result');
      keywordsResult.innerHTML = `
        <strong>Palabras clave extraídas:</strong> 
        <span class="badge bg-primary">Inteligencia Artificial</span> 
        <span class="badge bg-primary">Tecnología</span> 
        <span class="badge bg-primary">Innovación</span>`;
      showMessage('Palabras clave extraídas.');
    });
  });

  // -------- COPIAR TEXTO HUMANIZADO --------
  const copyHumanizedBtn = document.getElementById('copy-humanized');
  copyHumanizedBtn.addEventListener('click', () => {
    copyTextFromElement('humanized-text');
  });

  // -------- LIMPIAR SECCIÓN HUMANIZAR --------
  const clearHumanizeBtn = document.getElementById('clear-humanize');
  clearHumanizeBtn.addEventListener('click', () => {
    clearFields(['text-original', 'humanized-text', 'sentiment-result', 'keywords-result']);
  });

  // -------- RESUMIR TEXTO --------
  const summaryBtn = document.getElementById('summary-btn');
  summaryBtn.addEventListener('click', async () => {
    const text = document.getElementById('summary-input').value.trim();
    if (!text) {
      showMessage('Por favor, ingresa texto para resumir.', 'warning');
      return;
    }

    const sentences = parseInt(document.getElementById('summary-sentences').value, 10) || 3;
    const language = document.getElementById('summary-language').value;

    toggleSpinner('spinner-summary', true);
    
    const data = await postData('/summary', { texto: text });
    
    toggleSpinner('spinner-summary', false);
    
    if (data) {
      const summaryOutput = document.getElementById('summary-output');
      summaryOutput.value = `Resumen (${language} - ${sentences} frases): ${data.resumen}`;
      showMessage('Resumen generado.');
    }
  });

  // -------- COPIAR RESUMEN --------
  const copySummaryBtn = document.getElementById('copy-summary');
  copySummaryBtn.addEventListener('click', () => {
    copyTextFromElement('summary-output');
  });

  // -------- LIMPIAR RESUMEN --------
  const clearSummaryBtn = document.getElementById('clear-summary');
  clearSummaryBtn.addEventListener('click', () => {
    clearFields(['summary-input', 'summary-output']);
  });

  // -------- SIMULAR CAPTURA DE PANTALLA --------
  const screenshotBtn = document.getElementById('screenshot-btn');
  const screenshotResult = document.getElementById('screenshot-result');
  screenshotBtn.addEventListener('click', () => {
    // Mostrar spinner pequeño en botón mientras "procesa"
    screenshotBtn.disabled = true;
    screenshotBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Capturando...`;

    setTimeout(() => {
      screenshotBtn.disabled = false;
      screenshotBtn.innerHTML = `<i class="fas fa-camera"></i> Simular Captura`;

      // Mostrar imagen de ejemplo
      screenshotResult.innerHTML = `<img src="https://via.placeholder.com/600x300?text=Captura+Simulada" alt="Captura simulada" class="img-fluid rounded shadow-sm" />`;
      showMessage('Captura simulada mostrada.');
    }, 1500);
  });

  // -------- LIMPIAR CAPTURA --------
  const clearCaptureBtn = document.getElementById('clear-capture');
  clearCaptureBtn.addEventListener('click', () => {
    screenshotResult.innerHTML = '';
  });

  // -------- LIMPIAR TODO --------
  const clearAllBtn = document.getElementById('clear-all');
  clearAllBtn.addEventListener('click', () => {
    clearFields([
      'text-original', 'humanized-text', 'sentiment-result', 'keywords-result',
      'summary-input', 'summary-output',
      'screenshot-result'
    ]);
  });
});
