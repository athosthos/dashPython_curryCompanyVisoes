import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium as fl
from streamlit_folium import folium_static
import streamlit as st
from datetime import datetime
from PIL import Image
import numpy as np
from haversine import haversine as hs

st.set_page_config(page_title="Visão Entregadores", layout="wide")

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

#criando coluna de tempo sem o "min"
df2['Clean_time_minutes'] = df2['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
df2['Clean_time_minutes'] = df2['Clean_time_minutes'].astype(int)



# ======================================================
# BARRA LATERAL
# ======================================================



st.header('Curry Company')
st.markdown('##### Dashboard - Visão de Empresa')

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

tab1, = st.tabs(['Visão Gerancial'])

with tab1:
    st.markdown('<h2 style="color: #8E1C1C;">Métricas gerais</h2>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5, col6 = st.columns(6, gap="large")

    with col1:
        st.subheader('Entregadores únicos')
        entregadores_unicos = df2['Delivery_person_ID'].nunique()
        st.markdown(f'# {entregadores_unicos}')

    with col2:
        st.subheader('Distância média')
        df2['Distance_KM'] = df2.apply(
            lambda x: hs(
                (x['Restaurant_latitude'], x['Restaurant_longitude']),
                (x['Delivery_location_latitude'], x['Delivery_location_longitude'])
            ), axis=1
        )
        distancia_media = df2['Distance_KM'].mean()
        st.markdown(f'# {distancia_media:.1f}')

    with col3:
        st.subheader('Tempo de entrega média c/ festival')
        tempo_medio_entrega_festival = df2.loc[(df2['Festival'] != 'No'), 'Clean_time_minutes'].mean()
        st.markdown(f'# {tempo_medio_entrega_festival:.1f}')

    with col4:
        st.subheader('Desvio padrão de tempo de entrega c/ festival')
        desvio_padrao_entrega_festival = df2.loc[(df2['Festival'] != 'No'), 'Clean_time_minutes'].std()
        st.markdown(f'# {desvio_padrao_entrega_festival:.1f}')

    with col5:
        st.subheader('Tempo de entrega médio s/ festival')
        tempo_medio_entrega_s_festival = df2.loc[(df2['Festival'] == 'No'), 'Clean_time_minutes'].mean()
        st.markdown(f'# {tempo_medio_entrega_s_festival:.1f}')

    with col6:
        st.subheader('Desvio padrão de tempo de entrega s/ festival')
        desvio_padrao_entrega_s_festival = df2.loc[(df2['Festival'] == 'No'), 'Clean_time_minutes'].std()
        st.markdown(f'# {desvio_padrao_entrega_s_festival:.1f}')

    st.markdown('<h2 style="color: #8E1C1C;">Distribuição de distância por cidade e tráfego</h2>', unsafe_allow_html=True)
    tempo_medio_desvio_cidade_trafico = df2.loc[:, ['City', 'Clean_time_minutes', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Clean_time_minutes': {'std', 'mean'}})
    tempo_medio_desvio_cidade_trafico.columns = ['std_time', 'avg_time']
    tempo_medio_desvio_cidade_trafico = tempo_medio_desvio_cidade_trafico.reset_index()
    fig = px.sunburst(
        tempo_medio_desvio_cidade_trafico, 
        path=['City', 'Road_traffic_density'], # Determinando o centro e o sub-centro do círculo
        values='avg_time', # Determinando o que vai definir o tamanho de cada repartição
        color='std_time', # Determinando o que vai definir a cor de cada repartição
        color_continuous_scale='RdBu', # Determinando a escala de cor a ser utilzada
        color_continuous_midpoint=np.average(tempo_medio_desvio_cidade_trafico['std_time']) # Determinando o ponto central da cor (média do desvio padrão)
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2, gap = 'large')

    with col1:
        st.markdown('<h2 style="color: #8E1C1C;">Distribuição de tempo por cidade</h2>', unsafe_allow_html=True)
        distribuicao_tempo_entrega_cidade = df2.loc[:, ['Clean_time_minutes', 'City']].groupby('City').agg({'Clean_time_minutes': ['mean', 'std']})
        distribuicao_tempo_entrega_cidade.columns = ['avg_time', 'std_time']
        distribuicao_tempo_entrega_cidade = distribuicao_tempo_entrega_cidade.reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name = 'Control', 
            x = distribuicao_tempo_entrega_cidade['City'], 
            y = distribuicao_tempo_entrega_cidade['avg_time'], 
            error_y = dict(type = 'data', array = distribuicao_tempo_entrega_cidade['std_time']), # Criando o desvio padrão
            text=distribuicao_tempo_entrega_cidade['avg_time'], # Determinando qual o texto que vai ser exibido no pop-up
            texttemplate='<b>%{text:.2f}</b>', # Coloquei em negrito (<b>) para ler melhor
            textposition='inside',      # Força o texto para dentro da barra
            insidetextanchor='start',   # 'start' = base, 'middle' = meio, 'end' = topo
            textfont=dict(color='white') # Garante que dê contraste com a cor da barra
        ))
        fig.update_layout(barmode = 'group')
        st.plotly_chart(fig, use_container_width = True)

    with col2:
        st.markdown('<h2 style="color: #8E1C1C;">Distância média de entrega por cidade</h2>', unsafe_allow_html=True)
        distancia_media_entrega_cidade = df2.loc[:, ['Distance_KM', 'City']].groupby('City').mean().reset_index()
        fig = px.bar(distancia_media_entrega_cidade, x = 'City', y = 'Distance_KM', text_auto = True)
        fig.update_xaxes(title = None, showticklabels = False)
        fig.update_yaxes(title = None)
        st.plotly_chart(fig, use_container_width = True)