from textual.app import App, ComposeResult  # Import base classes for Textual apps
from textual.widgets import Footer, Header, Digits, Button  # Import UI widgets
from textual.reactive import reactive  # For reactive variables (not used here)
from textual import events  # For event handling (not used here)
import yfinance as yf  # Import yfinance for fetching stock data

# Constants for yfinance API
PERIOD = "1d"  # Fetch data for 1 day
INTERVAL = "1m"  # Fetch data at 1-minute intervals
UPDATE_INTERVAL = 60  # Update prices every 60 seconds

# Holdings: ticker symbol mapped to [number of shares, buy price]
HOLDINGS = {
    "SAAB-B.ST": [1, 500],
    "SSAB-B.ST": [1, 500],
    "^OMX": [0, 0],
    "MSFT": [1, 500],
    "AAPL": [5, 100],
    "AMZN": [1, 100],
}

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

    async def on_mount(self) -> None:
        # Called when app is ready
        await self.update_prices()  # Fetch initial prices
        self.set_interval(UPDATE_INTERVAL, self.update_prices)  # Schedule periodic updates

    async def update_prices(self) -> None:
        # Fetch and update prices for all tickers
        for ticker in HOLDINGS.keys():
            stock = yf.Ticker(ticker)  # Create yfinance Ticker object
            history = stock.history(period=PERIOD, interval=INTERVAL)  # Fetch price history
            if not history.empty:
                closing = history["Close"].iloc[-1]  # Get latest closing price
                self.ticker_widgets[ticker].update(f"{closing:.2f}")  # Update widget with 2 decimals
            else:
                self.ticker_widgets[ticker].update("N/A")  # Show N/A if no data

    def action_toggle_dark(self) -> None:
        # Toggle between dark and light themes
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

if __name__ == "__main__":
    app = SymbolWatcher2()  # Create app instance
    app.run()  # Run the app
