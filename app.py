import streamlit as st
import re
import io
import csv
from datetime import datetime
from pypdf import PdfReader

st.set_page_config(page_title="LicitaCheck AI", page_icon="🔎", layout="wide")

st.markdown("""
<style>
.main {background-color: #f7f9fc;}
.hero {padding: 1.3rem 1.5rem; border-radius: 16px; background: linear-gradient(120deg,#102a43,#176b87); color:white;}
.hero h1 {color:white; margin:0;}
.hero p {color:#e6f4f8; margin-bottom:0;}
.small-note {font-size: 0.9rem; color:#52606d;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🔎 LicitaCheck AI</h1>
<p>Revisa bases de licitaciones públicas y detecta condiciones que merecen una segunda mirada.</p>
</div>
""", unsafe_allow_html=True)
st.write("")

with st.sidebar:
    st.header("Acerca del prototipo")
    st.write("**Objetivo:** ayudar a las MYPE a revisar documentos de contratación pública.")
    st.info("Esta versión usa extracción de texto y reglas de detección. No determina que exista corrupción ni reemplaza una revisión legal.")
    st.caption("Prototipo demostrativo · Perú")

st.subheader("1. Carga las bases")
uploaded = st.file_uploader("Selecciona un archivo PDF con las bases de la licitación", type=["pdf"])

# Las reglas son señales de revisión, no conclusiones legales.
RULES = [
    {
        "name": "Especificación potencialmente restrictiva",
        "level": "Revisar",
        "patterns": [
            r"únicamente\s+(?:la marca|el modelo|el fabricante)",
            r"marca\s+específica",
            r"modelo\s+específico",
            r"exclusivamente\s+(?:de|del|la marca)",
            r"sin\s+equivalente",
            r"no\s+se\s+aceptarán\s+equivalentes"
        ],
        "why": "Revisa si la especificación está justificada por la necesidad pública y si permite alternativas equivalentes cuando corresponda."
    },
    {
        "name": "Experiencia o requisitos exigentes",
        "level": "Revisar",
        "patterns": [
            r"experiencia\s+mínima\s+(?:de\s+)?\d+\s+años",
            r"contratos\s+similares\s+(?:por|de)\s+un\s+monto",
            r"facturación\s+mínima",
            r"capital\s+social\s+mínimo",
            r"certificación\s+obligatoria"
        ],
        "why": "Comprueba si el requisito es proporcional al objeto y al monto de la contratación, y si está debidamente sustentado."
    },
    {
        "name": "Posible inconsistencia o ambigüedad",
        "level": "Atención",
        "patterns": [
            r"en caso de discrepancia",
            r"a criterio de la entidad",
            r"según lo determine la entidad",
            r"podrá modificarse",
            r"plazo\s+por\s+definir"
        ],
        "why": "Verifica si la condición es clara, objetiva y coherente con el resto de las bases."
    },
    {
        "name": "Plazo que conviene verificar",
        "level": "Atención",
        "patterns": [
            r"plazo\s+de\s+\d+\s+días",
            r"entrega\s+inmediata",
            r"en un plazo no mayor a\s+\d+\s+días"
        ],
        "why": "Contrasta el plazo con la complejidad, el lugar de entrega y las condiciones del procedimiento."
    },
    {
        "name": "Precio o presupuesto por contrastar",
        "level": "Comparar",
        "patterns": [
            r"valor\s+estimado",
            r"valor\s+referencial",
            r"presupuesto\s+(?:total|estimado|referencial)",
            r"monto\s+de\s+la\s+contratación"
        ],
        "why": "Compara el importe con fuentes actuales y comparables, considerando especificaciones, cantidades, impuestos y fecha. La presencia de esta frase no demuestra un sobrecosto."
    }
]

def extract_pdf(file):
    try:
        reader = PdfReader(file)
        pages = []
        for i, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""
            pages.append((i, text))
        return pages
    except Exception as exc:
        st.error(f"No se pudo leer el PDF: {exc}")
        return []

def find_context(text, start, end, radius=180):
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    snippet = re.sub(r"\s+", " ", text[left:right]).strip()
    if left > 0:
        snippet = "…" + snippet
    if right < len(text):
        snippet += "…"
    return snippet

