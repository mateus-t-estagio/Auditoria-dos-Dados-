import dash
#import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
#from plotly.subplots import make_subplots
from dash.dependencies import Input, Output
import numpy as np
import pathlib
import warnings
warnings.filterwarnings("ignore")
import io
from flask import send_file
import flask


#### TREM FORMADO
# Path
PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("Data").resolve()

lista = ['EFC', 'EFVM', 'FTC', 'FTL', 'FCA', 'RMN', 'RMP', 'RMO', 'RMS', 'MRS', 'EFPO', 'FNSTN']

# Querys
i=[1]
for x in i:
    TremKMCarga = pd.read_excel(DATA_PATH.joinpath('Carga.xlsx'))
    TremKMServ = pd.read_excel(DATA_PATH.joinpath('Serv.xlsx'))
    Siade = pd.read_excel(DATA_PATH.joinpath('Siade.xlsx'))
    TremFormado = pd.read_excel(DATA_PATH.joinpath('TremFormado.xlsx'))
    
    tblDesempenhoLocomotivax = pd.read_csv(DATA_PATH.joinpath('tblDesempenhoLocomotiva.csv'), sep=';', decimal=',')
    tblDesempenhoVagaox = pd.read_csv(DATA_PATH.joinpath('tblDesempenhoVagao.csv'), sep=';', decimal=',')
    tblFerroviax = pd.read_csv(DATA_PATH.joinpath('tblFerrovia.csv'), sep=';')
# Tabela referência para ferrovia
    tblFerroviax = tblFerroviax[['CodigoFerrovia', 'SiglaFerrovia']]

    tblDesempenhoLocomotivax = tblDesempenhoLocomotivax.merge(tblFerroviax, on = 'CodigoFerrovia')
    tblDesempenhoVagaox = tblDesempenhoVagaox.merge(tblFerroviax, on = 'CodigoFerrovia')
    tblDesempenhoVagaox = tblDesempenhoVagaox.fillna(0)

    tblDesempenhoLocomotiva = tblDesempenhoLocomotivax
    tblDesempenhoVagao = tblDesempenhoVagaox

# Querys
    tblAbastecimentox = pd.read_csv(DATA_PATH.joinpath('tblAbastecimento.csv'), sep=';')
    tblAbastecimentoFerroviax = pd.read_csv(DATA_PATH.joinpath('tblAbastecimentoFerrovia.csv'), sep=';')
    tblDesempenhoLocomotivax = pd.read_csv(DATA_PATH.joinpath('tblDesempenhoLocomotiva.csv'), sep=';')
    tblFerroviax = pd.read_csv(DATA_PATH.joinpath('tblFerrovia.csv'), sep=';')
    tblSiadex = pd.read_excel(DATA_PATH.joinpath('Siade.xlsx'))


# Tabela referência para ferrovia
    tblFerroviax = tblFerroviax[['CodigoFerrovia', 'SiglaFerrovia']]

# PROCV pro nome da ferrovia usando o Codigo Ferrovia
    tblAbastecimentox = tblAbastecimentox.merge(tblFerroviax, on = 'CodigoFerrovia')
    tblAbastecimentoFerroviax = tblAbastecimentoFerroviax.merge(tblFerroviax, on = 'CodigoFerrovia')
    tblDesempenhoLocomotivax = tblDesempenhoLocomotivax.merge(tblFerroviax, on = 'CodigoFerrovia')

    Siade_Fluxospt1 = pd.read_excel(DATA_PATH.joinpath('Siade_Fluxos1.xlsx'))
    Siade_Fluxospt2 = pd.read_excel(DATA_PATH.joinpath('Siade_Fluxos.xlsx'))
    Siade_Fluxos = pd.concat([Siade_Fluxospt1, Siade_Fluxospt2])
#print('Import OK')

    df_trem_formado = {}
    df_tremkm = {}
    df_siade = {}
    i=0
for i in lista:
    ferrovia = i
    # Filtro pra ferrovia
    iTremKMCarga = TremKMCarga['Ferrovia'] == ferrovia
    iTremKMServ = TremKMServ['Ferrovia'] == ferrovia
    iSiade = Siade['Ferrovia'] == ferrovia
    iTremFormado = TremFormado['Ferrovia'] == ferrovia

    TremKMCargaFilt = TremKMCarga[iTremKMCarga]
    TremKMServFilt = TremKMServ[iTremKMServ]
    SiadeFilt = Siade[iSiade]
    TremFormadoFilt = TremFormado[iTremFormado]

    # Wrangling do Trem Formado
    TremFormadoFilt = TremFormadoFilt.fillna(0)
    TremFormadoFilt['Período'] = pd.to_datetime(TremFormadoFilt['Período'], format='%m/%Y')
    TremFormadoFilt['TremKm'] = TremFormadoFilt['Nº Trens'] * TremFormadoFilt['Distância (km)']
    TremFormadoFilt['TKU'] = TremFormadoFilt['TU'] * TremFormadoFilt['Nº Trens'] * TremFormadoFilt['Distância (km)']
    TremFormadoFilt['TUa'] = TremFormadoFilt['TU'] * TremFormadoFilt['Nº Trens']

    # Adequação do resto pra abarcar o mesmo período de tempo
    SiadeFilt = SiadeFilt[58:]
    TremKMCargaFilt = TremKMCargaFilt[58:]
    TremKMServFilt = TremKMServFilt[58:]

    # União das planilhas de trem km de carga e serviço
    frames = [TremKMCargaFilt['Mês/Ano'],
                TremKMCargaFilt['Nº de Trens Formados'],
                TremKMCargaFilt['Distância Percorrida'],
                TremKMServFilt['Distância Percorrida Serviço']]
    TremKMFilt = pd.concat(frames, axis=1, sort=False)
    TremKMFilt['TremKm'] = float(0)
    TremKMFilt['Distância Percorrida'] = TremKMFilt['Distância Percorrida'].astype(int)
    TremKMFilt['TremKm'] = TremKMFilt['Distância Percorrida'] + TremKMFilt['Distância Percorrida Serviço']

    # Adequação dos dados do dataframe tremkm
    lista2 = ['Nº Trens', 'Tempo de Viagem', 'Distância (km)', 'TremKm', 'TKU', 'TUa']

    for x in lista2:
        TremFormadoFilt[x] = TremFormadoFilt[x].astype(float)

    df = TremFormadoFilt.pivot_table(['Nº Trens', 'Tempo de Viagem', 'Distância (km)', 'TremKm', 'TKU', 'TUa'],
                                        ['Período'], aggfunc='sum')
    

    # Rename TremKm
    df = df.rename(columns={'TremKm': 'TremKm - Trem Formado'})
    TremKMFilt = TremKMFilt.rename(columns={'TremKm': 'Trem Km - Siade'})
    df_tremkm[i] = TremKMFilt

    # Rename TKU
    SiadeFilt = SiadeFilt.rename(columns={'TKU': 'TKU - Siade'})
    df = df.rename(columns={'TKU': 'TKU - Trem Formado'})

    # Rename TU
    SiadeFilt = SiadeFilt.rename(columns={'TU': 'TU - Siade'})
    df = df.rename(columns={'TUa': 'TU - Trem Formado'})
    df_siade[i] = SiadeFilt

    # Período de referência
    lst = pd.date_range('2010-11', '2019-7', freq='m')
    df.index = df.index.strftime('%m-%Y')
    df_trem_formado[i] = df

