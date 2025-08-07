# forms.py
from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SubmitField, SelectField, IntegerField
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from flask_wtf.file import FileField, FileAllowed, FileRequired

# Formulario principal (solo textarea para referencia AJAX)
class HumanizeForm(FlaskForm):
    texto_principal = TextAreaField(
        'Texto Principal',
        render_kw={"rows": 10, "placeholder": "Ingresa o pega tu texto aquí..."}
    )

# Formulario para resumir texto pegado
class TextSummaryForm(FlaskForm):
    texto_para_resumir = TextAreaField(
        'Texto a Resumir',
        validators=[DataRequired(message="Ingresa el texto que deseas resumir.")],
        render_kw={"rows": 8, "placeholder": "Pega aquí el texto para resumir..."}
    )
    language_text = SelectField(
        'Idioma del Resumen',
        choices=[('spanish', 'Español'), ('english', 'Inglés')],
        default='spanish',
        validators=[DataRequired(message="Selecciona un idioma.")]
    )
    num_sentences_text = IntegerField(
        'Número de Frases',
        default=5,
        validators=[DataRequired(message="Indica el número de frases."), NumberRange(min=1, max=50)]
    )
    submit_text_summary = SubmitField('Resumir Texto Pegado')

# Formulario para resumir PDF
class PDFSummaryForm(FlaskForm):
    archivo_pdf = FileField(
        'Seleccionar Archivo PDF',
        validators=[FileRequired(message="Debes seleccionar un archivo PDF."), FileAllowed(['pdf'], '¡Solo PDF!')]
    )
    language_pdf = SelectField(
        'Idioma del Resumen',
        choices=[('spanish', 'Español'), ('english', 'Inglés')],
        default='spanish',
        validators=[DataRequired(message="Selecciona un idioma.")]
    )
    num_sentences_pdf = IntegerField(
        'Número de Frases',
        default=5,
        validators=[DataRequired(message="Indica el número de frases."), NumberRange(min=1, max=50)]
    )
    submit_pdf = SubmitField('Resumir PDF')

# --- SearchForm ELIMINADO ---

# Formulario para captura de pantalla
class CaptureForm(FlaskForm):
    submit_capture = SubmitField('Capturar Pantalla')

# Formulario para limpiar todo
class ClearForm(FlaskForm):
    submit_clear = SubmitField('Limpiar Todo')