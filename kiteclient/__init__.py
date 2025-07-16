"""
KiteClient:
- An UNofficial Python client for interacting with the Kite Connect API.
- Does not replicate the `kiteconnect` package functionality.
- Provides extended functionality.

"""

__version__ = "1.0.0"
__author__ = "Navdeep Virk"
__email__ = "nsvirk@gmail.com"

from kiteclient.sessions import KiteSessions, User, UserSession
from kiteclient.instruments import KiteInstruments, Instrument

__all__ = ["KiteSessions", "User", "UserSession", "KiteInstruments", "Instrument"]