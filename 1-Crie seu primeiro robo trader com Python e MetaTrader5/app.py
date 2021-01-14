import pandas as pd                     # Pandas
import numpy as np                      # NumPy
import MetaTrader5 as mt5               # MetaTrader5
import talib.abstract as ta             # TA-Lib
import datetime as dt                   # Datetime (biblioteca inclusa)
import time                             # Time (biblioteca inclusa)

# Definição da funlçao de obtenção de dados históricos.
def baixar_dados_historicos(ativo, intervalo, inicio, final):
    """Faz o download dos dados com base nos parâmetros definidos, formata os dados, e salva na pasta do projeto em formato CSV."""

    # Faz o download dos dados com base nos parâmetros definidos.
    mt5_dados_historicos = mt5.copy_rates_range(ativo, intervalo, inicio, final)

    # Formata os dados.
    dados_historicos = pd.DataFrame(mt5_dados_historicos)
    dados_historicos.rename(columns={'time': 'Date', 'open': 'Open','high': 'High', 'low': 'Low', 'close': 'Close', 'tick_volume': 'Volume'}, inplace=True)
    dados_historicos['Date'] = pd.to_datetime(dados_historicos['Date'], unit='s')
    dados_historicos.set_index('Date', inplace=True)
    dados_historicos.drop(columns=['spread', 'real_volume'], inplace=True)

    # Retorna os valores históricos em formato de objeto DataFrame.
    return dados_historicos

# Definição da função de produção da estratégia.
def produzir_estrategia(dados_historicos):
    """Produz os valores dos estudos utilizados. Nesse caso utilizamos Bandas de Bollinger e Índice de Força Relativa. Em seguida, produz os sinais de compra ou venda."""

    # Produz os valores dos estudos utilizados.
    BB_estudo = ta.BBANDS(dados_historicos['Close'], timeperiod=14, nbdevup=2.0, nbdevdn=2.0, matype=0)
    IFR_estudo = ta.RSI(dados_historicos['Close'], timeperiod=14)

    # Adiciona os estudos ao histórico de preços baixado na etapa anterior.
    dados_estrategia = dados_historicos.copy()
    dados_estrategia['BB_Superior'] = BB_estudo[0]
    dados_estrategia['BB_Media'] = BB_estudo[1]
    dados_estrategia['BB_Inferior'] = BB_estudo[2]
    dados_estrategia['IFR'] = IFR_estudo

    # Produz os sinais de compra ou venda.
    dados_estrategia['Sinal_BB'] = np.where(dados_estrategia['Close'] < dados_estrategia['BB_Inferior'], 1, np.where(dados_estrategia['Close'] > dados_estrategia['BB_Superior'], -1, 0))
    dados_estrategia['Sinal_IFR'] = np.where(dados_estrategia['IFR'] > 15, 1, 0)
    dados_estrategia['Decisao'] = np.where((dados_estrategia['Sinal_BB'] == 1) & (dados_estrategia['Sinal_IFR'] == 1), 'Compra', np.where((dados_estrategia['Sinal_BB'] == -1) & (dados_estrategia['Sinal_IFR'] == 1), 'Venda', 'Aguarde'))

    # Salva na pasta do projeto em formato CSV.
    dados_estrategia.to_csv(ativo + '.csv', index=True, encoding='utf-8')

    # Retorna os valores históricos + estudos em formato de objeto DataFrame.
    return dados_estrategia

# Carteira começa vazia.
ativos_comprados = []
tickets = {}

while True:

    horario_atual = dt.datetime.now()
    time.sleep(60 - (horario_atual.second + horario_atual.microsecond/1000000.0))

    # Definição de parâmetros.
    ativo = 'PETR4'                     # Ativo escolhido. Deve seguir a mesma formatação de como é mostrado no MetaTrader5.
    intervalo = mt5.TIMEFRAME_M15       # Constante utilizada pelo MetaTrader5 para intervalo de 15 minutos.
    inicio = dt.datetime(2021, 1, 4)    # Data inicial. Para fins de exemplo, utilizamos dia 04/01/2021.
    final = dt.datetime.now()           # Data e hora finais. Como a ideia é atualizar dinamicamente, usaremos o momento atual.

    # Execução do MetaTrader5.
    if not mt5.initialize():
        mt5.shutdown()

    # Execução da função definida acima.
    dados_historicos = baixar_dados_historicos(ativo, intervalo, inicio, final)

    dados_estrategia = produzir_estrategia(dados_historicos)

    horario_atual = dt.datetime.strftime(horario_atual, '%Y-%m-%d %H:%M')                           # Horário atual em formato de texto.
    volume = 100.0                                                                                  # Volume a ser comprado/vendido de determinado ativo. Padrão definido em 100 = 1 lote de ações.

    if (dados_estrategia['Decisao'].iloc[-1] == 'Compra') and (ativo not in ativos_comprados):      # Se decisão é compra e o ativo ainda não foi comprado.

        # Preenchimento da boleta de compra.
        boleta_compra = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': ativo,
            'volume': volume,
            'price': mt5.symbol_info_tick(ativo).ask,
            'type': mt5.ORDER_TYPE_BUY,
            'type_filling': mt5.ORDER_FILLING_RETURN,
            'magic': 123456
        }

        # Envio da ordem de compra a mercado e inclusão do ativo na lista de ativos comprados.
        ordem_compra = mt5.order_send(boleta_compra)
        ativos_comprados.append(ativo)
        tickets[ativo] = ordem_compra.order
        print('(' + horario_atual + ') Comprando ' + str(volume) + ' ' + ativo + '...')

    elif (dados_estrategia['Decisao'].iloc[-1] == 'Venda') and (ativo in ativos_comprados):         # Se decisão é venda e o ativo já esteja comprado.

        # Preenchimento da boleta de venda.
        boleta_venda = {
            'action': mt5.TRADE_ACTION_DEAL,
            'symbol': ativo,
            'volume': volume,
            'type': mt5.ORDER_TYPE_SELL,
            'position': tickets[ativo],
            'magic': 123456
        }

        # Envio da ordem de venda a mercado e retirada do ativo da lista de ativos comprados.
        ordem_venda = mt5.order_send(boleta_venda)                      
        ativos_comprados.remove(ativo)
        tickets.pop(ativo)
        print('(' + horario_atual + ') Vendendo ' + str(volume) + ' ' + ativo + '...')
        
    else:                                                                                           # Se decisão é esperar.

        print('(' + horario_atual + ') Aguarde...')