### Material Rodante
totalloc = ['NumeroImobilizacaoOficinaPropria',
            'NumeroImobilizacaoOficinaTerceiros',
            'NumeroDisponivelNaoUtilizadoPropria',
            'NumeroDisponivelNaoUtilizadoTerceiros',
            'NumeroUtilizacaoPropria',
            'NumeroUtilizacaoTerceiros',
            'NumeroUtilizacaoServicoInterno']

imobloc = ['NumeroImobilizacaoOficinaPropria',
            'NumeroImobilizacaoOficinaTerceiros']

disploc = ['NumeroDisponivelNaoUtilizadoPropria',
            'NumeroDisponivelNaoUtilizadoTerceiros',
            'NumeroUtilizacaoPropria',
            'NumeroUtilizacaoTerceiros',
            'NumeroUtilizacaoServicoInterno']

utiloc = ['NumeroUtilizacaoPropria',
            'NumeroUtilizacaoTerceiros',
            'NumeroUtilizacaoServicoInterno']

# Definindo total de locomotivas
tblDesempenhoLocomotiva['TotalLocomotivas'] = float(0)
for i in range(len(totalloc)):
    y1 = tblDesempenhoLocomotiva[totalloc[i]]
    tblDesempenhoLocomotiva['TotalLocomotivas'] += y1

# Definindo locomotivas imobilizadas
tblDesempenhoLocomotiva['LocomotivasImobilizadas'] = float(0)
for i in range(len(imobloc)):
    y2 = tblDesempenhoLocomotiva[imobloc[i]]
    tblDesempenhoLocomotiva['LocomotivasImobilizadas'] += y2

    # Definindo locomotivas disponíveis
tblDesempenhoLocomotiva['LocomotivasDisponiveis'] = float(0)
for i in range(len(disploc)):
    y3 = tblDesempenhoLocomotiva[disploc[i]]
    tblDesempenhoLocomotiva['LocomotivasDisponiveis'] += y3

    # Definindo locomotivas disponíveis
tblDesempenhoLocomotiva['LocomotivasUtilizadas'] = float(0)
for i in range(len(utiloc)):
    y4 = tblDesempenhoLocomotiva[utiloc[i]]
    tblDesempenhoLocomotiva['LocomotivasUtilizadas'] += y4

# Taxa de Imobilizacao
tblDesempenhoLocomotiva['Taxa de Imobolização - Locomotiva'] = \
    tblDesempenhoLocomotiva['LocomotivasImobilizadas']/tblDesempenhoLocomotiva['TotalLocomotivas']
#Taxa de Disponibilidade
tblDesempenhoLocomotiva['Taxa de Disponibilidade - Locomotiva'] = \
    tblDesempenhoLocomotiva['LocomotivasDisponiveis']/tblDesempenhoLocomotiva['TotalLocomotivas']
#Taxa de Utilização da Disponibilidade
tblDesempenhoLocomotiva['Taxa de Utilização da Disponibilidade - Locomotiva'] = \
    tblDesempenhoLocomotiva['LocomotivasUtilizadas']/tblDesempenhoLocomotiva['LocomotivasDisponiveis']

################################### VAGOES ##########################
# Criação das Colunas de Total, Imobilizado, Disponível e Utilizado
totalvag = ['NumeroImobilizacaoOficinaPropria',
            'NumeroImobilizacaoOficinaTerceiros',
            'NumeroDisponivelNaoUtilizadoPropria',
            'NumeroDisponivelNaoUtilizadoTerceiros',
            'NumeroUtilizacaoPropria',
            'NumeroUtilizacaoTerceiros',
            'NumeroUtilizacaoServicoInterno']

imobvag = ['NumeroImobilizacaoOficinaPropria',
            'NumeroImobilizacaoOficinaTerceiros']

dispvag = ['NumeroDisponivelNaoUtilizadoPropria',
            'NumeroDisponivelNaoUtilizadoTerceiros',
            'NumeroUtilizacaoPropria',
            'NumeroUtilizacaoTerceiros',
            'NumeroUtilizacaoServicoInterno']

utivag = ['NumeroUtilizacaoPropria',
            'NumeroUtilizacaoTerceiros',
            'NumeroUtilizacaoServicoInterno']

