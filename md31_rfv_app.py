# Imports
import pandas            as pd
import streamlit         as st
import numpy             as np

from datetime            import datetime
from PIL                 import Image
from io                  import BytesIO
import plotly.express as px

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# Função para converter o df para excel
@st.cache_data
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data


### Criando os segmentos
def recencia_class(x, r, q_dict):
    """Classifica como melhor o menor quartil 
       x = valor da linha,
       r = recencia,
       q_dict = quartil dicionario   
    """
    if x <= q_dict[r][0.25]:
        return 'A'
    elif x <= q_dict[r][0.50]:
        return 'B'
    elif x <= q_dict[r][0.75]:
        return 'C'
    else:
        return 'D'

def freq_val_class(x, fv, q_dict):
    """Classifica como melhor o maior quartil 
       x = valor da linha,
       fv = frequencia ou valor,
       q_dict = quartil dicionario   
    """
    if x <= q_dict[fv][0.25]:
        return 'D'
    elif x <= q_dict[fv][0.50]:
        return 'C'
    elif x <= q_dict[fv][0.75]:
        return 'B'
    else:
        return 'A'

# Função principal da aplicação
def main():
    # Configuração inicial da página da aplicação
    st.set_page_config(page_title = 'RFV',         layout="wide",
        initial_sidebar_state='expanded'
    )

    # Título principal da aplicação
    st.write("""# RFV

    RFV significa recência, frequência, valor e é utilizado para segmentação de clientes baseado no comportamento 
    de compras dos clientes e agrupa eles em clusters parecidos. Utilizando esse tipo de agrupamento podemos realizar 
    ações de marketing e CRM melhores direcionadas, ajudando assim na personalização do conteúdo e até a retenção de clientes.

    Para cada cliente é preciso calcular cada uma das componentes abaixo:

    - Recência (R): Quantidade de dias desde a última compra.
    - Frequência (F): Quantidade total de compras no período.
    - Valor (V): Total de dinheiro gasto nas compras do período.

    E é isso que iremos fazer abaixo.
    """)
    st.markdown("---")
    

    # Botão para carregar arquivo na aplicação
    st.sidebar.write("## Suba o arquivo")
    data_file_1 = st.sidebar.file_uploader("Bank marketing data", type = ['csv','xlsx'])

    # Verifica se há conteúdo carregado na aplicação
    if (data_file_1 is not None):
        df_compras = pd.read_csv(data_file_1, infer_datetime_format=True, parse_dates=['DiaCompra'])

        col1, col2 = st.columns(2)

        with col1:
            st.write('## Recência (R)')
            dia_atual = df_compras['DiaCompra'].max()
            st.write('Última data de registro na base: ', dia_atual)
            st.write('Dias sem afetuar uma nova compra')

            df_recencia = df_compras.groupby(by='ID_cliente', as_index=False)['DiaCompra'].max()
            df_recencia.columns = ['ID_cliente','DiaUltimaCompra']
            df_recencia['Recencia'] = df_recencia['DiaUltimaCompra'].apply(lambda x: (dia_atual - x).days)
            st.write(df_recencia.head())

            df_recencia.drop('DiaUltimaCompra', axis=1, inplace=True)

        with col2:
            st.write('## Frequência (F)')
            st.write('Quantidade de comprasa efetuadas')
            df_frequencia = df_compras[['ID_cliente','CodigoCompra']].groupby('ID_cliente').count().reset_index()
            df_frequencia.columns = ['ID_cliente','Frequencia']
            st.write(df_frequencia.head())

        col1, col2 = st.columns(2)
        with col1:
            st.write('## Valor (V)')
            st.write('Valor total de todas as compras por cliente')
            df_valor = df_compras[['ID_cliente','ValorTotal']].groupby('ID_cliente').sum().reset_index()
            df_valor.columns = ['ID_cliente','Valor']
            st.write(df_valor.head())
        

        with col2:
            st.write('## Tabela RFV final')
            st.write('Amostra da tabela')
            df_RF = df_recencia.merge(df_frequencia, on='ID_cliente')
            df_RFV = df_RF.merge(df_valor, on='ID_cliente')
            df_RFV.set_index('ID_cliente', inplace=True)
            st.write(df_RFV.head())

        st.write('## Segmentação utilizando o RFV')


        st.write("""
        **Segmentação de clientes por RFV usando quartis:**

        Uma técnica eficaz para segmentar clientes é utilizar o modelo RFV (Recência, Frequência, Valor) e dividir cada componente em quartis. Cada quartil recebe uma classificação de 'A' a 'D', onde 'A' representa o melhor desempenho e 'D' o pior.

        No entanto, a interpretação de "melhor" e "pior" varia dependendo da componente:

        * **Recência:** Quanto menor o tempo desde a última compra, melhor o cliente. Portanto, o quartil com a menor recência é classificado como 'A'.
        * **Frequência:** Quanto maior a frequência de compras, melhor o cliente. Nesse caso, o quartil com a maior frequência recebe a classificação 'A'.
        * **Valor:** Quanto maior o valor total das compras, melhor o cliente. Similar à frequência, o quartil com o maior valor é classificado como 'A'.

        Essa abordagem permite identificar diferentes perfis de clientes, como aqueles que compram com frequência e recentemente (clientes 'AAA') ou aqueles que compraram há muito tempo e com baixa frequência (clientes 'DDD').
        """)


        st.write('Estabelecendo Quartis em 25%')
        quartis = df_RFV.quantile(q=[0.25,0.5,0.75])
        st.write(quartis)

        st.write('Seguimentação em grupos')
        df_RFV['R_quartil'] = df_RFV['Recencia'].apply(recencia_class,
                                                        args=('Recencia', quartis))
        df_RFV['F_quartil'] = df_RFV['Frequencia'].apply(freq_val_class,
                                                        args=('Frequencia', quartis))
        df_RFV['V_quartil'] = df_RFV['Valor'].apply(freq_val_class,
                                                    args=('Valor', quartis))
        df_RFV['RFV_Score'] = (df_RFV.R_quartil 
                            + df_RFV.F_quartil 
                            + df_RFV.V_quartil)
        st.write(df_RFV.head())

        # Melhorando a visualização da distribuição dos scores RFV com um gráfico de barras interativo
        st.write('## Distribuição dos Scores RFV')
        rfv_counts = df_RFV['RFV_Score'].value_counts().reset_index()
        rfv_counts.columns = ['RFV_Score', 'Count']
        fig = px.bar(rfv_counts, x='RFV_Score', y='Count',
                     labels={'RFV_Score': 'Score RFV', 'Count': 'Número de Clientes'})
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)


        st.write('#### Clientes com menor recência, maior frequência e maior valor gasto')
        st.write(df_RFV[df_RFV['RFV_Score']=='AAA'].sort_values('Valor', ascending=False).head(10))

        st.write('### Ações de marketing/CRM')

        dict_acoes = {'AAA': 'Enviar cupons de desconto, Pedir para indicar nosso produto pra algum amigo, Ao lançar um novo produto enviar amostras grátis pra esses.',
        'DDD': 'Churn! clientes que gastaram bem pouco e fizeram poucas compras, fazer nada',
        'DAA': 'Churn! clientes que gastaram bastante e fizeram muitas compras, enviar cupons de desconto para tentar recuperar',
        'CAA': 'Churn! clientes que gastaram bastante e fizeram muitas compras, enviar cupons de desconto para tentar recuperar'
        }

        df_RFV['acoes de marketing/crm'] = df_RFV['RFV_Score'].map(dict_acoes)
        st.write(df_RFV.head())

        df_xlsx = to_excel(df_RFV)
        st.download_button(label='📥 Download',
                            data=df_xlsx ,
                            file_name= 'RFV_.xlsx')

        st.write('Quantidade de clientes por tipo de ação')
        st.write(df_RFV['acoes de marketing/crm'].value_counts(dropna=False))

if __name__ == '__main__':
	main()