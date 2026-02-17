import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="📊",
    layout="wide"
)



# ======================================
# FUNÇÕES
# ======================================


# FUNÇÃO DE BARRA LATERAL

image_path = r'files/logo.png'
image = Image.open(image_path)
st.image(image, width=120)
st.write('# Curry Company Growth Dashboard')

st.markdown('---')
st.markdown("""
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos entregadores e restaurantes.
    ### Como utilizar o dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento;
        - Visão Tática: Indicadores semanais de crescimento;
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes.
            
    ### Ask for help
    - Time de Data Science
""")