# Definindo total de locomotivas
tblDesempenhoVagao['TotalVagoes'] = float(0)
for i in range(len(totalvag)):
    y1 = tblDesempenhoVagao[totalvag[i]]
    tblDesempenhoVagao['TotalVagoes'] += y1

# Definindo locomotivas imobilizadas
tblDesempenhoVagao['VagoesImobilizados'] = float(0)
for i in range(len(imobvag)):
    y2 = tblDesempenhoVagao[imobvag[i]]
    tblDesempenhoVagao['VagoesImobilizados'] += y2

    # Definindo locomotivas disponíveis
tblDesempenhoVagao['VagoesDisponiveis'] = float(0)
for i in range(len(dispvag)):
    y3 = tblDesempenhoVagao[dispvag[i]]
    tblDesempenhoVagao['VagoesDisponiveis'] += y3

    # Definindo locomotivas disponíveis
tblDesempenhoVagao['VagoesUtilizados'] = float(0)
for i in range(len(utivag)):
    y4 = tblDesempenhoVagao[utivag[i]]
    tblDesempenhoVagao['VagoesUtilizados'] += y4

# Taxa de Imobilizacao
tblDesempenhoVagao['Taxa de Imobolização - Vagão'] = \
    tblDesempenhoVagao['VagoesImobilizados']/tblDesempenhoVagao['TotalVagoes']
#Taxa de Disponibilidade
tblDesempenhoVagao['Taxa de Disponibilidade - Vagão'] = \
    tblDesempenhoVagao['VagoesDisponiveis']/tblDesempenhoVagao['TotalVagoes']
#Taxa de Utilização da Disponibilidade
tblDesempenhoVagao['Taxa de Utilização da Disponibilidade - Vagão'] = \
    tblDesempenhoVagao['VagoesUtilizados']/tblDesempenhoVagao['VagoesDisponiveis']




consolidadoImobLoc = {}
consolidadoDispLoc = {}
consolidadoImobVag = {}
consolidadoDispVag = {}

for i in lista:
    ferrovia = i
    #tblDesempenhoLocomotivaL = tblDesempenhoLocomotiva
    #tblDesempenhoVagaoL = tblDesempenhoVagao

    if ferrovia == 'FNSTN':

        itblDesempenhoLocomotiva = tblDesempenhoLocomotiva['SiglaFerrovia'] == ferrovia
        tblDesempenhoLocomotivan = tblDesempenhoLocomotiva[itblDesempenhoLocomotiva]

        itblDesempenhoVagao = tblDesempenhoVagao['SiglaFerrovia'] == ferrovia
        tblDesempenhoVagaon = tblDesempenhoVagao[itblDesempenhoVagao]

        # Ajuste to_date_time
        tblDesempenhoLocomotivan.index = tblDesempenhoLocomotivan['DataReferencia']
        tblDesempenhoLocomotivan.index = \
            pd.to_datetime(tblDesempenhoLocomotivan.index, dayfirst=False).strftime('%m-%Y')
        tblDesempenhoLocomotivan['DataReferencia'] = \
            pd.to_datetime(tblDesempenhoLocomotivan['DataReferencia'], dayfirst=False)

        tblDesempenhoVagaon.index = tblDesempenhoVagaon['DataReferencia']
        tblDesempenhoVagaon.index = \
            pd.to_datetime(tblDesempenhoVagaon.index, dayfirst=False).strftime('%m-%Y')
        tblDesempenhoVagaon['DataReferencia'] = \
            pd.to_datetime(tblDesempenhoVagaon['DataReferencia'], dayfirst=False)



        # Dinâmica pra plotar
        tblDesempenhoLocomotivaPIVOT = tblDesempenhoLocomotivan.pivot_table(['Taxa de Imobolização - Locomotiva',
                                                    'Taxa de Disponibilidade - Locomotiva',
                                                    'Taxa de Utilização da Disponibilidade - Locomotiva'],
                                                                            ['DataReferencia'], aggfunc='mean')
        tblDesempenhoLocomotivaPIVOT.index = pd.to_datetime(tblDesempenhoLocomotivaPIVOT.index).strftime('%d-%Y')
        tblDesempenhoLocomotivaPIVOT = tblDesempenhoLocomotivaPIVOT['01-2008':'03-2019']

        consolidadoImobLoc[i] = tblDesempenhoLocomotivaPIVOT['Taxa de Imobolização - Locomotiva']
        consolidadoDispLoc[i] = tblDesempenhoLocomotivaPIVOT['Taxa de Utilização da Disponibilidade - Locomotiva']


        tblDesempenhoVagaoPIVOT = \
            tblDesempenhoVagaon.pivot_table(['Taxa de Imobolização - Vagão',
                                            'Taxa de Disponibilidade - Vagão',
                                            'Taxa de Utilização da Disponibilidade - Vagão'],
                                                                    ['DataReferencia'], aggfunc='mean')
        tblDesempenhoVagaoPIVOT.index = pd.to_datetime(tblDesempenhoVagaoPIVOT.index).strftime('%d-%Y')
        tblDesempenhoVagaoPIVOT = tblDesempenhoVagaoPIVOT['01-2008':'03-2019']

        consolidadoImobVag[i] = tblDesempenhoVagaoPIVOT['Taxa de Imobolização - Vagão']
        consolidadoDispVag[i] = tblDesempenhoVagaoPIVOT['Taxa de Utilização da Disponibilidade - Vagão']

    else:

        itblDesempenhoLocomotiva = tblDesempenhoLocomotiva['SiglaFerrovia'] == ferrovia
        tblDesempenhoLocomotivan = tblDesempenhoLocomotiva[itblDesempenhoLocomotiva]

        itblDesempenhoVagao = tblDesempenhoVagao['SiglaFerrovia'] == ferrovia
        tblDesempenhoVagaon = tblDesempenhoVagao[itblDesempenhoVagao]

        # Ajuste to_date_time
        tblDesempenhoLocomotivan.index = tblDesempenhoLocomotivan['DataReferencia']
        tblDesempenhoLocomotivan.index = \
            pd.to_datetime(tblDesempenhoLocomotivan.index, dayfirst=False).strftime('%m-%Y')
        tblDesempenhoLocomotivan['DataReferencia'] = \
            pd.to_datetime(tblDesempenhoLocomotivan['DataReferencia'], dayfirst=False)

        tblDesempenhoVagaon.index = tblDesempenhoVagaon['DataReferencia']
        tblDesempenhoVagaon.index = \
            pd.to_datetime(tblDesempenhoVagaon.index, dayfirst=False).strftime('%m-%Y')
        tblDesempenhoVagaon['DataReferencia'] = \
            pd.to_datetime(tblDesempenhoVagaon['DataReferencia'], dayfirst=False)



        # Dinâmica pra plotar
        tblDesempenhoLocomotivaPIVOT = tblDesempenhoLocomotivan.pivot_table(['Taxa de Imobolização - Locomotiva',
                                                    'Taxa de Disponibilidade - Locomotiva',
                                                    'Taxa de Utilização da Disponibilidade - Locomotiva'],
                                                                            ['DataReferencia'], aggfunc='mean')
        tblDesempenhoLocomotivaPIVOT.index = pd.to_datetime(tblDesempenhoLocomotivaPIVOT.index).strftime('%d-%Y')
        tblDesempenhoLocomotivaPIVOT = tblDesempenhoLocomotivaPIVOT['01-2006':'03-2019']

        consolidadoImobLoc[i] = tblDesempenhoLocomotivaPIVOT['Taxa de Imobolização - Locomotiva']
        consolidadoDispLoc[i] = tblDesempenhoLocomotivaPIVOT['Taxa de Utilização da Disponibilidade - Locomotiva']


        tblDesempenhoVagaoPIVOT = \
            tblDesempenhoVagaon.pivot_table(['Taxa de Imobolização - Vagão',
                                            'Taxa de Disponibilidade - Vagão',
                                            'Taxa de Utilização da Disponibilidade - Vagão'],
                                                                    ['DataReferencia'], aggfunc='mean')
        tblDesempenhoVagaoPIVOT.index = pd.to_datetime(tblDesempenhoVagaoPIVOT.index).strftime('%d-%Y')
        tblDesempenhoVagaoPIVOT = tblDesempenhoVagaoPIVOT['01-2006':'03-2019']

        consolidadoImobVag[i] = tblDesempenhoVagaoPIVOT['Taxa de Imobolização - Vagão']
        consolidadoDispVag[i] = tblDesempenhoVagaoPIVOT['Taxa de Utilização da Disponibilidade - Vagão']

