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

dados_estrategia = produzir_estrategia(dados_historicos)