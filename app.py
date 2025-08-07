# -*- coding: utf-8 -*-
import os
import logging
import traceback
import datetime
from flask import (
    Flask, render_template, request, flash, redirect, url_for, session, jsonify,
    send_from_directory, get_flashed_messages, current_app # Añadido current_app por si acaso
)
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect # Mantenemos CSRFProtect
# Asegúrate de importar TODOS los forms que necesitas
from forms import (
    HumanizeForm, TextSummaryForm, PDFSummaryForm, CaptureForm, ClearForm
)
# Asegúrate de importar TODAS las funciones y variables de utils necesarias
# humanizaria.py (cerca de línea 17 - CORREGIDO)
from utils import (
    humanizar_texto_simple, analizar_sentimiento_vader,
    resumir_texto, resumir_pdf, realizar_captura, extraer_palabras_clave,
    check_summary_prerequisites, check_vader_prerequisites, # Funciones OK
    check_pdf_prerequisites, check_screenshot_prerequisites, check_rake_prerequisites, # Funciones OK
    PDF_SUMMARY_MISSING_DEPS_MSG, TEXT_SUMMARY_MISSING_DEPS_MSG, # Constantes OK
    VADER_MISSING_MSG, SCREENSHOT_MISSING_MSG, RAKE_MISSING_MSG, # Constantes OK
    NLTK_DATA_DIR, VADER_LEXICON_PATH # Constantes OK (si las necesitas)
    # YA NO importamos _initial_vader_available, etc. desde aquí
)

# --- Configuración Inicial ---
# (Mantenemos la configuración como estaba)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(asctime)s %(module)s: %(message)s')
SECRET_KEY = os.environ.get('SECRET_KEY', '71691978efe6f24850c944896d9080528b1d964ccaf3971dd67bcc4ed9dd4312')
if SECRET_KEY == 'una-clave-secreta-realmente-secreta-para-desarrollo-cambiar-esto':
    logging.warning("ADVERTENCIA DE SEGURIDAD: Usando SECRET_KEY por defecto. ¡CAMBIAR EN PRODUCCIÓN!")

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
logging.info(f"Carpeta uploads configurada en: {app.config['UPLOAD_FOLDER']}")

# Inicializar protección CSRF
csrf = CSRFProtect(app)

# humanizaria.py

# ... (imports, app=Flask, app.config, csrf=CSRFProtect) ...

# --- Comprobaciones de Dependencias ---  <-- El bloque empieza aquí
_initial_vader_available, _ = check_vader_prerequisites(VADER_MISSING_MSG)
_initial_pdf_summary_enabled, _ = check_pdf_prerequisites(PDF_SUMMARY_MISSING_DEPS_MSG)
_initial_text_summary_enabled, _ = check_summary_prerequisites(_initial_pdf_summary_enabled, True, PDF_SUMMARY_MISSING_DEPS_MSG, TEXT_SUMMARY_MISSING_DEPS_MSG, check_pdf=False, check_text=True)
_initial_screenshot_enabled, _ = check_screenshot_prerequisites(SCREENSHOT_MISSING_MSG)
_initial_rake_available, _ = check_rake_prerequisites(RAKE_MISSING_MSG)
# El bloque termina aquí

# Ahora vienen los logs que usan esas variables:
if _initial_vader_available: logging.info("Funcionalidad VADER: OK")
else: logging.warning(f"Funcionalidad VADER: Desactivada ({VADER_MISSING_MSG})")
if _initial_pdf_summary_enabled: logging.info("Funcionalidad Resumen PDF: OK")
else: logging.warning(f"Funcionalidad Resumen PDF: Desactivada ({PDF_SUMMARY_MISSING_DEPS_MSG})")
if _initial_text_summary_enabled: logging.info("Funcionalidad Resumen Texto: OK")
else: logging.warning(f"Funcionalidad Resumen Texto: Desactivada ({TEXT_SUMMARY_MISSING_DEPS_MSG})")
if _initial_screenshot_enabled: logging.info("Funcionalidad Captura: OK")
else: logging.warning(f"Funcionalidad Captura: Desactivada ({SCREENSHOT_MISSING_MSG})")
if _initial_rake_available: logging.info("Funcionalidad Palabras Clave: OK")
else: logging.warning(f"Funcionalidad Palabras Clave: Desactivada ({RAKE_MISSING_MSG})")

# ... (resto de tu código: add_toast, rutas @app.route, etc.) ...


