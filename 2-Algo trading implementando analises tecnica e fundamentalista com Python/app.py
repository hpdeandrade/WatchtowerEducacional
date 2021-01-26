import pandas as pd                     # Pandas
import numpy as np                      # NumPy
import talib.abstract as ta             # TA-Lib
import MetaTrader5 as mt5               # MetaTrader5
import yfinance as yf                   # Yahoo Finance
import quandl                           # Quandl
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

# Definição da função de produção da estratégia.
def produzir_estrategia_robo3(dados_historicos, ativo):
    """Gera sinais de compra ou venda baseado nas análises técnica e fundamentalista."""

    # ROBÔ 1 - ANÁLISE TÉCNICA.

    # Produz os valores dos estudos utilizados.
    SMA30_estudo = ta.SMA(dados_historicos['Close'], timeperiod=30)
    SMA90_estudo = ta.SMA(dados_historicos['Close'], timeperiod=90)

    # Adiciona os estudos ao histórico de preços baixado na etapa anterior.
    dados_estrategia_robo3 = dados_historicos.copy()
    dados_estrategia_robo3['SMA30'] = SMA30_estudo
    dados_estrategia_robo3['SMA90'] = SMA90_estudo

    # ROBÔ 2 - ANÁLISE FUNDAMENTALISTA.

    # Download de informações sobre o ativo.
    ativo_yf = yf.Ticker(ativo + '.SA')     # Ajuste baseado na formatação exigida pelo Yahoo Finance.

    # Obtenção da DRE e BP.
    dre_trimestral = ativo_yf.quarterly_financials
    bp_trimestral = ativo_yf.quarterly_balance_sheet

    # Cálculo de margem líquida.
    n_trimestres = 3
    receita_trimestral = dre_trimestral[dre_trimestral.index == 'Total Revenue']
    lucro_trimestral = dre_trimestral[dre_trimestral.index == 'Net Income']
    margem_liquida_trimestral = lucro_trimestral.div(receita_trimestral.values).iloc[:, 0:n_trimestres]
    margem_liquida_trimestral.rename(index={'Net Income': 'Net Margin'}, inplace=True)
    media_margem_liquida = margem_liquida_trimestral.mean(axis=1)[0]

    # Cálculo de alavancagem (D / (D + E)).
    n_trimestres = 1
    divida_cp = bp_trimestral[bp_trimestral.index == 'Short Long Term Debt']
    divida_lp = bp_trimestral[bp_trimestral.index == 'Long Term Debt']
    divida_total = divida_cp.add(divida_lp.values)
    patrimonio_liquido = bp_trimestral[bp_trimestral.index == 'Total Stockholder Equity']
    divida_mais_patrimonio_liquido = divida_total.add(patrimonio_liquido.values)
    alavancagem_bp = divida_total.div(divida_mais_patrimonio_liquido.values).iloc[:, 0:n_trimestres]
    alavancagem_bp.rename(index={'Short Long Term Debt': 'Alavancagem BP'}, inplace=True)
    media_alavancagem_bp = alavancagem_bp.mean(axis=1)[0]

    # Preço do minério de ferro.
    quandl.ApiConfig.api_key = 'YOUR_QUANDL_API_KEY' # Obtenha de graça ao se cadastrar na Quandl para fazer 50+ chamadas de API por dia.
    hoje_string = dt.datetime.now().strftime('%Y-%m-%d')
    preco_minerio = quandl.get('ODA/PIORECR_USD', start_date='2020-01-01', end_date=hoje_string, collapse='daily').iloc[-1][0]

    # Sinais robô 1.
    sinal_compra_robo1 = (dados_estrategia_robo3['SMA30'] > dados_estrategia_robo3['SMA90']) & (dados_estrategia_robo3['SMA30'].shift(1, fill_value=0) <= dados_estrategia_robo3['SMA90'].shift(1, fill_value=0))
    sinal_venda_robo1 = (dados_estrategia_robo3['SMA30'] < dados_estrategia_robo3['SMA90']) & (dados_estrategia_robo3['SMA30'].shift(1, fill_value=0) >= dados_estrategia_robo3['SMA90'].shift(1, fill_value=0))
    dados_estrategia_robo3['Sinal_Robo1'] = np.where(sinal_compra_robo1, 1, np.where(sinal_venda_robo1, -1, 0))
    sinal = 'Sim' if dados_estrategia_robo3['Sinal_Robo1'].iloc[-1] != 0 else 'Não'

    # Sinais robô 2.
    sinal_compra_robo2 = (media_margem_liquida > 0.1) & (media_alavancagem_bp < 0.5) & (preco_minerio < 100)
    sinal_venda_robo2 = (media_margem_liquida < 0.05) & (media_alavancagem_bp > 0.7)
    dados_estrategia_robo3['Sinal_Robo2'] = np.where(sinal_compra_robo1, 1, np.where(sinal_venda_robo1, -1, 0))

    # Sinais robô 3.
    sinal_compra_robo3 = (dados_estrategia_robo3['Sinal_Robo1'] == 1) & (dados_estrategia_robo3['Sinal_Robo2'] == 1)
    sinal_venda_robo3 = (dados_estrategia_robo3['Sinal_Robo1'] == -1) & (dados_estrategia_robo3['Sinal_Robo2'] == -1)
    dados_estrategia_robo3['Sinal_Robo3'] = np.where(sinal_compra_robo3, 1, np.where(sinal_venda_robo3, -1, 0))
    dados_estrategia_robo3['Decisao'] = np.where(dados_estrategia_robo3['Sinal_Robo3'] == 1, 'Compra', np.where(dados_estrategia_robo3['Sinal_Robo3'] == -1, 'Venda', 'Aguarde'))

    # Resumo.
    resumo = {
        'Cruzamento média': sinal,
        'Margem líquida (média trimestral)': '{:.1%}'.format(media_margem_liquida),
        'Alavancagem (último trimestre)': '{:.1%}'.format(media_alavancagem_bp),
        'Preço minério de ferro (último disponivel)': 'US$' + '{:,.2f}'.format(preco_minerio)
    }

    print('\n------------------')
    for k,v in resumo.items(): 
        print(k + ': ' + v)
    print('------------------\n')

    # Salva na pasta do projeto em formato CSV.
    dados_estrategia_robo3.to_csv(ativo + '.csv', index=True, encoding='utf-8')

    # Retorna os valores históricos + estudos em formato de objeto DataFrame.
    return dados_estrategia_robo3

