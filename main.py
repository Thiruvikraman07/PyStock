import os
import csv
import sys

import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib import style
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import yfinance

from BuySell import *
from Live_data import UpdateThread

colour1 = "#69F0AE"
colour2 = "#00E676"
font = "Ariel"
code = "AAPL"
startdate = "10/20/2000"

update_thread = UpdateThread(code=code)


def update_all():
    update_thread.code = code
    update_thread.change_data = True
    app.stock_info.historic_plot.update_graph()
    app.stock_info.update_info('live')


class PyStock(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        stocks = open('stock_list.txt').read().split('\n')

        stock_list = StockList(stocks, master=self)
        stock_list.grid(row=0, column=0, sticky='ns')

        self.stock_info = StockInfo(master=self)
        self.stock_info.grid(row=0, column=1, sticky='ns')

    def on_close(self):
        self.destroy()
        sys.exit()


class StockList(tk.PanedWindow):
    def __init__(self, stocks, *args, **kwargs):
        tk.PanedWindow.__init__(self, *args, **kwargs)

        view_port = tk.Canvas(self, width=250, height=700)
        container = tk.Frame(view_port)
        scroll_bar = tk.Scrollbar(self,
                                  orient='vertical',
                                  command=view_port.yview,
                                  bg=colour2,
                                  troughcolor=colour1)

        container_conf = lambda event: view_port.configure(scrollregion=view_port.bbox("all"))
        container.bind("<Configure>", container_conf)

        view_port.configure(yscrollcommand=scroll_bar.set)

        scroll_bar.pack(side='right', fill='y')
        view_port.pack(side='left', fill='both', expand=True)
        view_port.create_window((0, 0), window=container, anchor='nw')

        stock_buttons = []
        for i in range(len(stocks)):
            stock_buttons.append(StockButton(stocks[i], master=container, bg=colour1))
            stock_buttons[i].grid(row=i, column=0)


class StockButton(tk.Button):
    def __init__(self, stock_name, *args, **kwargs):
        tk.Button.__init__(self,
                           text=stock_name,
                           width=35, height=3,
                           relief='flat',
                           command=self.button_callback,
                           *args, **kwargs
                           )
        self.stock = stock_name

    def button_callback(self):
        global code
        code = self.stock.split(',')[-1].strip()
        update_all()


class StockInfo(tk.PanedWindow):
    def __init__(self, *args, **kwargs):
        tk.PanedWindow.__init__(self, *args, **kwargs)
        self.live_plot = LivePlot(master=self)
        self.historic_plot = HistoricPlot(master=self)

        details_container = tk.Frame(master=self, bg=colour1, padx=10, pady=10)
        details_container.pack(side='left', fill='y')

        self.details = tk.Text(master=details_container,
                               font=font,
                               relief='flat',
                               bg=colour2,
                               padx=10, pady=10,
                               width=31, height=20)
        self.details.grid(row=2, column=0, columnspan=2)

        self.price_label = tk.Label(details_container,
                                    relief='flat', font=font,
                                    justify='left', bg='#ffffff',
                                    width=30)
        self.price_label.grid(row=0, column=0, pady=10, ipadx=5, ipady=5)

        self.live_button = tk.Button(details_container, relief='flat',
                                     text='   SHOW LIVE   ',
                                     font=font, command=lambda: self.update_info('live'))
        self.historic_button = tk.Button(details_container, relief='flat',
                                         text='   SHOW HISTORIC   ',
                                         font=font, command=lambda: self.update_info('historic'))
        self.stock_ops = StockOps(master=details_container, bg=colour1, padx=10, pady=10)
        self.stock_ops.grid(row=3, column=0)

    def update_info(self, graph_type):
        if graph_type == 'live':
            self.live_plot.pack(side='right', fill='y')
            self.historic_plot.pack_forget()
            self.live_button.grid_forget()
            self.historic_button.grid(row=1, column=0, pady=10, ipadx=10, ipady=5)
        elif graph_type == 'historic':
            self.historic_plot.pack(side='right', fill='y')
            self.live_plot.pack_forget()
            self.historic_button.grid_forget()
            self.live_button.grid(row=1, column=0, pady=10, ipadx=10, ipady=5)
        else:
            tk.messagebox.showerror(title="InvalidOperation",
                                    message=f"Cannot update_info graph of type: {graph_type}", )

        try:
            self.stock_ops.total_stock.configure(text=f"Total stock: {Total_Stock(code)}")
        except:
            self.stock_ops.total_stock.configure(text=f"Total stock:")

        try:
            self.stock_ops.avg_stock.configure(text=f"Average value: {average_price(code)}")

        except:
            self.stock_ops.avg_stock.configure(text=f"Average value:")

        self.details.delete('1.0', 'end')
        information = update_thread.stock.info
        self.details.insert('insert', f"""52 Week Change: {information['52WeekChange']}\nAvg. Volume: {information['averageVolume']}\nBeta: {information['beta']}\nForward Dividend & Yield: {information['dividendYield']}\nMarket Cap: {information['marketCap']}\nOpen: {information['open']}\nEPS (TTM): {information['forwardEps']}\nPE Ratio (TTM): {information['forwardPE']}\nPrevious Close: {information['previousClose']}\nVolume: {information['volume']}""")


class StockOps(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.total_stock = tk.Label(master=self,
                                    relief='flat', font=font,
                                    bg=colour2)
        self.avg_stock = tk.Label(master=self,
                                  relief='flat', font=font,
                                  bg=colour2)
        qty_label = tk.Label(master=self,
                             relief='flat', font=font,
                             text='Quantity: ', bg=colour2)
        self.qty_entry = tk.Entry(master=self,
                                  relief='flat', font=font,
                                  bg='#ffffff')

        button_container = tk.Frame(master=self, relief='flat', bg=colour1)
        buy_button = tk.Button(master=button_container,
                               relief='flat', font=font,
                               text='BUY', command=self.buy)
        sell_button = tk.Button(master=button_container,
                                relief='flat', font=font,
                                text='SELL', command=self.sell)

        self.total_stock.grid(row=0, column=0, sticky='news', columnspan=2, pady=1)
        self.avg_stock.grid(row=1, column=0, sticky='news', columnspan=2, pady=1)


        qty_label.grid(row=2, column=0, sticky='news', pady=1)
        self.qty_entry.grid(row=2, column=1, sticky='news', pady=1)

        button_container.grid(row=3, column=0, columnspan=2, pady=2)
        buy_button.grid(row=0, column=0, ipadx=20, sticky='news', padx=2)
        sell_button.grid(row=0, column=1, ipadx=20, sticky='news', padx=2)

    def buy(self):
        price = update_thread.live_price
        qty = self.get_amount()
        action = "Buy"

        try:
            conn.execute(f'''INSERT INTO {code} VALUES({price * qty},{qty},'{action.upper()}');''')
        except:
            conn.execute(f'''CREATE TABLE {code} (PRICE FLOAT , QTY INT , ACTION VARCHAR(4));''')
            conn.execute(f'''INSERT INTO {code} VALUES({price * qty},{qty},'{action.upper()}');''')

        conn.commit()
        update_all()

    def sell(self):
        price = update_thread.live_price
        qty = self.get_amount()
        action = "Sell"

        if Total_Stock(code) >= qty:

            try:
                conn.execute(f'''INSERT INTO {code} VALUES({price * qty},{qty},'{action.upper()}');''')
            except:
                tk.messagebox.showerror(title="InvalidOperation",
                                        message=f"NO STOCKS")
        else:
            tk.messagebox.showerror(title="InvalidOperation",
                                    message=f"YOU DO NOT HAVE THAT MUCH STOCK QTY")
        conn.commit()
        update_all()

    def get_amount(self):
        try:
            return float(self.qty_entry.get())
        except ValueError:
            tk.messagebox.showerror(title="InvalidOperation",
                                    message=f"Please enter a valid amount")


class LivePlot(tk.Frame):
    def __init__(self, *args, **kwargs):

        tk.Frame.__init__(self, *args, **kwargs)
        self.figure = Figure(figsize=(6, 6.5), dpi=100)

        self.axis = self.figure.add_subplot(111)
        self.axis.axes.xaxis.set_visible(False)
        plt.tick_params(axis='y', which='major', labelsize="10")
        plt.grid(True)
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(self.figure, self)

        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.ani = animation.FuncAnimation(self.figure, self.animate, interval=1000)

    def animate(self, i):
        num_lines = len(update_thread.live_data)

        if num_lines <= 200:
            xList = []
            yList = []
            for eachLine in update_thread.live_data:
                if len(eachLine) > 1:
                    x, y = eachLine.split(',')
                    yList.append(float(x))
                    xList.append((y))
            self.axis.clear()
            self.axis.plot(xList, yList)
        else:
            update_thread.live_data = update_thread.live_data[-200::]


class HistoricPlot(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.fig = Figure(figsize=(6, 6.5), dpi=100)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        self.canvas.get_tk_widget().pack()

    def update_graph(self):
        dataframe = update_thread.stock.history(period='1mo', interval='1d')
        dataframe.reset_index(inplace=True)
        dataframe.set_index("Date", inplace=True)
        dataframe = dataframe.drop("Volume", axis=1)
        try:
            dataframe = dataframe.drop("Dividends", axis=1)
            dataframe = dataframe.drop("Stock Splits", axis=1)
        except:
            pass
        
        plot1 = self.fig.add_subplot(111)
        plot1.clear()
        plot1.plot(dataframe)
        plt.setp(plot1.get_xticklabels(), rotation=30, horizontalalignment='right')
        self.fig.tight_layout()
        self.canvas.draw()


app = PyStock()
update_thread.root = app
update_all()
update_thread.start()
app.title('PyStock')
app.geometry('1200x700+0+0')
app.resizable(0, 0)
app.protocol("WM_DELETE_WINDOW", app.on_close)
app.mainloop()