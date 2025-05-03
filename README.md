# 🧠 Cuestionario Familiar - Salud Mental

Este proyecto contiene una herramienta interactiva desarrollada en Streamlit para la recogida y evaluación de datos de familiares de personas con problemas de salud mental. El cuestionario está diseñado como parte de una investigación académica y permite recoger, calcular y almacenar automáticamente los resultados.

---

## 🚀 Características principales

- 🌍 Idioma seleccionable (Español / Inglés)
- ✅ Escalas implementadas:
  - DSS-R (Diferenciación del Self)
  - FACES-20Esp (Funcionamiento Familiar)
  - AFPEM (Estigma Familiar)
  - PHQ-4 (Ansiedad y Depresión)
  - Zarit (Sobrecarga)
  - SSQ6, WEMWBS, SCS, satisfacción IA
- 🧮 Cálculo automático de puntuaciones
- 📊 Almacenamiento automático en Google Sheets o archivo local
- 🔐 Opción de anonimización de participantes
- 🧠 Diseñado para su uso en estudios de intervención y evaluación clínica

---

## 📦 Estructura del proyecto

```
cuestionario-familiar/
│
├── app.py               # Aplicación principal de Streamlit
├── correccion.py        # Procesamiento de respuestas y puntuaciones
├── utils.py             # Funciones auxiliares
├── requirements.txt     # Dependencias
└── credentials/
    └── credenciales.json  # Clave para acceso a Google Sheets (no subir al repo público)
```

---

## ▶️ Cómo ejecutarlo localmente

1. Clona este repositorio:
```bash
git clone https://github.com/tu_usuario/cuest-familiar.git
cd cuest-familiar
```

2. Instala dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecuta la app:
```bash
streamlit run app.py
```

---

## 🌐 Despliegue en la web

Puedes desplegar esta app gratis en [Streamlit Cloud](https://share.streamlit.io/) y compartir el enlace con los participantes. Solo necesitas vincular este repositorio.

---

## 🔒 Consideraciones de privacidad

- El sistema puede configurarse para anonimizar datos automáticamente.
- Los resultados pueden almacenarse en Google Sheets o en un archivo privado local / en OneDrive.


