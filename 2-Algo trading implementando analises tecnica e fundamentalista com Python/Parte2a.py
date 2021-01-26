# Definição da função de estratégia do robô 1 - análise técnica.
def produzir_estrategia_robo1(dados_historicos):
    """Gera sinais de compra ou venda baseado em análise técnica. Nesse caso observamos o cruzamento de médias móveis."""

    # ROBÔ 1 - ANÁLISE TÉCNICA.

    # Produz as médias móveis conforme parâmetros definidos.
    SMA30_estudo = ta.SMA(dados_historicos['Close'], timeperiod=30)
    SMA90_estudo = ta.SMA(dados_historicos['Close'], timeperiod=90)

    # Adiciona os estudos ao histórico de preços baixado na etapa anterior.
    dados_estrategia_robo1 = dados_historicos.copy()
    dados_estrategia_robo1['SMA30'] = SMA30_estudo
    dados_estrategia_robo1['SMA90'] = SMA90_estudo

    # Produz os sinais de compra ou venda.
    sinal_compra = (dados_estrategia_robo1['SMA30'] > dados_estrategia_robo1['SMA90']) & (dados_estrategia_robo1['SMA30'].shift(1, fill_value=0) <= dados_estrategia_robo1['SMA90'].shift(1, fill_value=0))
    sinal_venda = (dados_estrategia_robo1['SMA30'] < dados_estrategia_robo1['SMA90']) & (dados_estrategia_robo1['SMA30'].shift(1, fill_value=0) >= dados_estrategia_robo1['SMA90'].shift(1, fill_value=0))
    dados_estrategia_robo1['Sinal_Robo1'] = np.where(sinal_compra, 1, np.where(sinal_venda, -1, 0))
    dados_estrategia_robo1['Decisao'] = np.where(dados_estrategia_robo1['Sinal_Robo1'] == 1, 'Compra', np.where(dados_estrategia_robo1['Sinal_Robo1'] == -1, 'Venda', 'Aguarde'))

    # Retorna os valores históricos + sinais em formato de objeto DataFrame.
    return dados_estrategia_robo1