# --- Función Helper para añadir Toasts (Puede permanecer aquí) ---
def add_toast(message, category='info'):
    if 'toast_messages' not in session: session['toast_messages'] = []
    valid_categories = ['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark']
    if category not in valid_categories: category = 'info'
    session['toast_messages'].append({'message': message, 'category': category})
    session.modified = True

# --- Rutas de la Aplicación (Vuelven aquí) ---

@app.route('/', methods=['GET', 'POST'])
def home():
    # --- Instanciar forms ---
    humanize_form = HumanizeForm() # No necesita prefijo si solo hay uno por página
    text_summary_form = TextSummaryForm()
    pdf_summary_form = PDFSummaryForm()
    capture_form = CaptureForm()
    clear_form = ClearForm()

    # --- Leer estado de sesión ---
    # (Mantenemos como estaba)
    texto_original_actual = session.get('texto_original', '')
    texto_humanizado_actual = session.get('texto_humanizado', None) # Puede venir de AJAX o precarga
    pdf_summary_result = session.get('pdf_summary', None)
    # Text summary ahora es principalmente AJAX, no necesitamos leerlo aquí
    # text_summary_result = session.get('text_summary', None)

    # --- LÓGICA POST (Volvemos a la versión anterior) ---
    if request.method == 'POST':
        # Botón Limpiar
        # Usamos name='submit_clear' que definimos en el form/template
        if 'submit_clear' in request.form and clear_form.validate_on_submit():
            logging.info("Procesando ClearForm...")
            session.clear()
            add_toast("Interfaz limpiada.", "success")
            return redirect(url_for('home')) # Vuelve a usar 'home'
        elif 'submit_clear' in request.form: # Fallo CSRF u otro
             add_toast("Error al limpiar.", "danger")
             return redirect(url_for('home'))

        # Botón Resumir PDF (usa name='submit_pdf')
        elif 'submit_pdf' in request.form and pdf_summary_form.validate_on_submit():
            logging.info("Procesando PDFSummaryForm...")
            session.pop('pdf_summary', None)
            archivo = pdf_summary_form.archivo_pdf.data
            nombre_original = archivo.filename if archivo else None

            # --- Validación y Lógica de PDF (Como la tenías antes de Blueprints) ---
            if not archivo or not nombre_original:
                 add_toast("Error: No se seleccionó archivo PDF.", "danger")
                 return redirect(url_for('home')) # Usa 'home'

            # ... (resto de la lógica de limpieza de nombre, validación de extensión) ...
            nombre_original_limpio = nombre_original
            if nombre_original.lower().endswith('.pdf.pdf'):
                nombre_original_limpio = nombre_original[:-4]

            if '.' not in nombre_original_limpio or nombre_original_limpio.rsplit('.', 1)[1].lower() != 'pdf':
                add_toast(f"Error: Solo archivos .pdf permitidos.", "danger")
                return redirect(url_for('home')) # Usa 'home'

            # Check dependencias
            summary_possible, prereq_error_msg = check_pdf_prerequisites(PDF_SUMMARY_MISSING_DEPS_MSG)
            if not summary_possible:
                add_toast(prereq_error_msg, 'danger')
                return redirect(url_for('home')) # Usa 'home'

            nombre_seguro = secure_filename(nombre_original_limpio)
            if not nombre_seguro:
                 add_toast(f"Error: Nombre de archivo inválido.", "danger")
                 return redirect(url_for('home')) # Usa 'home'

            ruta_guardado_absoluta = os.path.join(app.config['UPLOAD_FOLDER'], nombre_seguro) # Usa app.config
            try:
                archivo.seek(0)
                archivo.save(ruta_guardado_absoluta)
                logging.info(f"PDF '{nombre_seguro}' guardado.")
                logging.info(f"Resumiendo PDF: {nombre_seguro}...")
                resumen, error_resumen = resumir_pdf(
                    ruta_guardado_absoluta,
                    pdf_summary_form.num_sentences_pdf.data,
                    pdf_summary_form.language_pdf.data
                )
                if error_resumen:
                    add_toast(f"Error al procesar PDF: {error_resumen}", "danger")
                    logging.error(f"Error en resumir_pdf: {error_resumen}")
                else:
                    add_toast("Resumen PDF generado.", "success")
                    session['pdf_summary'] = resumen
                    session['last_pdf_name'] = nombre_seguro
                    session['last_pdf_summary_lang'] = pdf_summary_form.language_pdf.data
                    session['last_pdf_summary_sentences'] = pdf_summary_form.num_sentences_pdf.data

            except OSError as e:
                 add_toast(f"Error al guardar PDF: {e}", "danger")
                 logging.error(f"OSError guardando PDF:\n{traceback.format_exc()}")
            except Exception as e:
                 add_toast(f"Error inesperado procesando PDF: {e}", "danger")
                 logging.error(f"Excepción procesando PDF:\n{traceback.format_exc()}")

            return redirect(url_for('home')) # Usa 'home'

        elif 'submit_pdf' in request.form: # Falla validación PDF
            # Los errores de campo se mostrarán por WTForms en la plantilla
            add_toast("Error en el formulario PDF. Revisa los campos.", "warning")
            # No redirigir para que se vean los errores inline
            # return redirect(url_for('home')) # NO REDIRIGIR AQUI

        # Botón Capturar Pantalla (usa name='submit_capture')
        elif 'submit_capture' in request.form and capture_form.validate_on_submit():
             logging.info("Procesando Captura...")
             session.pop('screenshot_file', None); session.pop('screenshot_ts', None)
             screenshot_possible, prereq_error_msg = check_screenshot_prerequisites(SCREENSHOT_MISSING_MSG)
             if not screenshot_possible:
                 add_toast(prereq_error_msg, "danger")
             else:
                 ruta_relativa = 'screenshot.png'
                 ruta_absoluta_guardado = os.path.join(app.static_folder, ruta_relativa) # Usa app.static_folder
                 captura_ok, error_captura = realizar_captura(ruta_absoluta_guardado)
                 if captura_ok:
                     add_toast("Captura realizada.", "success")
                     try:
                         timestamp = os.path.getmtime(ruta_absoluta_guardado)
                         session['screenshot_file'] = ruta_relativa
                         session['screenshot_ts'] = timestamp
                     except FileNotFoundError:
                         add_toast("Error: Captura guardada no encontrada.", "danger")
                 else:
                     add_toast(f"Error al capturar: {error_captura}", "danger")
                     logging.error(f"Error en realizar_captura: {error_captura}")
             return redirect(url_for('home')) # Usa 'home'
        elif 'submit_capture' in request.form: # Falla validación Captura
             add_toast("Error en formulario captura.", "danger")
             return redirect(url_for('home')) # Usa 'home'

        else:
             # Si llega un POST que no coincide con ningún botón conocido
             logging.warning(f"WARN: POST recibido pero no coincide con botón submit conocido: {request.form}")
             pass # Simplemente renderiza GET

    # --- LÓGICA GET (Se ejecuta si no es POST o si POST falló validación y no redirigió) ---
    current_year = datetime.datetime.now().year
    flashed_messages = session.pop('toast_messages', []) # Para mostrar toasts

    # Obtener tokens CSRF para pasar a la plantilla para AJAX
    ajax_csrf_token = humanize_form.csrf_token.current_token
    ajax_csrf_token_text_summary = text_summary_form.csrf_token.current_token

    return render_template(
        'index.html',
        # Formularios
        humanize_form=humanize_form,
        text_summary_form=text_summary_form,
        pdf_summary_form=pdf_summary_form,
        capture_form=capture_form,
        clear_form=clear_form,
        # Datos para pre-rellenar o mostrar
        texto_original=texto_original_actual,
        texto_humanizado=texto_humanizado_actual, # Se usa si se recarga la pág con datos en sesión
        pdf_summary=pdf_summary_result,
        # Flags de disponibilidad
        vader_available=_initial_vader_available,
        pdf_summary_enabled=_initial_pdf_summary_enabled,
        text_summary_enabled=_initial_text_summary_enabled,
        screenshot_enabled=_initial_screenshot_enabled,
        rake_available=_initial_rake_available,
        # Mensajes de error de dependencias (para tooltips o alertas)
        RAKE_MISSING_MSG=RAKE_MISSING_MSG,
        PDF_SUMMARY_MISSING_DEPS_MSG=PDF_SUMMARY_MISSING_DEPS_MSG,
        TEXT_SUMMARY_MISSING_DEPS_MSG=TEXT_SUMMARY_MISSING_DEPS_MSG,
        SCREENSHOT_MISSING_MSG=SCREENSHOT_MISSING_MSG,
        # Otros datos
        current_year=current_year,
        flashed_messages=flashed_messages,
        # Tokens CSRF para JS
        ajax_csrf_token=ajax_csrf_token,
        ajax_csrf_token_text_summary=ajax_csrf_token_text_summary
    )