## Consumo
df_Siade = {}
df_Abastecimento = {}
df_Locomotiva = {}
df_Consumo = {}
cont = 0
for i in lista:

    itblAbastecimento = tblAbastecimentox['SiglaFerrovia'] == i
    itblAbastecimentoFerrovia = tblAbastecimentoFerroviax['SiglaFerrovia'] == i
    itblDesempenhoLocomotiva = tblDesempenhoLocomotivax['SiglaFerrovia'] == i

    tblAbastecimento = tblAbastecimentox[itblAbastecimento]
    tblAbastecimentoFerrovia = tblAbastecimentoFerroviax[itblAbastecimentoFerrovia]
    tblDesempenhoLocomotiva = tblDesempenhoLocomotivax[itblDesempenhoLocomotiva]

    itblSiade = tblSiadex['Ferrovia'] == i
    tblSiade = tblSiadex[itblSiade]

    # Ajuste to_date_time
    tblAbastecimento.index = tblAbastecimento['DataReferencia']
    tblAbastecimento.index = pd.to_datetime(tblAbastecimento.index, dayfirst=True).strftime('%m-%Y')
    tblAbastecimento['DataReferencia'] = pd.to_datetime(tblAbastecimento['DataReferencia'], dayfirst=False)

    tblDesempenhoLocomotiva.index = tblDesempenhoLocomotiva['DataReferencia']
    tblDesempenhoLocomotiva.index = pd.to_datetime(tblDesempenhoLocomotiva.index, dayfirst=False).strftime('%m-%Y')
    tblDesempenhoLocomotiva['DataReferencia'] = pd.to_datetime(tblDesempenhoLocomotiva['DataReferencia'], dayfirst=False)

    tblSiade.index = tblSiade['Mês/Ano']
    tblSiade.index = pd.to_datetime(tblSiade.index, dayfirst=False).strftime('%m-%Y')
    tblSiade['Mês/Ano'] = pd.to_datetime(tblSiade['Mês/Ano'], dayfirst=False)
    tblSiade = tblSiade['11-2010':'03-2019']

    # Dinâmica pra plotar
    tblAbastecimentoPIVOT = tblAbastecimento.pivot_table(['LitrosViagem'],
                                        ['DataReferencia'], aggfunc='sum')
    tblAbastecimentoPIVOT.index = pd.to_datetime(tblAbastecimentoPIVOT.index).strftime('%d-%Y')
    tblAbastecimentoPIVOT = tblAbastecimentoPIVOT['11-2010':'03-2019']
    tblDesempenhoLocomotivaPIVOT = tblDesempenhoLocomotiva.pivot_table(['NumeroDistanciaPercorrida', 'NumeroConsumoCombustivel'],
                                                                        ['DataReferencia'], aggfunc='sum')
    tblDesempenhoLocomotivaPIVOT.index = pd.to_datetime(tblDesempenhoLocomotivaPIVOT.index).strftime('%d-%Y')
    tblDesempenhoLocomotivaPIVOT = tblDesempenhoLocomotivaPIVOT['11-2010':'03-2019']

    lst = pd.date_range('2010-11', '2019-4', freq='m')
    consumo_por_tku = pd.DataFrame([])
    consumo_por_tku['Consumo Médio - L/ mil TKU'] = tblDesempenhoLocomotivaPIVOT['NumeroConsumoCombustivel']/(tblSiade['TKU']/1000)


    df_Consumo[i] = consumo_por_tku
    df_Abastecimento[i] = tblAbastecimentoPIVOT
    df_Locomotiva[i] = tblDesempenhoLocomotivaPIVOT
    df_Siade[i] = tblSiade
    cont += 1
    #print(round(cont/12,2))