if uploaded:
    pages = extract_pdf(uploaded)
    full_text = "\n".join(t for _, t in pages)
    if not full_text.strip():
        st.error("No se pudo extraer texto. Si el PDF está escaneado como imagen, necesitará OCR antes de analizarlo.")
        st.stop()

    st.success(f"Documento leído: {uploaded.name} · {len(pages)} páginas")
    with st.expander("Vista previa del texto extraído"):
        st.text_area("Primeros 5,000 caracteres", full_text[:5000], height=220)

    if st.button("Analizar posibles riesgos", type="primary", use_container_width=True):
        findings = []
        for page_num, page_text in pages:
            for rule in RULES:
                for pattern in rule["patterns"]:
                    for match in re.finditer(pattern, page_text, flags=re.IGNORECASE):
                        findings.append({
                            "categoria": rule["name"],
                            "prioridad": rule["level"],
                            "pagina": page_num,
                            "evidencia": find_context(page_text, match.start(), match.end()),
                            "recomendacion": rule["why"],
                            "patron": match.group(0)
                        })
        # Evita repetir la misma alerta por categoría/página/evidencia.
        unique = []
        seen = set()
        for f in findings:
            key = (f["categoria"], f["pagina"], f["patron"].lower(), f["evidencia"])
            if key not in seen:
                seen.add(key)
                unique.append(f)
        st.session_state["findings"] = unique
        st.session_state["filename"] = uploaded.name

    if "findings" in st.session_state:
        findings = st.session_state["findings"]
        st.subheader("2. Resultados del análisis")
        c1, c2, c3 = st.columns(3)
        c1.metric("Alertas encontradas", len(findings))
        c2.metric("Páginas analizadas", len(pages))
        c3.metric("Categorías con alertas", len(set(f["categoria"] for f in findings)))

        st.warning("Las alertas son indicios para revisión, no pruebas de direccionamiento, corrupción o ilegalidad. La ausencia de alertas tampoco garantiza que las bases sean correctas.")

        if not findings:
            st.info("No se detectaron coincidencias con las reglas actuales. Esto no garantiza que el documento esté libre de riesgos: revisa también el contexto y los requisitos no detectados por el prototipo.")
        else:
            categories = ["Todas"] + sorted(set(f["categoria"] for f in findings))
            chosen = st.selectbox("Filtrar por categoría", categories)
            shown = findings if chosen == "Todas" else [f for f in findings if f["categoria"] == chosen]
            for idx, f in enumerate(shown, start=1):
                with st.expander(f"{idx}. {f['categoria']} · Página {f['pagina']} · {f['prioridad']}"):
                    st.markdown("**Fragmento encontrado**")
                    st.write(f["evidencia"])
                    st.markdown("**¿Qué conviene revisar?**")
                    st.write(f["recomendacion"])
                    st.caption("Coincidencia detectada: " + f["patron"])

        # CSV para descargar informe simple.
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["categoria", "prioridad", "pagina", "evidencia", "recomendacion", "patron"])
        writer.writeheader()
        writer.writerows(findings)
        st.download_button(
            "Descargar informe de alertas (CSV)",
            data=output.getvalue().encode("utf-8-sig"),
            file_name="informe_licitacheck.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.subheader("3. Lista de verificación para la MYPE")
        checklist = [
            "¿Cada requisito técnico está vinculado a una necesidad justificada?",
            "¿Se permiten alternativas equivalentes cuando corresponda?",
            "¿Los requisitos de experiencia y capacidad son proporcionales al contrato?",
            "¿Las fechas, cantidades, plazos y montos son consistentes en todo el documento?",
            "¿El presupuesto puede compararse con precios actuales de bienes o servicios equivalentes?",
            "¿Se necesita consultar con un especialista en contratación pública?"
        ]
        for item in checklist:
            st.checkbox(item, key="check_" + str(abs(hash(item))))

else:
    st.markdown("### ¿Cómo funciona?")
    col1, col2, col3 = st.columns(3)
    col1.markdown("#### 📄 Carga\nSube las bases en PDF.")
    col2.markdown("#### 🔍 Analiza\nBusca señales que requieren revisión.")
    col3.markdown("#### 📊 Revisa\nLee la evidencia y descarga las alertas.")
    st.info("Para una demostración, utiliza un PDF con texto seleccionable. Los documentos escaneados pueden necesitar OCR.")
    st.markdown('<p class="small-note">Privacidad: el documento se procesa durante la sesión de la aplicación. Evita cargar documentos con datos personales innecesarios.</p>', unsafe_allow_html=True)
