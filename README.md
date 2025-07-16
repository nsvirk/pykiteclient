# Kite Connect API Python custom client

- An UNofficial Python client for interacting with the [Kite Connect API](https://kite.trade).
- Does not replicate the `kiteconnect` package functionality.
- Provides extended functionality.

## Installing the client

You can install the pre release via pip or uv

```bash
pip install --upgrade kiteclient

uv add kiteclient
```

## Documentation

### Kite Sessions

Generate a Kite User Session programmatically.

```python
from kiteclient.sessions import KiteSessions, User, UserSession

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

See [example](examples/sessions.py)