## Velocidade
df_SiadeFluxos = {}
df_TremKMV = {}
df_prod = {}

cont=0
for z in lista:
    # Filtro pra ferrovia
    iTremKMCarga = TremKMCarga['Ferrovia'] == z
    iTremKMServ = TremKMServ['Ferrovia'] == z
    iSiade = Siade['Ferrovia'] == z
    iTremFormado = TremFormado['Ferrovia'] == z
    iSiade_Fluxos = Siade_Fluxos['Ferrovia'] == z

    TremKMCargaFilt = TremKMCarga[iTremKMCarga]
    TremKMServFilt = TremKMServ[iTremKMServ]
    SiadeFilt = Siade[iSiade]
    TremFormadoFilt = TremFormado[iTremFormado]
    Siade_Fluxos_Filt = Siade_Fluxos[iSiade_Fluxos]

    xTremFormadoFilt = TremFormadoFilt['TU'] != ''
    TremFormadoFilt = TremFormadoFilt[xTremFormadoFilt]

    # Cálculo da Velocidade - Trem Formado
    TremFormadoFilt = TremFormadoFilt.fillna(0)
    TremFormadoFilt.index = TremFormadoFilt['Período']
    TremFormadoFilt.index = pd.to_datetime(TremFormadoFilt.index).strftime('%m-%Y')
    TremFormadoFilt['Período'] = pd.to_datetime(TremFormadoFilt['Período'])
    TremFormadoFilt['Distância (km)'] = TremFormadoFilt['Distância (km)'].astype(float)
    TremFormadoFilt['Tempo de Viagem'] = TremFormadoFilt['Tempo de Viagem'].astype(float)
    TremFormadoFilt['Velocidade - Trem Formado'] = float(0)
    TremFormadoFilt['Velocidade - Trem Formado'] = TremFormadoFilt['Distância (km)'] / TremFormadoFilt['Tempo de Viagem']


    # Cálculo da Velocidade - Siade
    SiadeFilt = SiadeFilt.fillna(0)
    SiadeFilt.index = SiadeFilt['Mês/Ano']
    SiadeFilt.index = pd.to_datetime(SiadeFilt.index).strftime('%m-%Y')
    SiadeFilt['Dist. Média (km)'] = SiadeFilt['Dist. Média (km)'].astype(float)
    SiadeFilt['Tempo Viag. (h)'] = SiadeFilt['Tempo Viag. (h)'].astype(float)
    SiadeFilt['Velocidade - Siade'] = float(0)
    SiadeFilt['Velocidade - Siade'] = SiadeFilt['Dist. Média (km)'] / SiadeFilt['Tempo Viag. (h)']
    
    # Cálculo da Velocidade - Siade_Fluxos
    Siade_Fluxos_Filt = Siade_Fluxos_Filt.fillna(0)
    Siade_Fluxos_Filt['Mês/Ano'] = pd.to_datetime(Siade_Fluxos_Filt['Mês/Ano'])
    Siade_Fluxos_Filt['Dist. Média (km)'] = Siade_Fluxos_Filt['Dist. Média (km)'].astype(float)
    Siade_Fluxos_Filt['Tempo Viag. (h)'] = Siade_Fluxos_Filt['Tempo Viag. (h)'].astype(float)
    Siade_Fluxos_Filt['Velocidade - Siade'] = float(0)
    Siade_Fluxos_Filt['Velocidade - Siade'] = Siade_Fluxos_Filt['Dist. Média (km)'] / Siade_Fluxos_Filt['Tempo Viag. (h)']
    Siade_Fluxos_Filt['Valor pond'] = (Siade_Fluxos_Filt['Dist. Média (km)'] / Siade_Fluxos_Filt['Tempo Viag. (h)'])*Siade_Fluxos_Filt['TU']

    Siade_Fluxos_FiltDF = Siade_Fluxos_Filt.pivot_table(['Dist. Média (km)', 'TU', 'TKU', 'Tempo Viag. (h)', 'Valor pond'],
                                        ['Mês/Ano'], aggfunc='sum')
    
    Siade_Fluxos_FiltDF['Velocidade - Siade'] = float(0)
    Siade_Fluxos_FiltDF['Velocidade - Siade'] = Siade_Fluxos_FiltDF['Valor pond'] / Siade_Fluxos_FiltDF['TU']
    Siade_Fluxos_FiltDF.index = pd.to_datetime(Siade_Fluxos_FiltDF.index).strftime('%m-%Y')
    for i in range(len(Siade_Fluxos_FiltDF['TU'])):
        if Siade_Fluxos_FiltDF.iloc[i,2] == 0:
            Siade_Fluxos_FiltDF.iloc[i,4] = 0

    # União das planilhas de trem km de carga e serviço
    frames = [TremKMCargaFilt['Velocidade Média Comercial (km/h)'],
                TremKMCargaFilt['Velocidade Média do Percurso (km/h)'],
                TremKMCargaFilt['Mês/Ano']]
    TremKMFilt = pd.concat(frames, axis=1, sort=False)
    TremKMFilt.index = TremKMFilt['Mês/Ano']
    TremKMFilt.index = pd.to_datetime(TremKMFilt.index).strftime('%m-%Y')

    df = TremFormadoFilt.pivot_table(['Velocidade - Trem Formado'],
                                        ['Período'], aggfunc='mean')
    for i in range(len(df['Velocidade - Trem Formado'])):
        if df.iloc[i,0]>70:
            df.iloc[i,0]=0

    # Período de referência
    lst = pd.date_range('2011-01', '2019-7', freq='m')
    df.index = pd.to_datetime(df.index).strftime('%m-%Y')
    
    
    df_SiadeFluxos[z] = Siade_Fluxos_FiltDF
    df_TremKMV[z] = TremKMFilt
    df_prod[z] = SiadeFilt
    
    cont += 1
    #print(round(cont/12,2))

