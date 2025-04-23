import os
import streamlit as st
import base64
from openai import OpenAI

# Función para codificar imagen a base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="🔍 Análisis de Imagen con IA",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# TÍTULO Y DESCRIPCIÓN
st.title("🧠 Análisis de Imagen con GPT-4o")
st.markdown("Sube una imagen y deja que la inteligencia artificial describa lo que ve 👁️‍🗨️")

# SECCIÓN PARA API KEY
st.markdown("### 🔐 Ingresa tu Clave de OpenAI")
ke = st.text_input(
    'Clave de API de OpenAI:',
    type="password",
    help="Puedes obtener tu clave en https://platform.openai.com/account/api-keys"
)

# Guardar la clave en una variable de entorno
if ke:
    os.environ['OPENAI_API_KEY'] = ke
    api_key = ke
else:
    st.warning("Por favor, ingresa tu clave de API para continuar.")
    api_key = None

# Inicializar cliente OpenAI si la clave fue ingresada
if api_key:
    client = OpenAI(api_key=api_key)

# SUBIDA DE IMAGEN
uploaded_file = st.file_uploader("📤 Sube una imagen (JPG, PNG, JPEG)", type=["jpg", "png", "jpeg"])

# Mostrar la imagen cargada
if uploaded_file:
    with st.expander("📸 Vista previa de la imagen", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# CONTEXTO ADICIONAL
show_details = st.toggle("📝 ¿Deseas agregar contexto sobre la imagen?", value=False)

if show_details:
    additional_details = st.text_area("✍️ Describe aquí cualquier detalle relevante sobre la imagen:", height=150)

# BOTÓN PARA ANALIZAR
analyze_button = st.button("🚀 Analizar Imagen")

# ANALIZAR SI TODO ESTÁ LISTO
if uploaded_file and api_key and analyze_button:
    with st.spinner("🧠 Analizando imagen..."):
        try:
            # Codificar la imagen a base64
            base64_image = encode_image(uploaded_file)

            # Construir el prompt inicial
            prompt_text = "Describe lo que ves en la imagen en español."

            if show_details and additional_details:
                prompt_text += f"\n\nContexto adicional del usuario:\n{additional_details}"

            # Crear los mensajes para la API de chat con imagen
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ],
                }
            ]

            # Solicitud a la API de OpenAI
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1200,
                stream=True
            ):
                if completion.choices[0].delta.content:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"❌ Ocurrió un error: {e}")

# ADVERTENCIAS SI FALTAN ELEMENTOS
elif not uploaded_file and analyze_button:
    st.warning("⚠️ Por favor, sube una imagen antes de analizar.")
elif not api_key:
    st.info("🔑 Ingresa tu clave de API para usar la aplicación.")
