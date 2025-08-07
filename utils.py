# utils.py
# -*- coding: utf-8 -*-
import os
import random
import logging
import re
import traceback

# --- Definición Inicial de Flags de Disponibilidad ---
# Es crucial definirlas ANTES de los try-except para que existan globalmente
_nltk_available = False
_sumy_available = False
_pymupdf_available = False
_pyautogui_available = False
_rake_available = False
SentimentIntensityAnalyzer = None # Placeholder inicial
PlaintextParser = Tokenizer = LsaSummarizer = Stemmer = get_stop_words = None # Placeholders Sumy
fitz = numpy = None # Placeholders PDF
pyautogui = None # Placeholder Captura
Rake = None # Placeholder Rake

# --- Dependencias Opcionales (Importar y actualizar flags) ---
try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
    _nltk_available = True
    logging.info("Dependencia NLTK cargada.")
except ImportError:
    logging.warning("NLTK no encontrado.")

# Solo intentar importar Sumy si NLTK está disponible (dependencia)
if _nltk_available:
    try:
        from sumy.parsers.plaintext import PlaintextParser
        from sumy.nlp.tokenizers import Tokenizer
        from sumy.summarizers.lsa import LsaSummarizer
        from sumy.nlp.stemmers import Stemmer
        from sumy.utils import get_stop_words
        _sumy_available = True
        logging.info("Dependencia Sumy cargada.")
    except ImportError:
        logging.warning("Sumy no encontrado.")
else:
     logging.warning("Sumy no se intentó cargar porque NLTK falta.")


try:
    import fitz # PyMuPDF
    import numpy # A veces PyMuPDF tiene dependencia indirecta o se usa con él
    _pymupdf_available = True
    logging.info("Dependencias PDF (PyMuPDF/NumPy) cargadas.")
except ImportError:
    logging.warning("PyMuPDF (fitz) o NumPy no encontrado.")

try:
    import pyautogui
    _pyautogui_available = True
    logging.info("Dependencia Captura (PyAutoGUI) cargada.")
except ImportError:
    logging.warning("PyAutoGUI no encontrado.")
except Exception as e:
    logging.warning(f"PyAutoGUI encontrado pero falló al importar ({type(e).__name__}).")

# Solo intentar importar Rake si NLTK está disponible
if _nltk_available:
    try:
        from rake_nltk import Rake
        _rake_available = True
        logging.info("Dependencia Rake-NLTK cargada.")
    except ImportError:
        logging.warning("rake-nltk no encontrado.")
else:
    logging.warning("Rake-NLTK no se intentó cargar porque NLTK falta.")


# --- Constantes y Configuración ---
NLTK_DATA_DIR = os.path.join(os.path.dirname(__file__), 'nltk_data_local')
if _nltk_available and os.path.exists(NLTK_DATA_DIR):
    if NLTK_DATA_DIR not in nltk.data.path:
        try: # Añadir try-except por si falla la manipulación de nltk.data.path
            nltk.data.path.insert(0, NLTK_DATA_DIR)
            logging.info(f"Directorio local NLTK '{NLTK_DATA_DIR}' añadido a las rutas.")
        except Exception as e:
            logging.error(f"No se pudo añadir directorio local NLTK a path: {e}")

VADER_LEXICON_PATH = 'sentiment/vader_lexicon.zip/vader_lexicon/vader_lexicon.txt'
PDF_SUMMARY_MISSING_DEPS_MSG = "Se requieren 'PyMuPDF' (fitz) y 'NumPy' para resumir PDFs."
TEXT_SUMMARY_MISSING_DEPS_MSG = "Se requieren 'sumy' y 'nltk' (punkt, stopwords) para resumir texto."
VADER_MISSING_MSG = "Se requiere 'nltk' (vader_lexicon) para análisis de sentimiento."
SCREENSHOT_MISSING_MSG = "Se requiere 'pyautogui' y 'Pillow' para capturas."
RAKE_MISSING_MSG = "Se requiere 'rake-nltk' y stopwords de NLTK para palabras clave."