### INICIO DASHBOARD
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

#Texto do Relatório
intro = '''
## Produção e Distância Percorrida
'''

parte2 = '''
## Material Rodante
'''

parte3 = '''
## Consumo de Combustível
'''

parte4 = '''
## Velocidade
'''
lista1 = ['EFC', 'EFVM', 'FTC', 'FTL', 'FCA', 'RMN', 'RMP', 'RMO', 'RMS', 'MRS', 'EFPO', 'FNSTN']
lista3 = ['TU', 'TKU']
# Definição do Layout do APP
app.layout = html.Div([
        html.Div([

            html.Div([
                dcc.Dropdown(
                    id='yaxis-column',
                    options=[{'label': i, 'value': i} for i in lista1],
                    value='EFC'
                ),

            ],style={'width': '20%', 'float': 'right', 'display': 'inline-block'}),
            html.Div([
                dcc.Markdown(children=intro)],
                style={'marginLeft': '5%', 'float': 'center', 'width': '80%', 'textAlign': 'justify', 'display': 'inline-block'}),
            html.Div([
            dcc.RadioItems(
                id='yxaxis-type',
                options=[{'label': i, 'value': i} for i in ['TU', 'TKU']],
                value='TU',
                labelStyle={'marginLeft': '5%', 'display': 'inline-block'}
            )
            ]),
        ]),



    html.Div([
    dcc.Graph(id='1'),
    dcc.Graph(id='2'),
                html.Div([
                    dcc.Graph(id='3')],
                    style={'width': '48%', 'display': 'inline-block'}),
                    html.Div([
                        dcc.Graph(id='4')],
                        style={'width': '48%', 'display': 'inline-block'}
                        ),

    dcc.Markdown(children=parte2, style={'marginLeft': '5%'}),
    dcc.Graph(id='5'),
    dcc.Graph(id='6'),

            html.Div([
            dcc.RadioItems(
                id='seção temporal',
                options=[{'label': i, 'value': i} for i in ['Todo o histórico', '2014-2018']],
                value='2014-2018',
                labelStyle={'marginLeft': '5%', 'display': 'inline-block'}
            )
            ]),

    dcc.Graph(id='7'),
    dcc.Graph(id='8'),
    dcc.Graph(id='9'),
    dcc.Graph(id='10'),

    dcc.Markdown(children=parte3, style={'marginLeft': '5%'}),
    dcc.Graph(id='11'),

                html.Div([
                    dcc.Graph(id='12')],
                    style={'width': '48%', 'display': 'inline-block'}),
                    html.Div([
                        dcc.Graph(id='13')],
                        style={'width': '48%', 'display': 'inline-block'}
                        ),
    
    dcc.Markdown(children=parte4, style={'marginLeft': '5%'}),
    dcc.Graph(id='14')
    ]),

])
@app.callback(
    Output('1', 'figure'),
    [Input('yaxis-column', 'value'),
    Input('yxaxis-type', 'value')])
def update_graph1(yaxis_column_name, yxaxis_column_name):
    x=pd.date_range('2006-1', '2019-7', freq='m')    
    y1 = df_prod[yaxis_column_name][yxaxis_column_name]

    trace1 = go.Scatter(x=x,
                        y=y1,
                        mode='lines+markers',
                        name='Produção de Transporte',                            
                        #text="R² = "+str(rsq)
                        )
    
    data = [trace1]

    return {
            'data': data,
            'layout': {
            'title':'Produção de Transporte - ' + str(yaxis_column_name),
            'xaxis':{'title': 'Ano'},
            'yaxis':{'title':str(yxaxis_column_name)},
        }

    }

@app.callback(
    Output('2', 'figure'),
    [Input('yaxis-column', 'value')])
def update_graph2(yaxis_column_name):
    x=pd.date_range('2010-11', '2019-7', freq='m')    
    y1 = df_trem_formado[yaxis_column_name]['TremKm - Trem Formado']
    y2 = df_tremkm[yaxis_column_name]['Trem Km - Siade']

    trace1 = go.Scatter(x=x,
                        y=y1,
                        mode='lines+markers',
                        name='TremKm - Trem Formado',                            
                        #text="R² = "+str(rsq)
                        )
    
    trace2 = go.Scatter(x=x,
                        y=y2,
                        mode='lines+markers',
                        name='Trem Km - Siade',
                        #text="R² = "+str(rsq)
                        )
    data = [trace1, trace2]

    return {
            'data': data,
            'layout': {
            'title':'Trem km - ' + str(yaxis_column_name),
            'xaxis':{'title': 'Ano'},
            'yaxis':{'title': 'Trem km'},
            
            'legend': {
                'orientation':'h'
            }
            }


    }

@app.callback(
    Output('3', 'figure'),
    [Input('yaxis-column', 'value')])
