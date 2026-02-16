import pandas as pd
import plotly.express as px
import folium as fl
from streamlit_folium import folium_static
import streamlit as st
from datetime import datetime
from PIL import Image
import numpy as np



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



st.set_page_config(page_title="Visão Entregadores", layout="wide")
barra_lateral(df)
st.header('Curry Company')
st.markdown('##### Dashboard - Visão de Entregadores')
tab1, = st.tabs(['Visão Gerancial'])

with tab1:
    col1, col2, col3, col4 = st.columns(4, gap = 'large')

    with col1:  
        st.subheader('Maior Idade dos Entregadores')
        entregador_mais_velho = df['Delivery_person_Age'].max()
        st.markdown(f'# {entregador_mais_velho}')
        #col1.metric('Maior idade entre os entregadores', entregador_mais_velho)

    with col2:  
        st.subheader('Menor Idade dos Entregadores')
        entregador_mais_novo = df['Delivery_person_Age'].min()
        st.markdown(f'# {entregador_mais_novo}')

    with col3:  
        st.subheader('Melhor condição de veículos')
        melhor_condicao_veiculo = df['Vehicle_condition'].max()
        st.markdown(f'# {melhor_condicao_veiculo}')

    with col4:  
        st.subheader('Pior condição de veículos')
        pior_condicao_veiculo = df['Vehicle_condition'].min()
        st.markdown(f'# {pior_condicao_veiculo}')

    st.markdown('---')

    col1, col2 = st.columns(2, gap = 'large')

    with col1:
        st.markdown('##### Média de avaliações por entregador')
        media_avaliacoes_entregador = df.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']].groupby('Delivery_person_ID').mean().reset_index()
        st.dataframe(media_avaliacoes_entregador, height=900, use_container_width=True)

    with col2:
        st.markdown('##### Média de avaliações por trânsito')
        media_avaliacoes_transito = df.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density').mean().reset_index()
        fig = px.bar(media_avaliacoes_transito, x = 'Road_traffic_density', y = 'Delivery_person_Ratings', text_auto = True)
        fig.update_xaxes(title = None)
        fig.update_yaxes(title = None, showticklabels = False)
        st.plotly_chart(fig, use_container_width = True)

        st.markdown('##### Média de avaliações por clima')
        media_avaliacoes_clima = df.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').mean().reset_index()
        fig = px.bar(media_avaliacoes_clima, x = 'Weatherconditions', y = 'Delivery_person_Ratings', text_auto = True)
        fig.update_xaxes(title = None)
        fig.update_yaxes(title = None, showticklabels = False)
        st.plotly_chart(fig, use_container_width = True)

    st.markdown('---')

    df_ordenada = df.loc[:, ['City', 'Delivery_person_ID', 'Clean_time_minutes']].groupby(['City', 'Delivery_person_ID']).mean().reset_index()
    
    st.markdown('# Top 5 entregadores mais rápidos')
    
    entregadores_mais_rapidos_cidade = df_ordenada.sort_values(['City', 'Clean_time_minutes'], ascending = True)    
    entregadores_mais_rapidos_cidade = entregadores_mais_rapidos_cidade.groupby('City').head(5).reset_index(drop = True)
    
    col1, col2, col3 = st.columns(3, gap = 'large')

    with col1:
        st.markdown('##### Metropolitian')
        metropolitian = entregadores_mais_rapidos_cidade.loc[entregadores_mais_rapidos_cidade['City'] == 'Metropolitian', :]
        fig = px.bar(metropolitian, x = 'Clean_time_minutes', y = 'Delivery_person_ID', orientation = 'h', text_auto = True)
        fig.update_layout(yaxis={'categoryorder':'total descending'})
        fig.update_xaxes(title = None, showticklabels = False)
        fig.update_yaxes(title = None)
        st.plotly_chart(fig, use_container_width = True)

    with col2:
        st.markdown('##### Urban')
        metropolitian = entregadores_mais_rapidos_cidade.loc[entregadores_mais_rapidos_cidade['City'] == 'Urban', :]
        fig = px.bar(metropolitian, x = 'Clean_time_minutes', y = 'Delivery_person_ID', orientation = 'h', text_auto = True)
        fig.update_layout(yaxis={'categoryorder':'total descending'})
        fig.update_xaxes(title = None, showticklabels = False)
        fig.update_yaxes(title = None)
        st.plotly_chart(fig, use_container_width = True)

    with col3:
        st.markdown('##### Semi-Urban')
        metropolitian = entregadores_mais_rapidos_cidade.loc[entregadores_mais_rapidos_cidade['City'] == 'Semi-Urban', :]
        fig = px.bar(metropolitian, x = 'Clean_time_minutes', y = 'Delivery_person_ID', orientation = 'h', text_auto = True)
        fig.update_layout(yaxis={'categoryorder':'total descending'})
        fig.update_xaxes(title = None, showticklabels = False)
        fig.update_yaxes(title = None)
        st.plotly_chart(fig, use_container_width = True)

    st.markdown('# Top 5 entregadores mais lentos')
    
    entregadores_mais_lentos_cidade = df_ordenada.sort_values(['City', 'Clean_time_minutes'], ascending = [True, False])    
    entregadores_mais_lentos_cidade = entregadores_mais_lentos_cidade.groupby('City').head(5).reset_index(drop = True)
    
    col1, col2, col3 = st.columns(3, gap = 'large')

    with col1:
        st.markdown('##### Metropolitian')
        metropolitian = entregadores_mais_lentos_cidade.loc[entregadores_mais_lentos_cidade['City'] == 'Metropolitian', :]
        fig = px.bar(metropolitian, x = 'Clean_time_minutes', y = 'Delivery_person_ID', orientation = 'h', text_auto = True)
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        fig.update_xaxes(title = None, showticklabels = False)
        fig.update_yaxes(title = None)
        st.plotly_chart(fig, use_container_width = True)

    with col2:
        st.markdown('##### Urban')
        metropolitian = entregadores_mais_lentos_cidade.loc[entregadores_mais_lentos_cidade['City'] == 'Urban', :]
        fig = px.bar(metropolitian, x = 'Clean_time_minutes', y = 'Delivery_person_ID', orientation = 'h', text_auto = True)
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        fig.update_xaxes(title = None, showticklabels = False)
        fig.update_yaxes(title = None)
        st.plotly_chart(fig, use_container_width = True)

    with col3:
        st.markdown('##### Semi-Urban')
        metropolitian = entregadores_mais_lentos_cidade.loc[entregadores_mais_lentos_cidade['City'] == 'Semi-Urban', :]
        fig = px.bar(metropolitian, x = 'Clean_time_minutes', y = 'Delivery_person_ID', orientation = 'h', text_auto = True)
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        fig.update_xaxes(title = None, showticklabels = False)
        fig.update_yaxes(title = None)
        st.plotly_chart(fig, use_container_width = True)