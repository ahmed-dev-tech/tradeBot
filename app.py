from flask import Flask, render_template, request, flash, redirect, jsonify
import config, csv, datetime
from binance.client import Client
from binance.enums import *
import bot

app = Flask(__name__)
app.secret_key = b'somelongrandomstring'

client = Client(config.API_KEY, config.API_SECRET, tld='us')
#Bot Params
STREAM_SYMBOL=request.form['symbol']
TRADE_SYMBOL=request.form['trade_symbol']
TRADE_QUANTITY=request.form['quantity']
RSI_PERIOD=request.form['rsi_length']
RSI_OVERBOUGHT= request.form['rsi_overbought']
RSI_OVERSOLD= request.form['rsi_oversold']
STREAM_DURATION = request.form['steam_duration']
#Bot init
RsiBot = bot.Bot(RSI_PERIOD,RSI_OVERBOUGHT,RSI_OVERSOLD,STREAM_SYMBOL,STREAM_DURATION,TRADE_QUANTITY,TRADE_SYMBOL)
@app.route('/')
def index():
    title = 'BotView'
    if RsiBot.onmessage()=='Sell Sucessfull':
        action = "bought {TRADE_SYMBOL}"
    else:
        action = "Sell {TRADE_SYMBOL}"
    # account = client.get_account()
    # balances = account['balances']
    # exchange_info = client.get_exchange_info()
    # symbols = exchange_info['symbols']
    return render_template('index.html', title=title, action=action)

# @app.route('/buy', methods=['POST'])
# def buy():
#     print(request.form)
#     try:
#         order = client.create_order(symbol=request.form['symbol'], 
#             side=SIDE_BUY,
#             type=ORDER_TYPE_MARKET,
#             quantity=request.form['quantity'])

#     except Exception as e:
#         flash(e.message, "error")
#     return None #returns suc

@app.route('/history')
def history():
    candlesticks = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_15MINUTE, "1 Jul, 2020", "12 Jul, 2020")
    processed_candlesticks = []
    for data in candlesticks:
        candlestick = { 
            "time": data[0] / 1000, 
            "open": data[1],
            "high": data[2], 
            "low": data[3], 
            "close": data[4]
        }
        processed_candlesticks.append(candlestick)
    return jsonify(processed_candlesticks)