def update_graph3(yaxis_column_name):

    x = df_tremkm[yaxis_column_name]['Trem Km - Siade'].astype(float),
    y = df_siade[yaxis_column_name]['TKU - Siade'].astype(float),    
    correlation = np.corrcoef(x, y)[0,1]
    rsq = correlation**2
    rsq = round(rsq, 4)
    #print(rsq)

    trace1 = go.Scatter(x=df_tremkm[yaxis_column_name]['Trem Km - Siade'],
                        y=df_siade[yaxis_column_name]['TKU - Siade'],
                        mode='markers',                          
                        #text="R² = "+str(rsq)
                        )

    data = [trace1]

    return {
            'data': data,
            'layout': {
            'title':str(yaxis_column_name) + ' - Trem Km vs. TKU: R² = ' + str(rsq),
            'xaxis':{'title': 'Trem KM'},
            'yaxis':{'title': 'TKU'},
            
            'legend': {
                'orientation':'h'
            }
            }


    }

@app.callback(
    Output('4', 'figure'),
    [Input('yaxis-column', 'value')])
def update_graph4(yaxis_column_name):
    x=pd.date_range('2010-11', '2019-7', freq='m')    
    y1 = df_siade[yaxis_column_name]['TKU - Siade']
    y2 = df_tremkm[yaxis_column_name]['Trem Km - Siade']

    trace1 = go.Scatter(x=x,
                        y=y1,
                        mode='lines',
                        name='TKU',
                        yaxis='y2'                            
                        #text="R² = "+str(rsq)
                        )
    
    trace2 = go.Scatter(x=x,
                        y=y2,
                        mode='lines',
                        name='Trem km',
                        #text="R² = "+str(rsq)
                        )
    data = [trace1, trace2]

    return {
            'data': data,
            'layout': go.Layout(
                title='Produção de Transporte vs. Trem Km',
                yaxis=dict(
                    title='yaxis title'
                ),
                yaxis2=dict(
                    title='yaxis2 title',
                    titlefont=dict(
                        color='rgb(148, 103, 189)'
                    ),
                    tickfont=dict(
                        color='rgb(148, 103, 189)'
                    ),
                    overlaying='y',
                    side='right'
                )
            )
    }

@app.callback(
    Output('5', 'figure'),
    [Input('yaxis-column', 'value')])
def update_graph5(yaxis_column_name):
    x = pd.date_range('2006-01', '2019-4', freq='m')
    y1 = consolidadoImobLoc[yaxis_column_name]
    y2 = consolidadoDispLoc[yaxis_column_name]

    trace1 = go.Scatter(x=x,
                        y=y1,
                        mode='lines+markers',
                        name='Taxa de Imobilização',                            
                        #text="R² = "+str(rsq)
                        )
    
    trace2 = go.Scatter(x=x,
                        y=y2,
                        mode='lines+markers',
                        name='Taxa de Utilização da Disponibilidade',
                        #text="R² = "+str(rsq)
                        )
    data = [trace1, trace2]

    return {
            'data': data,
            'layout': {
            'title':'Indicadores de Material Rodante - Locomotiva',
            'xaxis':{'title': 'Ano'},
            'yaxis':{'title': ''},
            
            'legend': {
                'orientation':'h'
            }
            }


    }

@app.callback(
    Output('6', 'figure'),
    [Input('yaxis-column', 'value')])
def update_graph6(yaxis_column_name):
    x = pd.date_range('2006-01', '2019-4', freq='m')
    y1 = consolidadoImobVag[yaxis_column_name]
    y2 = consolidadoDispVag[yaxis_column_name]

    trace1 = go.Scatter(x=x,
                        y=y1,
                        mode='lines+markers',
                        name='Taxa de Imobilização',                            
                        #text="R² = "+str(rsq)
                        )
    
    trace2 = go.Scatter(x=x,
                        y=y2,
                        mode='lines+markers',
                        name='Taxa de Utilização da Disponibilidade',
                        #text="R² = "+str(rsq)
                        )
    data = [trace1, trace2]

    return {
            'data': data,
            'layout': {
            'title':'Indicadores de Material Rodante - Vagão',
            'xaxis':{'title': 'Ano'},
            'yaxis':{'title': ''},
            
            'legend': {
                'orientation':'h'
            }
            }


    }

@app.callback(
    Output('7', 'figure'),
    [Input('yaxis-column', 'value'),
    Input('seção temporal', 'value')])
def update_graph7(yaxis_column_name, sec_temporal):
    if sec_temporal == 'Todo o histórico':
        df1 = consolidadoImobLoc
        fig=go.Figure()
        for i in df1.keys():
            fig.add_trace(go.Box(
                y=df1[i],
                x0=str(i),
                name=i,
                boxpoints='all',
                boxmean=True
            ))
        fig.update_layout(title_text="Taxa de Imbilização de Locomotiva")
    else:
        df1 = consolidadoImobLoc
        fig=go.Figure()
        for i in df1.keys():
            fig.add_trace(go.Box(
                y=df1[i].iloc[96:],
                x0=str(i),
                name=i,
                boxpoints='all',
                boxmean=True
            ))
        fig.update_layout(title_text="Taxa de Imbilização de Locomotiva")

    return fig

@app.callback(
    Output('8', 'figure'),
    [Input('yaxis-column', 'value'),
    Input('seção temporal', 'value')])
def update_graph8(yaxis_column_name, sec_temporal):
    if sec_temporal == 'Todo o histórico':
        df2 = consolidadoImobVag
        fig=go.Figure()
        for i in df2.keys():
            fig.add_trace(go.Box(
                y=df2[i],
                x0=str(i),
                name=i,
                boxpoints='all',
                boxmean=True
            ))
        fig.update_layout(title_text="Taxa de Imbilização de Vagão")
    else:
        df2 = consolidadoImobVag
        fig=go.Figure()
        for i in df2.keys():
            fig.add_trace(go.Box(
                y=df2[i].iloc[96:],
                x0=str(i),
                name=i,
                boxpoints='all',
                boxmean=True
            ))
        fig.update_layout(title_text="Taxa de Imbilização de Vagão")

    return fig

@app.callback(
    Output('9', 'figure'),
    [Input('yaxis-column', 'value'),
    Input('seção temporal', 'value')])
