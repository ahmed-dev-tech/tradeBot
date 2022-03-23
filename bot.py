import os
import websocket, json, pprint,talib, numpy
import config
from binance.client import Client
from binance.enums import *
import telebot
TELE_API_KEY = os.getenv('API_KEY')
bot = telebot.TeleBot(TELE_API_KEY)

# self.RSI_PERIOD = 14
# RSI_OVERBOUGHT = 70
# RSI_OVERSOLD = 30
# self.TRADE_SYMBOL = 'ETHUSD'
# self.TRADE_QUANTITY = 0.05

closes = []
in_position = False

# client = Client(config.API_KEY, config.API_SECRET, tld='us')
class Bot():
    def __init__(self, RSI_PERIOD,RSI_OVERBOUGHT,RSI_OVERSOLD,STREAM_SYMBOL,STREAM_DURATION,TRADE_QUANTITY,TRADE_SYMBOL):
        self.RSI_PERIOD=RSI_PERIOD
        self.RSI_OVERBOUGHT=RSI_OVERBOUGHT
        self.RSI_OVERSOLD=RSI_OVERSOLD
        self.STREAM_SYMBOL=STREAM_SYMBOL
        self.STREAM_DURATION=STREAM_DURATION
        self.TRADE_QUANTITY=TRADE_QUANTITY
        self.TRADE_SYMBOL=TRADE_SYMBOL
    SOCKET = "wss://stream.binance.com:9443/ws/{self.STREAM_SYMBOL}@kline_{self.STREAM_DURATION}"
    def order(self,side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
        try:
            print("sending order")
            order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
            print(order)
        except Exception as e:
            print("an exception occured - {}".format(e))
            return False
        return True

    def on_open(self,ws):
        print('opened connection')

    def on_close(self,ws):
        print('closed connection')

    def on_message(self,ws, message):
        json_message = json.loads(message)
        pprint.pprint(json_message)

        candle = json_message['k']

        is_candle_closed = candle['x']
        close = candle['c']
        if is_candle_closed:
            print("candle closed at {}".format(close))
            closes.append(float(close))
            print("closes")
            print(closes)

            if len(closes) > self.RSI_PERIOD:
                np_closes = numpy.array(closes)
                rsi = talib.RSI(np_closes, self.RSI_PERIOD)
                print("all rsis calculated so far")
                print(rsi)
                last_rsi = rsi[-1]
                print("the current rsi is {}".format(last_rsi))

                if last_rsi > RSI_OVERBOUGHT:
                    if in_position:
                        print("Overbought! Sell! Sell! Sell!")
                        # put binance sell logic here
                        order_succeeded = order(SIDE_SELL, self.TRADE_QUANTITY, self.TRADE_SYMBOL)
                        if order_succeeded:
                            in_position = False                                            
                        # put telegram sell signal logic here
                        @bot.message_handler(func=order_succeeded)                   
                        def sendSellSignal(message):
                            bot.send_message(message.chat.id, "Sell {self.TRADE_SYMBOL}")

                    else:
                        print("It is overbought, but we don't own any. Nothing to do.")
                
                if last_rsi < RSI_OVERSOLD:
                    if in_position:
                        print("It is oversold, but you already own it, nothing to do.")
                    else:
                        print("Oversold! Buy! Buy! Buy!")
                        # put binance buy order logic here
                        order_succeeded = order(SIDE_BUY, self.TRADE_QUANTITY, self.TRADE_SYMBOL)
                        if order_succeeded:
                            in_position = True
                        # put telegram buy signal logic here
                        @bot.message_handler(func=order_succeeded)                   
                        def sendBuySignal(message):
                            bot.send_message(message.chat.id, "BUY {self.TRADE_SYMBOL}")
    bot.polling()
    ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
    ws.run_forever()