# --- Ruta AJAX para Humanizar y Analizar (Vuelve aquí) ---
@app.route('/ajax/humanize', methods=['POST'])
def ajax_humanize_analyze():
    response_data = {'humanized_text': None, 'sentiment': None, 'error': None}
    status_code = 200
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            response_data['error'] = 'No se recibió texto.'
            status_code = 400
        else:
            texto_original = data.get('text', '')
            session['texto_original'] = texto_original # Guarda en sesión

            humanizado = humanizar_texto_simple(texto_original)
            # Guarda humanizado en sesión por si el usuario recarga la página
            session['texto_humanizado'] = humanizado

            # Limpia datos relacionados si es necesario
            # session.pop('resultados_busqueda', None)

            sentimiento_resultado = {'label': 'No disponible', 'score': None, 'icon': 'bi-question-circle', 'error': None}
            vader_available_now, error_msg = check_vader_prerequisites(VADER_MISSING_MSG)

            if not vader_available_now:
                sentimiento_resultado['error'] = error_msg
                logging.warning(f"AJAX Humanize: VADER no disponible: {error_msg}")
            elif not texto_original.strip():
                sentimiento_resultado['label'] = 'Vacío'
                sentimiento_resultado['icon'] = 'bi-body-text'
                logging.info("AJAX Humanize: Texto vacío para análisis.")
            else:
                try:
                    resultado_vader = analizar_sentimiento_vader(texto_original)
                    # Importante: No sobrescribir 'error' si ya había uno por no disponibilidad
                    if not sentimiento_resultado.get('error'):
                        sentimiento_resultado.update(resultado_vader)
                    if sentimiento_resultado.get('error') and not vader_available_now:
                         pass # Mantener el error de no disponibilidad
                    elif sentimiento_resultado.get('error'):
                        logging.error(f"AJAX Humanize: Error VADER: {sentimiento_resultado['error']}")
                    else:
                        logging.info(f"AJAX Humanize: Sentimiento: {sentimiento_resultado.get('label','N/A')}")
                except Exception as e_inner:
                     logging.error(f"ERROR CRÍTICO (AJAX Humanize VADER): {type(e_inner).__name__}\n{traceback.format_exc()}")
                     sentimiento_resultado = {'label': 'Error Análisis', 'score': None, 'icon': 'bi-exclamation-octagon-fill', 'error': 'Error inesperado analizando.'}

            response_data['humanized_text'] = humanizado
            response_data['sentiment'] = sentimiento_resultado

    except Exception as e_outer:
        logging.error(f"Excepción en /ajax/humanize: {e_outer}\n{traceback.format_exc()}")
        response_data = {'error': 'Error interno del servidor.'}
        status_code = 500

    return jsonify(response_data), status_code


