# coding=utf-8
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from statistics import mode
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings("ignore")
import base64

def predicao(portfolio):
    # carregando dados do mercado
    m1 = pd.read_csv('mercado_1.csv')
    m2 = pd.read_csv('mercado_2.csv')
    m3 = pd.read_csv('mercado_3.csv')
    m4 = pd.read_csv('mercado_4.csv')
    mercado_tratado = m1.append(m2).append(m3).append(m4)
    # mercado_tratado = mercado_tratado.set_index('id')

    # Dados de entrada
    features = [
        'fl_optante_simei', 'fl_optante_simples', 'idade_empresa_anos', 'cod_de_natureza_juridica', 'cod_sg_uf',
        'cod_de_ramo', 'cod_setor', 'cod_nm_divisao', 'cod_nm_segmento', 'cod_de_nivel_atividade',
        'cod_nm_meso_regiao', 'cod_de_faixa_faturamento_estimado', 'cod_de_saude_tributaria']

    # gera o modelo de KMeans
    modelo = KMeans(n_clusters=7)

    # treina o modelo
    modelo.fit(mercado_tratado[features])

    # identificar os clusters no dataset
    labels = modelo.labels_
    mercado_tratado['kmeans'] = labels

    # identifica os clientes da empresa no mercado
    # Transformando o id em index no portfolio:
    portfolio.set_index('id', inplace=True)
    # Retirarando as colunas do portfolio 1:
    portfolio.drop(columns=portfolio.columns, inplace=True)
    # Resetando o index:
    portfolio.reset_index(inplace=True)

    # Identificacao da empresa
    portfolio['portfolio'] = 1

    # Colocando essa identificacao no mercado
    mercado = mercado_tratado.merge(portfolio, on='id', how='left')

    # Coletando
    df_p = mercado.query('portfolio == 1')
    cluster = df_p['kmeans'].mode()[0]

    # Selecionar apenas novos leads, desconsiderar as pessoas que ja sao clientes da empresa
    leads_cluster = pd.DataFrame(mercado[mercado['kmeans'] == cluster].id)
    leads_cluster = leads_cluster.merge(portfolio, on='id', how='left')
    leads_cluster['portfolio'].fillna(0, inplace=True)
    # Recomendar novos leads
    leads_recomendados = leads_cluster.query('portfolio == 0')
    leads_recomendados.drop(columns='portfolio', inplace=True)


    return leads_recomendados

########## streamlit app ##########

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
    return href

# titulo
st.image ('logo.png',format='PNG')
st.title("Sistema de Recomendação")

# subtitulo
st.markdown(
    "Esse produto recomenda leads do mercado para empresas dada a sua lista de clientes (portfólio).")

########## sidebar ##########
st.sidebar.header("Projeto desenvolvido por:")
st.sidebar.markdown('**Isabela Franceschi**')
st.sidebar.markdown('LinkedIn:')
st.sidebar.markdown('https://www.linkedin.com/in/isabela-hachmann-de-franceschi-aaa22470/')
st.sidebar.markdown('GitHub:')
st.sidebar.markdown('https://github.com/IsabelaFranceschi')
########## sidebar ##########


st.subheader("Faça o upload da sua base de clientes: ")
file_port = st.file_uploader('', type='csv')

if file_port:
    btn_predict = st.button("Gerar Leads")
    if btn_predict:
        # barra de loading
        bar = st.progress(0)
        latest_iteration = st.empty()
        latest_iteration.text('Gerando Leads..')

        portfolio = pd.read_csv(file_port)

        # barra de loading
        bar.progress(20)

        #pt1 = pt1.set_index('id')
        df_leads = predicao(portfolio)

        # barra de loading
        bar.progress(40)

        st.markdown("Leads Recomendados")
        #df_leads.index
        df_leads

        st.markdown("Total de leads recomendados:")
        df_leads.shape[0]

        st.markdown("Voce já pode baixar os leads no arquivo abaixo:")

        # barra de loading
        bar.progress(50)
        latest_iteration.text('Gerando arquivo para Download...')

        st.markdown(get_table_download_link(df_leads), unsafe_allow_html=True)

        # barra de loading
        bar.progress(100)
        latest_iteration.text('ARQUIVO PRONTO PARA DOWNLOAD!')


