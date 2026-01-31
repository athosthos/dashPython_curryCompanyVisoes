import pandas as pd
import plotly.express as px
import folium as fl
from streamlit_folium import folium_static
import streamlit as st
from datetime import datetime
from PIL import Image
import numpy as np

df = pd.read_csv('train.csv')



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
st.markdown('##### Dashboard - Visão de Empresa')

image_path = 'logo.png'
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



tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    # ==============================================================
    st.markdown('### Ordens por dia')
    pedidos_por_dia = df2.loc[:, ['ID', 'Order_Date']].groupby(['Order_Date']).count().reset_index()
    pedidos_por_dia = pedidos_por_dia.rename(columns={'ID': 'Quantidade de Pedidos', 'Order_Date': 'Data do Pedido'})
    fig = px.bar(pedidos_por_dia, x='Data do Pedido', y='Quantidade de Pedidos')
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    
    with col1:
        # ==============================================================
        st.markdown('### Porcentagem de densidade de tráfico')
        pedidos_por_tipo_de_traficos = df2.loc[:, ['Road_traffic_density', 'ID']].groupby(['Road_traffic_density']).count().reset_index()
        pedidos_por_tipo_de_traficos['Deliveries_perc'] = pedidos_por_tipo_de_traficos['ID'] / pedidos_por_tipo_de_traficos['ID'].sum()
        fig = px.pie(pedidos_por_tipo_de_traficos, values='Deliveries_perc', names='Road_traffic_density')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # ==============================================================
        st.markdown('### Densidade de tráfico por cidade')
        pedidos_por_cidade_trafico = df2.loc[:, ['City', 'Road_traffic_density', 'ID']].groupby(['Road_traffic_density', 'City']).count().reset_index()
        st.plotly_chart(px.bar(pedidos_por_cidade_trafico, x='Road_traffic_density', y='ID', color='City', barmode='group'), use_container_width=True)
        
with tab2:
    # ==============================================================
    st.markdown('### Quantidade de pedidos por semana')
    df2['week_of_year'] = df2['Order_Date'].dt.isocalendar().week
    df2['day_name'] = df2['Order_Date'].dt.day_name()
    mapa_dias = {
        'Monday': 'Segunda-feira',
        'Tuesday': 'Terça-feira',
        'Wednesday': 'Quarta-feira',
        'Thursday': 'Quinta-feira',
        'Friday': 'Sexta-feira',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    df2['day_name'] = df2['day_name'].map(mapa_dias)
    pedidos_por_semana = df2.loc[:, ['week_of_year', 'ID']].groupby(['week_of_year']).count().reset_index()
    st.plotly_chart(px.line(pedidos_por_semana, x='week_of_year', y='ID'), use_container_width=True)

    # ==============================================================
    st.markdown('### Média de pedidos de entregadores por semana')
    media_pedidos_por_semana_dos_entregadores = df2.loc[:, ['ID', 'Delivery_person_ID', 'week_of_year']].groupby('week_of_year').agg({
        'ID': 'count',                  
        'Delivery_person_ID': 'nunique'
    }).reset_index()
    media_pedidos_por_semana_dos_entregadores['order_by_deliver'] = media_pedidos_por_semana_dos_entregadores['ID'] / media_pedidos_por_semana_dos_entregadores['Delivery_person_ID']
    media_pedidos_por_semana_dos_entregadores = media_pedidos_por_semana_dos_entregadores.rename(columns={'ID': 'Qtd_Pedidos', 'Delivery_person_ID': 'Qtd_Entregadores'})
    fig = px.bar(media_pedidos_por_semana_dos_entregadores, x='week_of_year', y='order_by_deliver', text_auto=True)
    fig.update_yaxes(title = None, showticklabels = False)
    fig.update_xaxes(title = None)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    # ==============================================================
    st.markdown('### Mapa de tráfico por cidade')
    localizacao_central_regiao_por_trafico = df2.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    world_map = fl.Map()
    for i in range(len(localizacao_central_regiao_por_trafico)):
        fl.Marker([localizacao_central_regiao_por_trafico.loc[i, 'Delivery_location_latitude'],
                localizacao_central_regiao_por_trafico.loc[i, 'Delivery_location_longitude']],
                popup=localizacao_central_regiao_por_trafico.loc[i, ['Road_traffic_density', 'City']]
        ).add_to(world_map)
    folium_static(world_map, width = 1024, height = 600)