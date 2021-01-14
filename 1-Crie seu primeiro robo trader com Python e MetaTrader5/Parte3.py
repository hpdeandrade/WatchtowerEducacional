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