document.addEventListener('DOMContentLoaded', () => {
    const copySummaryButton = document.getElementById('copy-summary-button');
    const printSummaryButton = document.getElementById('print-summary-button');
    const copyHumanizedButton = document.getElementById('copy-humanized-button');
    const summaryTextContent = document.getElementById('summary-text-content');
    const humanizedTextContent = document.getElementById('humanized-text-content');
    const form = document.getElementById('main-form');
    const loadingIndicator = document.getElementById('loading-indicator');
    const clearSectionButtons = document.querySelectorAll('.button-clear-section');
    const messagesContainer = document.getElementById('messages-container');

    // --- Indicador de Carga ---
    if (form) {
        form.addEventListener('submit', (event) => {
            // Mostrar indicador solo si se presiona un botón de acción principal
            const submitter = event.submitter; // Botón que envió el form
            if (submitter && submitter.classList.contains('action-button')) {
                 if (loadingIndicator) {
                    loadingIndicator.style.display = 'flex';
                 }
            }
             // Pequeña demora para asegurar que el form se envíe antes de ocultar (si es necesario)
             // setTimeout(() => {
             //     if (loadingIndicator) loadingIndicator.style.display = 'none';
             // }, 5000); // Ocultar después de 5s como fallback
        });
    }
     // Ocultar indicador cuando la página se carga completamente (después de una recarga POST)
     window.addEventListener('load', () => {
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
     });


    // --- Copiar al Portapapeles ---
    const copyToClipboard = async (element, button) => {
        if (!element || !navigator.clipboard) {
            alert('Error: No se pudo copiar o el navegador no es compatible.');
            return;
        }
        try {
            await navigator.clipboard.writeText(element.innerText); // Usar innerText para <pre> y <p>
            // Cambiar ícono temporalmente
            if(button){
                const originalIcon = button.innerHTML;
                button.innerHTML = '<i class="fas fa-check"></i>'; // Ícono de check
                setTimeout(() => {
                    button.innerHTML = originalIcon; // Restaurar ícono original
                }, 1500); // Después de 1.5 segundos
            } else {
                 alert('Texto copiado al portapapeles.'); // Fallback si no hay botón
            }

        } catch (err) {
            console.error('Error al copiar texto: ', err);
            alert('Error al copiar texto.');
        }
    };

    if (copySummaryButton && summaryTextContent) {
        copySummaryButton.addEventListener('click', () => copyToClipboard(summaryTextContent, copySummaryButton));
    }

    if (copyHumanizedButton && humanizedTextContent) {
        copyHumanizedButton.addEventListener('click', () => copyToClipboard(humanizedTextContent, copyHumanizedButton));
    }

    // --- Imprimir Resumen ---
    if (printSummaryButton && summaryTextContent) {
        printSummaryButton.addEventListener('click', () => {
            const summaryWindow = window.open('', 'PRINT', 'height=600,width=800');

            summaryWindow.document.write('<html><head><title>Resumen PDF</title>');
            // Incluir estilos básicos para impresión
            summaryWindow.document.write('<style>');
            summaryWindow.document.write(`
                body { font-family: sans-serif; line-height: 1.5; margin: 20px;}
                pre { white-space: pre-wrap; word-wrap: break-word; background-color: #f0f0f0; padding: 15px; border: 1px solid #ccc; border-radius: 5px; }
                h2 { border-bottom: 1px solid #ccc; padding-bottom: 5px;}
                @media print {
                    body { margin: 1cm; } /* Márgenes de impresión */
                }
            `);
            summaryWindow.document.write('</style></head><body>');
            summaryWindow.document.write(`<h2>Resumen de: ${document.querySelector('.summary-results .filename')?.innerText || 'PDF'}</h2>`); // Obtener nombre si existe
            summaryWindow.document.write('<pre>' + summaryTextContent.innerText + '</pre>');
            summaryWindow.document.write('</body></html>');

            summaryWindow.document.close(); // Necesario para IE
            summaryWindow.focus(); // Necesario para algunos navegadores

            // Dar tiempo para cargar antes de imprimir
            setTimeout(() => {
                 summaryWindow.print();
                 summaryWindow.close();
            }, 500);
        });
    }

    // --- Limpiar Secciones Individuales ---
    clearSectionButtons.forEach(button => {
        button.addEventListener('click', (event) => {
             event.preventDefault(); // Prevenir envío del formulario
             const targetSelector = button.getAttribute('data-target');
             const targetElement = document.querySelector(targetSelector);
             if (targetElement) {
                 // Ocultar la sección completa
                 targetElement.style.display = 'none';
                 // Opcional: podrías querer limpiar campos ocultos específicos también,
                 // pero ocultar la sección es más simple visualmente.
             }
             // Limpiar mensajes flash y de error
             if (messagesContainer) {
                messagesContainer.innerHTML = '';
             }
        });
    });

});