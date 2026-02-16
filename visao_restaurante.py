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



# =======================================================
# FUNÇÕES
# =======================================================


# FUNÇÃO DE LIMPEZA DE DADOS


def clean_df (df):

    #removendo linhas onde algumas colunas é igual a NaN
    df = df.replace('NaN ', np.nan)
    linhas_para_limpar = ['Delivery_person_Age', 'multiple_deliveries', 'Road_traffic_density', 'City']
    df = df.dropna(subset=linhas_para_limpar)

    #removendo espaço de todas as colunas que necessitam usando lambda
    colunas_texto = ['Festival', 'Road_traffic_density', 'ID', 'Type_of_vehicle', 'Type_of_order', 'Weatherconditions', 'City']
    df[colunas_texto] = df[colunas_texto].apply(lambda x: x.str.strip())

    #conversões de tipos de dados
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format = '%d-%m-%Y')
    df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)

    #restaurando indice do dataframe
    df = df.reset_index(drop=True)

    #criando coluna de tempo sem o "min"
    df['Clean_time_minutes'] = df['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df['Clean_time_minutes'] = df['Clean_time_minutes'].astype(int)

    return df


# FUNÇÃO DE BARRA LATERAL


def barra_lateral(df):
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
    linhas = (df['Order_Date'] <= data_fim) & (df['Order_Date'] >= data_inicio)
    df = df.loc[linhas, :]

    st.sidebar.markdown('---')

    densidade_transito = st.sidebar.multiselect(
        'Quais as condições de transito?',
        ['Low', 'Medium', 'High', 'Jam'],
        default='Low'
    )
    linhas = df['Road_traffic_density'].isin(densidade_transito)
    df = df.loc[linhas, :]


    st.sidebar.markdown('---')

    st.sidebar.markdown('### Powered by Athos Oliveira')



# ======================================================
# IMPORTANDO DADOS E LIMPANDO DADOS
# ======================================================



df = pd.read_csv(r'files/train.csv')
df = clean_df(df)



# ======================================================
# LAYOUT NO STREAMLIT
# ======================================================



st.set_page_config(page_title="Visão Restaurante", layout="wide")
barra_lateral(df)
st.header('Curry Company')
st.markdown('##### Dashboard - Visão de Restaurante')
tab1, = st.tabs(['Visão Gerancial'])

with tab1:
    st.markdown('<h2 style="color: #8E1C1C;">Métricas gerais</h2>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5, col6 = st.columns(6, gap="large")

    with col1:
        st.subheader('Entregadores únicos')
        entregadores_unicos = df['Delivery_person_ID'].nunique()
        st.markdown(f'# {entregadores_unicos}')

    with col2:
        st.subheader('Distância média')
        df['Distance_KM'] = df.apply(
            lambda x: hs(
                (x['Restaurant_latitude'], x['Restaurant_longitude']),
                (x['Delivery_location_latitude'], x['Delivery_location_longitude'])
            ), axis=1
        )
        distancia_media = df['Distance_KM'].mean()
        st.markdown(f'# {distancia_media:.1f}')

    with col3:
        st.subheader('Tempo de entrega média c/ festival')
        tempo_medio_entrega_festival = df.loc[(df['Festival'] != 'No'), 'Clean_time_minutes'].mean()
        st.markdown(f'# {tempo_medio_entrega_festival:.1f}')

    with col4:
        st.subheader('Desvio padrão de tempo de entrega c/ festival')
        desvio_padrao_entrega_festival = df.loc[(df['Festival'] != 'No'), 'Clean_time_minutes'].std()
        st.markdown(f'# {desvio_padrao_entrega_festival:.1f}')

    with col5:
        st.subheader('Tempo de entrega médio s/ festival')
        tempo_medio_entrega_s_festival = df.loc[(df['Festival'] == 'No'), 'Clean_time_minutes'].mean()
        st.markdown(f'# {tempo_medio_entrega_s_festival:.1f}')

    with col6:
        st.subheader('Desvio padrão de tempo de entrega s/ festival')
        desvio_padrao_entrega_s_festival = df.loc[(df['Festival'] == 'No'), 'Clean_time_minutes'].std()
        st.markdown(f'# {desvio_padrao_entrega_s_festival:.1f}')

    st.markdown('<h2 style="color: #8E1C1C;">Distribuição de distância por cidade e tráfego</h2>', unsafe_allow_html=True)
    tempo_medio_desvio_cidade_trafico = df.loc[:, ['City', 'Clean_time_minutes', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Clean_time_minutes': {'std', 'mean'}})
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
        distribuicao_tempo_entrega_cidade = df.loc[:, ['Clean_time_minutes', 'City']].groupby('City').agg({'Clean_time_minutes': ['mean', 'std']})
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
        distancia_media_entrega_cidade = df.loc[:, ['Distance_KM', 'City']].groupby('City').mean().reset_index()
        fig = px.bar(distancia_media_entrega_cidade, x = 'City', y = 'Distance_KM', text_auto = True)
        fig.update_xaxes(title = None, showticklabels = False)
        fig.update_yaxes(title = None)
        st.plotly_chart(fig, use_container_width = True)