# --- Funciones de Comprobación (Revisadas para devolver SIEMPRE tupla) ---

def check_nltk_resource(resource_path_relative):
    """Verifica si un recurso NLTK está disponible. Devuelve bool."""
    # Asegurarse que NLTK se importó correctamente
    if not _nltk_available or not nltk or not hasattr(nltk, 'data'):
        return False
    try:
        nltk.data.find(resource_path_relative)
        return True
    except LookupError:
        return False
    except Exception as e:
        logging.error(f"Error buscando recurso NLTK {resource_path_relative}: {e}")
        return False

def check_vader_prerequisites(error_message):
    """Comprueba VADER. Devuelve SIEMPRE (bool, msg|None)."""
    if not _nltk_available or not SentimentIntensityAnalyzer: # Verificar también la clase
        return False, error_message # Devuelve tupla
    if check_nltk_resource(VADER_LEXICON_PATH):
        try:
            SentimentIntensityAnalyzer() # Intentar instanciar
            return True, None # Devuelve tupla
        except Exception as e:
             logging.error(f"VADER disponible pero falló inicialización: {e}")
             return False, f"Error al inicializar VADER: {e}" # Devuelve tupla
    else:
        return False, error_message + " (Falta vader_lexicon)" # Devuelve tupla

def check_pdf_prerequisites(error_message):
    """Comprueba PyMuPDF/NumPy. Devuelve SIEMPRE (bool, msg|None)."""
    if not _pymupdf_available:
        return False, error_message # Devuelve tupla
    return True, None # Devuelve tupla

def _check_nltk_stopwords(language):
    """Verifica stopwords. Devuelve bool."""
    if not _nltk_available: return False
    try:
        stopwords_path = f'corpora/stopwords/{language}'
        if check_nltk_resource(stopwords_path): return True
        manual_path = os.path.join(NLTK_DATA_DIR, 'corpora', 'stopwords', language)
        if os.path.exists(manual_path): return True
        # Solo loguear si realmente no se encontraron
        logging.debug(f"Stopwords para '{language}' no encontradas.")
        return False
    except Exception as e: logging.error(f"Error comprobando stopwords para '{language}': {e}"); return False

def check_summary_prerequisites(pdf_enabled, text_enabled_base, pdf_msg, text_msg, check_pdf=True, check_text=True, language='english'):
    """Comprueba Sumy/NLTK deps. Devuelve SIEMPRE (bool, msg|None)."""
    # Usar las variables globales definidas al principio
    global _sumy_available, _nltk_available # Declarar explícitamente que usamos las globales

    if check_pdf and not pdf_enabled:
        return False, pdf_msg # Devuelve tupla
    if check_text:
        # Usar los flags globales
        if not _sumy_available or not _nltk_available:
            return False, text_msg # Devuelve tupla
        if not check_nltk_resource('tokenizers/punkt'):
            return False, text_msg + " (Falta 'punkt')" # Devuelve tupla
        if not _check_nltk_stopwords(language):
            return False, text_msg + f" (Faltan stopwords para '{language}')" # Devuelve tupla
    # Si todas las comprobaciones necesarias pasaron
    return True, None # Devuelve tupla

def check_screenshot_prerequisites(error_message):
    """Comprueba PyAutoGUI. Devuelve SIEMPRE (bool, msg|None)."""
    global _pyautogui_available # Usar global
    if not _pyautogui_available:
        return False, error_message # Devuelve tupla
    return True, None # Devuelve tupla

def check_rake_prerequisites(error_message, language='spanish'):
    """Comprueba Rake/NLTK deps. Devuelve SIEMPRE (bool, msg|None)."""
    global _rake_available, _nltk_available # Usar globales
    if not _rake_available or not _nltk_available:
        return False, error_message + " (Falta rake-nltk o nltk base)" # Devuelve tupla
    if not _check_nltk_stopwords(language):
         return False, error_message + f" (Faltan stopwords NLTK para '{language}')" # Devuelve tupla
    return True, None # Devuelve tupla


