from datetime import datetime
from threading import Thread
import yfinance as yf
import time

class UpdateThread(Thread):
    def __init__(self, code, *args, **kwargs):
        self.code = code
        self.change_data = False
        Thread.__init__(self, target=self.track_data, daemon=True)
        self.live_data = []
        self.root = None
        self.stock = yf.Ticker(self.code)
        self.live_price = 0
        self.currency = ''

    def track_data(self):
        while True:
            if self.change_data:
                self.live_data = []
                self.change_data = False
                self.root.stock_info.price_label.configure(text='LOADING...')
                self.stock = yf.Ticker(self.code)
                self.currency = self.stock.info['currency']
            else:
                a = (datetime.now().strftime("%H:%M:%S"))
                try:
                    self.live_price = round(self.stock.history(period='1m', interval='1m')['Close'][0], 6)
                except:
                    pass
                self.live_data.append(f"{self.live_price},{a}")
                self.root.stock_info.price_label.configure(text= f"{self.live_price} {self.currency}")