# Carteira começa vazia.
ativos_comprados = []
tickets = {}

atualizacao_dinamica = False
while True:

    horario_atual = dt.datetime.now()
    time.sleep(60 - (horario_atual.second + horario_atual.microsecond/1000000.0))

    # Definição de parâmetros.
    ativo = 'VALE3'                         # Ativo escolhido. Deve seguir a mesma formatação de como é mostrado no MetaTrader5.
    intervalo = mt5.TIMEFRAME_D1            # Constante utilizada pelo MetaTrader5 para intervalo de 1 dia.
    inicio = dt.datetime(2020, 1, 1)        # Data inicial. Para fins de exemplo, utilizamos dia 01/01/2020.
    final = dt.datetime.now()               # Data e hora finais. Como a ideia é atualizar dinamicamente, usaremos o momento atual.

    # Execução do MetaTrader5.
    if not mt5.initialize():
        mt5.shutdown()

    # Verifica se o ativo escolhido está disponível/habilitado na plataforma do MetaTrader5.
    ativos_disponiveis = mt5.symbols_get(group='*' + ativo + '*')
    if ativo in ativo in [ativos_disponiveis[n].name for n in range(len(ativos_disponiveis))]:
        mt5.symbol_select(ativo, True)

    else:
        print('Ativo selecionado inválido. Verifique se o mesmo está disponível na corretora sincronizada com o MetaTrader5.')
        exit()

    # Execução da função definida acima.
    dados_historicos = baixar_dados_historicos(ativo, intervalo, inicio, final)
    dados_estrategia_robo3 = produzir_estrategia_robo3(dados_historicos, ativo)

    horario_atual = dt.datetime.strftime(horario_atual, '%Y-%m-%d %H:%M')                                   # Horário atual em formato de texto.
    volume = 100.0                                                                                          # Volume a ser comprado/vendido de determinado ativo. Padrão definido em 100 = 1 lote de ações. Pode ser alterado.

    if (dados_estrategia_robo3['Decisao'].iloc[-1] == 'Compra') and (ativo not in ativos_comprados):        # Se decisão é compra e o ativo ainda não foi comprado.

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

    elif (dados_estrategia_robo3['Decisao'].iloc[-1] == 'Venda') and (ativo in ativos_comprados):           # Se decisão é venda e o ativo já esteja comprado.

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
        
    else:                                                                                                   # Se decisão é esperar.
        print('(' + horario_atual + ') Nenhum sinal por enquanto...')

    if not atualizacao_dinamica:
        break