# --- Ruta AJAX para Resumir Texto Pegado (Vuelve aquí) ---
@app.route('/ajax/summarize_text', methods=['POST'])
def ajax_summarize_text():
    response_data = {'summary': None, 'language': None, 'sentences': None, 'error': None}
    status_code = 200
    try:
        data = request.get_json()
        if not data:
            response_data['error'] = 'No se recibieron datos.'
            status_code = 400
        else:
            texto_para_resumir = data.get('text', '').strip()
            idioma_seleccionado = data.get('language', 'spanish')
            num_frases_str = data.get('sentences', '5')
            num_frases = None

            # Validación de Inputs
            if not texto_para_resumir:
                response_data['error'] = 'El texto para resumir está vacío.'
                status_code = 400
            else:
                try:
                    num_frases = int(num_frases_str)
                    if not (1 <= num_frases <= 50): # Ajusta rango si cambiaste el form
                         raise ValueError("Número de frases fuera de rango")
                except (ValueError, TypeError):
                    response_data['error'] = 'Número de frases inválido (debe ser un número entre 1 y 50).'
                    status_code = 400

                if idioma_seleccionado not in ['spanish', 'english']: # Ajusta si soportas más idiomas
                    response_data['error'] = 'Idioma no soportado para resumen.'
                    status_code = 400

            # Si las validaciones pasaron
            if status_code == 200:
                # Limpia resúmenes anteriores de sesión
                session.pop('text_summary', None) # Aunque ahora se maneja en JS, limpiar sesión es buena práctica
                session.pop('pdf_summary', None) # Para evitar confusión en la UI

                # Comprueba prerrequisitos justo antes de usar
                summary_possible, prereq_error_msg = check_summary_prerequisites(
                    _initial_pdf_summary_enabled, # Usa los flags globales comprobados al inicio
                    _initial_text_summary_enabled,
                    PDF_SUMMARY_MISSING_DEPS_MSG,
                    TEXT_SUMMARY_MISSING_DEPS_MSG,
                    check_pdf=False, check_text=True, language=idioma_seleccionado
                )

                if not summary_possible:
                    response_data['error'] = f"Funcionalidad no disponible: {prereq_error_msg}"
                    status_code = 503 # Service Unavailable
                    logging.error(f"AJAX Summarize: Prerrequisitos no cumplidos: {prereq_error_msg}")
                else:
                    try:
                        logging.info(f"AJAX Summarize: Resumiendo texto ({idioma_seleccionado}, {num_frases} frases)...")
                        resumen, error_resumen = resumir_texto(texto_para_resumir, num_frases, idioma_seleccionado)
                        if error_resumen:
                            response_data['error'] = f"Error al resumir: {error_resumen}"
                            status_code = 500
                            logging.error(f"AJAX Summarize: Error en utils.resumir_texto: {error_resumen}")
                        else:
                            response_data['summary'] = resumen
                            response_data['language'] = idioma_seleccionado
                            response_data['sentences'] = num_frases
                            # session['text_summary'] = resumen # No necesario si JS lo muestra
                            logging.info("AJAX Summarize: Resumen generado con éxito.")
                    except Exception as e_inner:
                         logging.error(f"Error CRÍTICO (AJAX Summarize): {type(e_inner).__name__}\n{traceback.format_exc()}")
                         response_data['error'] = f'Error inesperado al resumir: {type(e_inner).__name__}'
                         status_code = 500

    except Exception as e_outer:
        logging.error(f"Excepción en /ajax/summarize_text: {e_outer}\n{traceback.format_exc()}")
        response_data = {'error': 'Error interno del servidor.'}
        status_code = 500

    return jsonify(response_data), status_code


