import pandas as pd
# import seaborn as sns
import matplotlib.pyplot as plt
import os

import streamlit as st


def plota_pivot_table(df, value, index, func, ylabel, xlabel, opcao='nada'):
    if opcao == 'nada':
        pd.pivot_table(df, values=value, index=index,aggfunc=func).plot(figsize=[15, 5])
    elif opcao == 'unstack':
        pd.pivot_table(df, values=value, index=index,aggfunc=func).unstack().plot(figsize=[15, 5])
    elif opcao == 'sort':
        pd.pivot_table(df, values=value, index=index,aggfunc=func).sort_values(value).plot(figsize=[15, 5])
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    st.pyplot(fig=plt)
    return None


st.set_page_config(layout='wide',
                   page_title='SINASC Rondônia',
                   page_icon ='https://upload.wikimedia.org/wikipedia/commons/e/ea/Flag_map_of_Rondonia.png')
st.write('# Análise SINASC')



sinasc = pd.read_csv('./input/SINASC_RO_2019.csv')

sinasc.DTNASC = pd.to_datetime(sinasc.DTNASC)

min_data = sinasc.DTNASC.min()
max_data = sinasc.DTNASC.max()

data_inicial = pd.to_datetime(st.sidebar.date_input('Data Inicial',
              value = min_data,
              min_value = min_data,
              max_value = max_data))

data_final = pd.to_datetime(st.sidebar.date_input('Data Inicial',
              value = max_data,
              min_value = min_data,
              max_value = max_data))

st.sidebar.write('Data Inicial: ',data_inicial)
st.sidebar.write('Data Final: ',data_final)

sinasc_filtrado = sinasc[(sinasc.DTNASC <= data_final)&(sinasc.DTNASC >= data_inicial)]
#st.write(sinasc_filtrado)


##plots
plota_pivot_table(sinasc_filtrado, 'IDADEMAE', 'DTNASC', 'mean', 'média idade mãe por data', 'data nascimento')

plota_pivot_table(sinasc_filtrado, 'IDADEMAE', ['DTNASC', 'SEXO'], 'mean', 'media idade mae','data de nascimento','unstack')

plota_pivot_table(sinasc_filtrado, 'PESO', ['DTNASC', 'SEXO'], 'mean', 'media peso bebe','data de nascimento','unstack')

plota_pivot_table(sinasc_filtrado, 'PESO', 'ESCMAE', 'median', 'PESO mediano','escolaridade mae','sort')

plota_pivot_table(sinasc_filtrado, 'APGAR1', 'GESTACAO', 'mean', 'apgar1 medio','gestacao','sort')
