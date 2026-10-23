# LicitaCheck AI

Prototipo MVP para ayudar a las MYPE peruanas a revisar bases de licitaciones públicas y encontrar fragmentos que merecen una revisión adicional.

## Funcionalidades
- Carga de bases en PDF.
- Extracción de texto por página.
- Búsqueda de señales mediante reglas configurables.
- Visualización de evidencia y recomendaciones de revisión.
- Filtro por categoría y descarga de alertas en CSV.
- Lista de verificación para la MYPE.

## Importante
Este MVP usa reglas de detección, no un modelo de IA generativa. Las alertas son señales preliminares y **no prueban direccionamiento, corrupción ni ilegalidad**. No detectar alertas tampoco garantiza que las bases estén libres de problemas. Se necesita validación por una persona con conocimientos de contratación pública.

La detección depende del texto que pueda extraerse del PDF. Los documentos escaneados como imágenes requieren OCR.

## Ejecutar en tu computadora
1. Instala Python 3.10 o posterior.
2. Descarga o clona este repositorio.
3. Abre una terminal en la carpeta del proyecto.
4. Instala dependencias:

   ```bash
   pip install -r requirements.txt
   ```

5. Inicia la aplicación:

   ```bash
   streamlit run app.py
   ```

6. Se abrirá la aplicación en tu navegador.

## Publicar gratis con GitHub y Streamlit Community Cloud
1. Crea un repositorio público en GitHub llamado `licitacheck-ai`.
2. Sube `app.py`, `requirements.txt` y `README.md`.
3. Entra a https://share.streamlit.io/ e inicia sesión con GitHub.
4. Selecciona **Create app**, elige el repositorio y selecciona `app.py`.
5. Publica y comparte la URL generada.

Los nombres de participantes, universidades y países no deben aparecer en el prototipo ni en la presentación si las bases de la hackathon lo prohíben. Usa solo el nombre del equipo.

## Mejoras siguientes
- Integrar OCR para PDF escaneados.
- Añadir IA generativa con recuperación de fragmentos y citas a página.
- Incorporar comparación de precios usando fuentes públicas verificables.
- Añadir referencias a la normativa vigente, con fecha y enlaces oficiales.
- Probar con documentos de ejemplo y revisión de especialistas.