# --- Funciones de Procesamiento (Revisadas para devolver SIEMPRE tipo esperado) ---

def humanizar_texto_simple(texto): # Devuelve string
    if not texto: return ""
    # ... (resto función igual) ...
    reemplazos = { 'muy': ['bastante', 'realmente'], 'bueno': ['genial', 'excelente'], 'malo': ['terrible', 'horrible'], 'hacer': ['realizar', 'efectuar'], 'decir': ['comentar', 'mencionar'], 'problema': ['inconveniente', 'dificultad'], }
    palabras = texto.split(); nuevas_palabras = []
    for palabra in palabras:
        match = re.match(r'^([^a-zA-Z0-9]*)(.*?)([^a-zA-Z0-9]*)$', palabra)
        if match:
            prefijo, palabra_nucleo, sufijo = match.groups(); palabra_limpia = palabra_nucleo.lower()
            if palabra_limpia in reemplazos and random.random() < 0.3:
                sustituto = random.choice(reemplazos[palabra_limpia])
                if palabra_nucleo and palabra_nucleo[0].isupper(): sustituto = sustituto.capitalize()
                nuevas_palabras.append(prefijo + sustituto + sufijo)
            else: nuevas_palabras.append(palabra)
        else: nuevas_palabras.append(palabra)
    return ' '.join(nuevas_palabras)


def analizar_sentimiento_vader(texto): # Devuelve SIEMPRE dict
    resultado = {'label': 'Error', 'score': None, 'icon': 'bi-emoji-dizzy-fill', 'error': None}
    if not _nltk_available or not SentimentIntensityAnalyzer: resultado['error'] = VADER_MISSING_MSG; return resultado
    if not texto or not texto.strip(): resultado['label'] = 'Vacío'; resultado['icon'] = 'bi-body-text'; return resultado
    try:
        vader_ok, msg = check_vader_prerequisites(VADER_MISSING_MSG)
        if not vader_ok: resultado['error'] = msg; return resultado
        analyzer = SentimentIntensityAnalyzer(); vs = analyzer.polarity_scores(texto); score = vs['compound']
        resultado['score'] = round(score, 3)
        if score >= 0.05: resultado['label'] = 'Positivo'; resultado['icon'] = 'bi-emoji-smile-fill'
        elif score <= -0.05: resultado['label'] = 'Negativo'; resultado['icon'] = 'bi-emoji-frown-fill'
        else: resultado['label'] = 'Neutral'; resultado['icon'] = 'bi-emoji-neutral-fill'
        resultado['error'] = None
    except LookupError as e: logging.error(f"Error VADER - LookupError: {e}"); resultado['error'] = f"Recurso NLTK no encontrado: {e}."
    except Exception as e: logging.error(f"Error inesperado en análisis VADER: {e}\n{traceback.format_exc()}"); resultado['error'] = f"Error inesperado: {type(e).__name__}"
    return resultado

def _cargar_stopwords_manual(lang): # Devuelve set o None
    ruta_stopwords = os.path.join(NLTK_DATA_DIR, 'corpora', 'stopwords', lang)
    if os.path.exists(ruta_stopwords):
        try:
            with open(ruta_stopwords, 'r', encoding='utf-8') as f:
                stopwords = set(word.strip() for word in f if word.strip()); return stopwords
        except Exception as e: logging.warning(f"WARN: No se pudo cargar stopwords manuales: {e}")
    return None