# --- Ruta AJAX para Palabras Clave (Vuelve aquí) ---
@app.route('/ajax/keywords', methods=['POST'])
def ajax_keywords():
    response_data = {'keywords': [], 'error': None}
    status_code = 200
    try:
        # Lee el texto de la sesión (escrito por /ajax/humanize o precargado)
        texto_original = session.get('texto_original', '')

        if not texto_original or not texto_original.strip():
            response_data['error'] = "No hay texto original en la sesión para extraer palabras clave."
            status_code = 400
            logging.warning("AJAX Keywords: Texto vacío en sesión.")
        else:
            # Podrías recibir opciones como idioma o max_keywords del request JSON si quisieras
            idioma = 'spanish' # O detectar/recibir
            max_keywords = 15 # Ajusta si quieres

            rake_ok, msg = check_rake_prerequisites(RAKE_MISSING_MSG, language=idioma)
            if not rake_ok:
                response_data['error'] = f"Funcionalidad no disponible: {msg}"
                status_code = 503 # Service Unavailable
                logging.error(f"AJAX Keywords: Prerrequisitos Rake no cumplidos: {msg}")
            else:
                try:
                    logging.info(f"AJAX Keywords: Extrayendo palabras clave (idioma={idioma}, max={max_keywords})...")
                    resultado = extraer_palabras_clave(texto_original, idioma=idioma, max_palabras=max_keywords)
                    if resultado.get('error'):
                        response_data['error'] = f"Error al extraer: {resultado['error']}"
                        status_code = 500
                        logging.error(f"AJAX Keywords: Error en utils.extraer_palabras_clave: {resultado['error']}")
                    else:
                        response_data['keywords'] = resultado.get('keywords', [])
                        logging.info(f"AJAX Keywords: Extracción exitosa ({len(response_data['keywords'])} palabras).")
                except Exception as e_inner:
                    logging.error(f"Error CRÍTICO (AJAX Keywords): {e_inner}\n{traceback.format_exc()}")
                    response_data['error'] = f'Error inesperado extrayendo palabras clave: {type(e_inner).__name__}'
                    status_code = 500

    except Exception as e_outer:
        logging.error(f"Excepción en /ajax/keywords: {e_outer}\n{traceback.format_exc()}")
        response_data = {'error': 'Error interno del servidor.'}
        status_code = 500

    return jsonify(response_data), status_code


# --- Ruta Acerca de (Vuelve aquí) ---
@app.route('/acerca')
def acerca_de():
    current_year = datetime.datetime.now().year
    # Asegúrate de que tienes 'templates/about.html'
    return render_template('about.html', current_year=current_year)

# --- Punto de entrada (sin cambios) ---
if __name__ == '__main__':
    # Debug True es útil para desarrollo, False para producción
    # host='0.0.0.0' permite acceso desde otros dispositivos en la red
    app.run(debug=True, host='0.0.0.0', port=5000)