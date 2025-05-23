from textual.app import App, ComposeResult  # Import base classes for Textual apps
from textual.widgets import Footer, Header, Digits, Button, LoadingIndicator  # Import UI widgets
from textual.containers import VerticalScroll
import yfinance as yf  # Import yfinance for fetching stock data
import re
from textual_plotext import PlotextPlot

HOLDINGS = {
    "SAAB-B.ST": [1, 500],
    "SSAB-B.ST": [1, 500],
    "^OMX": [0, 0],
    "MSFT": [1, 500]
}

PERIOD = "1d"
INTERVAL = "1m"
UPDATE_INTERVAL = 60

def AllSymbolObjectsID():
    obj = []
    for symbol in HOLDINGS:
        obj_name = Clean_symbol(symbol)
        obj.append(f"{globals()[obj_name]}")
        return obj

def get_only_id(buttonid):
    return re.sub(r'[0-9]', '', buttonid)

def Clean_symbol(symbol):
    return re.sub(r'[^a-zA-Z0-9]', '', str(symbol))

class Tickersymbol():
    def __init__(self,symbol, quantity, value):
        stock = yf.Ticker(symbol)
        self.symbol = symbol
        self.quantity = quantity
        self.value = value
        self.history = stock.history(period=PERIOD, interval=INTERVAL)
        self.datetime = self.history.index
        self.close = self.history["Close"]
        self.open = self.history["Open"]
        self.high = self.history["High"]
        self.low = self.history["Low"]
        self.volume = self.history["Volume"]
        self.currency = stock.info["currency"]

class TickerClosedPrice(Digits):
    """Displays digits"""

class SymbolWatcher2(App):
        
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    def __init__(self):
        super().__init__()
        self.ticker_widgets = {}
        self.plot_widget = None  # Will hold the PlotextPlot widget

    CSS = """
    PlotextPlot {
        height: 20;
    }
"""

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll():
            for idx, ticker in enumerate(HOLDINGS.keys()):
                yield Button(ticker, id=f"ticker{idx}")
                price_widget = TickerClosedPrice("...")
                self.ticker_widgets[ticker] = price_widget
                yield price_widget
            self.plot_widget = PlotextPlot(id="plot")
            yield self.plot_widget  # Add the plot widget to the UI
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button = event.button
        clean_symbol = Clean_symbol(button.label)
        obj = globals()[clean_symbol]
        # Update the plot with the selected ticker's close prices
        if not obj.history.empty:
            y = list(range(len(obj.datetime)))
            # x = 1,2,3,4,5,6,7,8,9
            # y = 1,2,3,4,5,6,7,8,9
            self.plot_widget.plt.clf()
            self.plot_widget.plt.plot(y, obj.close, label=obj.symbol)
            self.plot_widget.plt.title(f"{obj.symbol} Close Prices")
            self.plot_widget.plt.xlabel("Time")
            self.plot_widget.plt.ylabel("Close")
            self.plot_widget.refresh()

    async def on_mount(self) -> None:
        await self.update_prices()
        self.set_interval(UPDATE_INTERVAL, self.update_prices)

    async def update_prices(self) -> None:
        for symbol, (quantity, value) in HOLDINGS.items():
            globals()[Clean_symbol(symbol)] = Tickersymbol(symbol, quantity, value)
            if not globals()[Clean_symbol(symbol)].history.empty:
                closing = globals()[Clean_symbol(symbol)].close.iloc[-1]
                self.ticker_widgets[symbol].update(f"{closing:.2f}")
            else:
                self.ticker_widgets[symbol].update("N/A")

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

if __name__ == "__main__":
    app = SymbolWatcher2()
    app.run()
