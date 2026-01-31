import pandas as pd
import plotly.express as px
import folium as fl
from streamlit_folium import folium_static
import streamlit as st
from datetime import datetime
from PIL import Image
import numpy as np

df = pd.read_csv(r'files/train.csv')



# =======================================================
#LIMPEZA DE DADOS
# =======================================================



#removendo linhas onde algumas colunas é igual a NaN
df1 = df.replace('NaN ', np.nan)
linhas_para_limpar = ['Delivery_person_Age', 'multiple_deliveries', 'Road_traffic_density', 'City']
df2 = df1.dropna(subset=linhas_para_limpar).copy()

#convertendo a idade para número
df2['Delivery_person_Age'] = df2['Delivery_person_Age'].astype(int)

#convertendo os ratings para float
df2['Delivery_person_Ratings'] = df2['Delivery_person_Ratings'].astype(float)

#convertendo a coluna de data da ordem para o tipo data
df2['Order_Date'] = pd.to_datetime(df2['Order_Date'], format = '%d-%m-%Y')

#convertendo a coluna de multiplos deliveries para número
df2['multiple_deliveries'] = df2['multiple_deliveries'].astype(int)

#restaurando indice do dataframe
df2 = df2.reset_index(drop=True)

#removendo espaço das estremidade
df2['ID'] = df2['ID'].str.strip()

#removendo espaço de todas as colunas que necessitam usando lambda
colunas_texto = ['Festival', 'Road_traffic_density', 'Type_of_vehicle', 'Type_of_order', 'Weatherconditions', 'City']
df2[colunas_texto] = df2[colunas_texto].apply(lambda x: x.str.strip())



# ======================================================
# BARRA LATERAL
# ======================================================



st.header('Curry Company')

image_path = r'files/logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Filtros')

st.sidebar.markdown('---')

st.sidebar.markdown('## Selecione o período')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=(datetime(2022, 2, 11), datetime(2022, 4 , 6)),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD/MM/YYYY'
)
data_inicio = date_slider[0]
data_fim = date_slider[1]
linhas = (df2['Order_Date'] <= data_fim) & (df2['Order_Date'] >= data_inicio)
df2 = df2.loc[linhas, :]

st.sidebar.markdown('---')

densidade_transito = st.sidebar.multiselect(
    'Quais as condições de transito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default='Low'
)
linhas = df2['Road_traffic_density'].isin(densidade_transito)
df2 = df2.loc[linhas, :]


st.sidebar.markdown('---')

st.sidebar.markdown('### Powered by Athos Oliveira')



# ======================================================
# LAYOUT NO STREAMLIT
# ======================================================