def resumir_texto(texto, num_frases=5, idioma='spanish'): # Devuelve SIEMPRE tupla (str|None, str|None)
    if not _sumy_available or not _nltk_available: return None, TEXT_SUMMARY_MISSING_DEPS_MSG
    if not texto or not texto.strip(): return "", None
    summary_ok, msg = check_summary_prerequisites( True, True, PDF_SUMMARY_MISSING_DEPS_MSG, TEXT_SUMMARY_MISSING_DEPS_MSG, check_pdf=False, check_text=True, language=idioma)
    if not summary_ok: return None, msg
    try:
        parser = PlaintextParser.from_string(texto, Tokenizer(idioma)); stemmer = Stemmer(idioma)
        stopwords = None
        try: stopwords = get_stop_words(idioma)
        except LookupError: stopwords = _cargar_stopwords_manual(idioma)
        except Exception as e: logging.error(f"ERROR obteniendo stopwords: {e}"); stopwords = _cargar_stopwords_manual(idioma)
        if stopwords is None: logging.warning(f"WARN: No se pudieron cargar stopwords para '{idioma}'."); stopwords = set()
        summarizer = LsaSummarizer(stemmer); summarizer.stop_words = stopwords; resumen_frases = summarizer(parser.document, num_frases)
        return " ".join(str(frase) for frase in resumen_frases), None
    except LookupError as e: logging.error(f"Error Sumy - LookupError: {e}."); return None, f"Recurso NLTK no encontrado: {e}."
    except Exception as e: logging.error(f"Error inesperado en resumen texto: {e}\n{traceback.format_exc()}"); return None, f"Error inesperado: {type(e).__name__}"

def resumir_pdf(ruta_pdf, num_frases=5, idioma='spanish'): # Devuelve SIEMPRE tupla (str|None, str|None)
    if not _pymupdf_available: return None, PDF_SUMMARY_MISSING_DEPS_MSG
    if not ruta_pdf or not os.path.exists(ruta_pdf): return None, "Archivo PDF no encontrado."
    texto_extraido = ""; error_extraccion = None
    try:
        with fitz.open(ruta_pdf) as doc:
            for page in doc: texto_pagina = page.get_text("text", sort=True); texto_extraido += texto_pagina + "\n" if texto_pagina else ""
    except fitz.fitz.FileNotFoundError: error_extraccion = f"Error: PyMuPDF no encontró el archivo."
    except Exception as e: error_extraccion = f"Error extrayendo texto: {type(e).__name__}"; logging.error(f"Error extrayendo PDF '{ruta_pdf}': {e}\n{traceback.format_exc()}")
    if error_extraccion: return None, error_extraccion
    if not texto_extraido.strip(): logging.warning(f"WARN: No se extrajo texto del PDF."); return None, "No se pudo extraer texto (¿vacío o imagen?)."
    return resumir_texto(texto_extraido, num_frases, idioma)


def extraer_palabras_clave(texto, idioma='spanish', max_palabras=10): # Devuelve SIEMPRE dict
    resultado = {'keywords': [], 'error': None}
    prereq_ok, msg = check_rake_prerequisites(RAKE_MISSING_MSG, language=idioma)
    if not prereq_ok: resultado['error'] = msg; return resultado
    if not texto or not texto.strip(): resultado['error'] = "El texto está vacío."; return resultado
    try:
        # Rake necesita las stopwords, check_rake_prerequisites las verifica
        r = Rake(language=idioma); r.extract_keywords_from_text(texto)
        ranked_keywords = r.get_ranked_phrases_with_scores()
        resultado['keywords'] = [phrase for score, phrase in ranked_keywords[:max_palabras]]
        resultado['error'] = None
    except Exception as e:
        logging.error(f"Error extrayendo keywords: {e}\n{traceback.format_exc()}")
        resultado['error'] = f"Error inesperado: {type(e).__name__}"
    return resultado


def realizar_captura(ruta_guardado): # Devuelve tupla (bool, str|None)
    if not _pyautogui_available: return False, SCREENSHOT_MISSING_MSG
    try:
        directorio = os.path.dirname(ruta_guardado); os.makedirs(directorio, exist_ok=True)
        screenshot = pyautogui.screenshot(); screenshot.save(ruta_guardado)
        return True, None
    except pyautogui.PyAutoGUIException as e: logging.error(f"Error PyAutoGUI: {e}"); return False, f"Error PyAutoGUI: {e}"
    except Exception as e: logging.error(f"Error inesperado en captura: {e}\n{traceback.format_exc()}"); return False, f"Error inesperado: {type(e).__name__}"