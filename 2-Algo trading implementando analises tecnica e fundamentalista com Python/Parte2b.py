# Definição da função de estratégia do robô 2 - análise fundamentalista.
def produzir_estrategia_robo2(dados_historicos, ativo):
    """Gera sinais de compra ou venda baseado em análise fundamentalista. Nesse caso observamos as métricas de rentabilidade, alavancagem e preço do minério de ferro."""

    # ROBÔ 2 - ANÁLISE FUNDAMENTALISTA.

    # Download de informações sobre o ativo.
    ativo_yf = yf.Ticker(ativo + '.SA')                     # Ajuste baseado na formatação exigida pelo Yahoo Finance.

    # Obtenção da DRE e BP através do Yahoo Finance.
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
    quandl.ApiConfig.api_key = 'YOUR_QUANDL_API_KEY'        # Obtenha de graça ao se cadastrar na Quandl para fazer 50+ chamadas de API por dia.
    hoje_string = dt.datetime.now().strftime('%Y-%m-%d')
    preco_minerio = quandl.get('ODA/PIORECR_USD', start_date='2020-01-01', end_date=hoje_string, collapse='daily').iloc[-1][0]

    # Sinais robô 2.
    sinal_compra_robo2 = (media_margem_liquida > 0.1) & (media_alavancagem_bp < 0.5) & (preco_minerio < 100)
    sinal_venda_robo2 = (media_margem_liquida < 0.05) & (media_alavancagem_bp > 0.7)
    dados_estrategia_robo2 = dados_historicos.copy()
    dados_estrategia_robo2['Sinal_Robo2'] = np.where(sinal_compra_robo2, 1, np.where(sinal_venda_robo2, -1, 0))
    dados_estrategia_robo2['Decisao'] = np.where(dados_estrategia_robo2['Sinal_Robo2'] == 1, 'Compra', np.where(dados_estrategia_robo2['Sinal_Robo2'] == -1, 'Venda', 'Aguarde'))

    # Retorna os valores históricos + sinais em formato de objeto DataFrame.
    return dados_estrategia_robo2