def update_graph9(yaxis_column_name, sec_temporal):
    if sec_temporal == 'Todo o histórico':
        df3 = consolidadoDispLoc
        fig=go.Figure()
        for i in df3.keys():
            fig.add_trace(go.Box(
                y=df3[i],
                x0=str(i),
                name=i,
                boxpoints='all',
                boxmean=True
            ))
        fig.update_layout(title_text="Taxa de Utilização da Disponibilidade de Locomotiva")
    else:
        df3 = consolidadoDispLoc
        fig=go.Figure()
        for i in df3.keys():
            fig.add_trace(go.Box(
                y=df3[i].iloc[96:],
                x0=str(i),
                name=i,
                boxpoints='all',
                boxmean=True
            ))
        fig.update_layout(title_text="Taxa de Utilização da Disponibilidade de Locomotiva")

    return fig

@app.callback(
    Output('10', 'figure'),
    [Input('yaxis-column', 'value'),
    Input('seção temporal', 'value')])
def update_graph10(yaxis_column_name, sec_temporal):
    if sec_temporal == 'Todo o histórico':
        df4 = consolidadoDispVag
        fig=go.Figure()
        for i in df4.keys():
            fig.add_trace(go.Box(
                y=df4[i],
                x0=str(i),
                name=i,
                boxpoints='all',
                boxmean=True
            ))
        fig.update_layout(title_text="Taxa de Utilização da Disponibilidade de Vagão")
    else:
        df44 = consolidadoDispVag
        fig=go.Figure()
        for i in df44.keys():
            fig.add_trace(go.Box(
                y=df44[i].iloc[96:],
                x0=str(i),
                name=i,
                boxpoints='all',
                boxmean=True
            ))
        fig.update_layout(title_text="Taxa de Utilização da Disponibilidade de Vagão")

    return fig

@app.callback(
    Output('11', 'figure'),
    [Input('yaxis-column', 'value')])
def update_graph11(yaxis_column_name):
    x = pd.date_range('2010-11', '2019-4', freq='m')
    y1 = df_Abastecimento[yaxis_column_name]['LitrosViagem']
    y2 = df_Locomotiva[yaxis_column_name]['NumeroConsumoCombustivel']

    trace1 = go.Scatter(x=x,
                        y=y1,
                        mode='lines+markers',
                        name='Quantidade Abastecida')
    trace2 = go.Scatter(x=x,
                        y=y2,
                        mode='lines+markers',
                        name='Quantidade Consumida')
    data = [trace1, trace2]

    return {
            'data': data,
            'layout': {
            'title':'Consumo de Combustível - ' + str(format(yaxis_column_name)),
            'xaxis':{'title': 'Ano'},
            'yaxis':{'title': 'Litros de Diesel'},
            
            'legend': {
                'orientation':'h'
            }
            }


    }

@app.callback(
    Output('12', 'figure'),
    [Input('yaxis-column', 'value')])
def update_graph12(yaxis_column_name):
    y = df_Siade[yaxis_column_name]['TKU']
    x = df_Locomotiva[yaxis_column_name]['NumeroConsumoCombustivel']

    y=y
    x=x
    correlation = np.corrcoef(x, y)[0,1]
    rsq = correlation**2
    rsq = round(rsq, 4)
    #print(rsq)    

    trace1 = go.Scatter(x=x,
                        y=y,
                        mode='markers',
                        #text="R² = "+str(rsq)
                        )
    data = [trace1]

    return {
            'data': data,
            'layout': {
            'title':'Dispersão - TKU vs. Consumo (R² = '+str(rsq)+')',
            'xaxis':{'title': 'Litros'},
            'yaxis':{'title': 'TKU'},
            'hovermode':'closest'
        }

    }

@app.callback(
    Output('13', 'figure'),
    [Input('yaxis-column', 'value')])
def update_graph13(yaxis_column_name):
    x = pd.date_range('2010-11', '2019-4', freq='m')    
    y = df_Consumo[yaxis_column_name]['Consumo Médio - L/ mil TKU']

    trace1 = go.Scatter(x=x,
                        y=y,
                        mode='lines+markers',
                        #text="R² = "+str(rsq)
                        )
    data = [trace1]

    return {
            'data': data,
            'layout': {
            'title':'Consumo Relativo - L/mil TKU',
            'xaxis':{'title': 'Ano'},
            'yaxis':{'title': 'L/mil TKU'},
        }

    }

@app.callback(
    Output('14', 'figure'),
    [Input('yaxis-column', 'value')])
def update_graph14(yaxis_column_name):
    x = pd.date_range('2006-01', '2019-7', freq='m')
    y1 = df_SiadeFluxos[yaxis_column_name]['Velocidade - Siade']
    y2 = df_TremKMV[yaxis_column_name]['Velocidade Média Comercial (km/h)']
    y3 = df_TremKMV[yaxis_column_name]['Velocidade Média do Percurso (km/h)']

    trace1 = go.Scatter(x=x,
                        y=y1,
                        mode='lines+markers',
                        name = 'Velocidade - Fluxos de Transp.',
                        #text="R² = "+str(rsq)
                        )
    trace2 = go.Scatter(x=x,
                        y=y2,
                        mode='lines+markers',
                        name = 'Velocidade Média Comercial',
                        #text="R² = "+str(rsq)
                        )
    trace3 = go.Scatter(x=x,
                        y=y3,
                        mode='lines+markers',
                        name = 'Velocidade Média de Percurso',
                        #text="R² = "+str(rsq)
                        )                        
    data = [trace1, trace2, trace3]

    return {
            'data': data,
            'layout': {
            'title':'Velocidade - ' + str(format(yaxis_column_name)),
            'xaxis':{'title': 'Ano'},
            'yaxis':{'title': 'km/h'},
            
            'legend': {
                'orientation':'h'
            }
            }


    }

if __name__ == '__main__':
    app.run_server()
