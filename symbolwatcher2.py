from textual.app import App, ComposeResult  # Import base classes for Textual apps
from textual.widgets import Footer, Header, Digits, Button, LoadingIndicator  # Import UI widgets
import yfinance as yf  # Import yfinance for fetching stock data
import re
import matplotlib.pyplot as plt

# Holdings: ticker symbol mapped to [number of shares, buy price] # will be used to calculate portfolio worth
HOLDINGS = {
    "SAAB-B.ST": [1, 500],
    "SSAB-B.ST": [1, 500],
    "^OMX": [0, 0],
    "MSFT": [1, 500],
    "AAPL": [5, 100],
    "AMZN": [1, 100],
}

# Constants for yfinance API
PERIOD = "1d"  # Fetch data for 1 day
INTERVAL = "1m"  # Fetch data at 1-minute intervals
UPDATE_INTERVAL = 60  # Update prices every 60 seconds


# Plot colours
OPEN_COLOUR = "green"
CLOSE_COLOUR = "red"
HILO_INT_COLOUR = "orange"
CLOSE_OPEN_INT_COLOUR = "red"
VOLUME_COLOUR = "grey"

def AllSymbolObjectsID():
    obj = []
    for symbol in HOLDINGS:
        obj_name = Clean_symbol(symbol)
        obj.append(f"{globals()[obj_name]}")
        return obj
    

def Clean_symbol(symbol):
        return re.sub(r'[^a-zA-Z0-9]', '', str(symbol))

class Tickersymbol():
    
    def __init__(self,symbol, quantity, value):
        stock = yf.Ticker(symbol)
        self.symbol = symbol      # Store the Symbol
        self.quantity = quantity  # Store the quantity
        self.value = value        # Store the value
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
    # Inherits from Digits widget to show price values

class SymbolWatcher2(App):
    # Main application class
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]  # Keyboard shortcut for dark mode
    def __init__(self):
        super().__init__()  # Initialize parent class
        self.ticker_widgets = {}  # Dictionary to hold ticker widgets

    def compose(self) -> ComposeResult:
        # Compose the UI layout
        for idx, ticker in enumerate(HOLDINGS.keys()):
            yield Button(ticker, id=f"ticker{idx}")  # Add a button for each ticker
            price_widget = TickerClosedPrice("...")  # Placeholder for price
            self.ticker_widgets[ticker] = price_widget  # Store widget for updates
            yield price_widget  # Add price widget to UI
        yield Header()  # Add header to UI
        yield Footer()  # Add footer to UI
    
    # watches for event if button is clicked
    def on_button_pressed(self, event: Button.Pressed) -> None:
        button = event.button  # Get the button that was pressed
        clean_symbol = Clean_symbol(button.label)
        obj = globals()[clean_symbol]
        # Create a new figure for each symbol to allow multiple windows
        fig = plt.figure(obj.symbol)  # Create a new figure window
        ax = fig.add_subplot(111)
        ax.plot(obj.datetime, obj.close, label="Close", color=CLOSE_COLOUR)
        plt.title(obj.symbol)
        plt.xlabel("Time")
        plt.ylabel("Price")
        plt.draw()
        plt.show()
        #fig.canvas.manager.set_window_title(obj.symbol)  # Set window title to symbol
        #plt.show(block=False)  # Non-blocking show to allow multiple windows https://stackoverflow.com/questions/28269157/plotting-in-a-non-blocking-way-with-matplotlib

    async def on_mount(self) -> None:
        # Called when app is ready
        await self.update_prices()  # Fetch initial prices
        self.set_interval(UPDATE_INTERVAL, self.update_prices)  # Schedule periodic updates

    async def update_prices(self) -> None:
        # Fetch and update prices for all tickers
        for symbol, (quantity, value) in HOLDINGS.items():
            globals()[Clean_symbol(symbol)] = Tickersymbol(symbol, quantity, value)
            if not globals()[Clean_symbol(symbol)].history.empty:
                closing = globals()[Clean_symbol(symbol)].close.iloc[-1]  # Get latest closing price
                self.ticker_widgets[symbol].update(f"{closing:.2f}")  # Update widget with 2 decimals
            else:
                self.ticker_widgets[symbol].update("N/A")  # Show N/A if no data

    def action_toggle_dark(self) -> None:
        # Toggle between dark and light themes
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

if __name__ == "__main__":
    app = SymbolWatcher2()  # Create app instance
    app.run()  # Run the app
