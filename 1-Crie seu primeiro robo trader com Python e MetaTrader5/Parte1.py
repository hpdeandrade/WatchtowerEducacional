import pandas as pd                     # Pandas
import numpy as np                      # NumPy
import MetaTrader5 as mt5               # MetaTrader5
import talib.abstract as ta             # TA-Lib
import datetime as dt                   # Datetime (biblioteca inclusa)
import time                             # Time (biblioteca inclusa)

# Definição da função de obtenção de dados históricos.
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

# Definição de parâmetros.
ativo = 'PETR4'                         # Ativo escolhido. Deve seguir a mesma formatação de como é mostrado no MetaTrader5.
intervalo = mt5.TIMEFRAME_M15           # Constante utilizada pelo MetaTrader5 para intervalo de 15 minutos.
inicio = dt.datetime(2021, 1, 4)        # Data inicial. Para fins de exemplo, utilizamos dia 04/01/2021.
final = dt.datetime.now()               # Data e hora finais. Como a ideia é atualizar dinamicamente, usaremos o momento atual.

# Execução do MetaTrader5.
if not mt5.initialize():
    mt5.shutdown()

# Verifica se o ativo escolhido está disponível/habilitado na plataforma do MetaTrader5.
ativos_disponiveis = mt5.symbols_get(group='*' + ativo + '*')
if ativo in ativo in [ativos_disponiveis[n].name for n in range(len(ativos_disponiveis))]:
    mt5.symbol_select(ativo, True)
else:
    print('Ativo selecionado inválido. Verifique se o mesmo está disponível na plataforma do MetaTrader5.')

# Execução da função definida acima.
dados_historicos = baixar_dados_historicos(ativo, intervalo, inicio, final)