/* ==========================================================================
   styles.css — Personalización para HumanizarIA
   ========================================================================== */

/* Colores de marca */
:root {
  --color-primario: #1976d2;
  --color-acento: #00bcd4;
  --color-fondo: #f9fafb;
}

/* Fondo general */
body {
  background-color: var(--color-fondo);
}

/* Navbar */
.navbar {
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
.navbar-brand {
  font-weight: bold;
  letter-spacing: 1px;
  font-size: 1.35rem;
}

/* Cards */
.card {
  border-radius: 0.75rem;
  box-shadow: 0 2px 16px rgba(0,0,0,0.06);
}

/* Botones personalizados */
.btn-primary, .btn-info, .btn-success, .btn-danger {
  border-radius: 0.5em;
}
.btn-primary {
  background-color: var(--color-primario);
  border: none;
}
.btn-primary:hover, .btn-primary:focus {
  background-color: #115293;
}
.btn-info {
  background-color: var(--color-acento);
  color: #fff;
  border: none;
}
.btn-info:hover, .btn-info:focus {
  background-color: #008ba3;
  color: #fff;
}

/* Campos de texto */
textarea[readonly], input[readonly] {
  background-color: #f3f3f3 !important;
  color: #555;
}

/* Spinner alineado en botones */
.spinner-border {
  vertical-align: -0.125em;
  margin-right: 0.4em;
}

/* Footer */
footer {
  background: #f7f7f7;
  color: #555;
  font-size: 0.98em;
  border-top: 1px solid #e0e0e0;
  margin-top: 4rem;
}

/* Mensajes */
#messages-container .alert {
  max-width: 500px;
  margin: 0 auto 1.5rem auto;
  font-size: 1rem;
}

/* Badges y resultados */
.badge {
  font-size: 1em;
  margin-right: 0.3em;
}
#sentiment-result .badge,
#keywords-result .badge {
  margin-top: 0.5em;
}

/* Responsive */
@media (max-width: 575.98px) {
  h1, h2, .navbar-brand {
    font-size: 1.1em;
  }
  .card {
    margin-bottom: 1.2em;
  }
  main.container {
    padding: 0.5em;
  }
}

a {
  color: var(--color-primario);
}
a:hover {
  color: var(--color-acento);
}
