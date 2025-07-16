# Kite Connect API Python custom client

- An UNofficial Python client for interacting with the [Kite Connect API](https://kite.trade).
- Does not replicate the `kiteconnect` package functionality.
- Provides extended functionality.

## Installing the client

### Install from github repo

```bash

uv add git+https://github.com/nsvirk/pykiteclient.git
```

## Documentation

### Kite Sessions

Generate a Kite User Session automatically.

#### Example code for KiteSessions

```python
from kiteclient import KiteSessions, User, UserSession

# Create a User
user = User(
    user_id=os.getenv("KITE_USER_ID"),
    password=os.getenv("KITE_PASSWORD"),
    totp_secret=os.getenv("KITE_TOTP_SECRET"),
    api_key=os.getenv("KITE_API_KEY"),
    api_secret=os.getenv("KITE_API_SECRET"),
)

# Generate a User Session
session: UserSession = KiteSessions().generate_session(user)

api_key = session.api_key
access_token = session.access_token
```

See [sessions](examples/sessions.py) examples for more.

### Kite Instruments

Query Kite instruments at `https://api.kite.trade/instruments` easily.

**Filter methods**: All methods not starting with `get` are filter methods and can be chained.

**Result Methods**: All methons starting with `get` are results methods and can only one of these be at the end of the filter methods chain.

#### Example code for KiteInstruments

```python
from kiteclient import KiteInstruments, Instrument

# Example 1: Get NIFTY futures
nifty_futures = KiteInstruments().name("NIFTY").instrument_type("FUT").get_all()
print(f"NIFTY Futures: {len(nifty_futures)} found")

# Example 2: Get first NIFTY future
nifty_future = KiteInstruments().name("NIFTY").instrument_type("FUT").get_first()
print(f"NIFTY First Future: {nifty_future.tradingsymbol}")

# Example 3: Get NIFTY expiries and first expiry
expiries = KiteInstruments().name("NIFTY").instrument_type("CE").get_expiries()

# Example 4: Get NIFTY first expiry
first_expiry = KiteInstruments().name("NIFTY").instrument_type("CE").get_first().expiry
```

See [instruments](examples/instruments.py) examples for more.
