import logging
import os
from pprint import pprint
from dotenv import load_dotenv
from kiteclient.sessions import KiteSessions, User, UserSession

load_dotenv()

logging.basicConfig(level=logging.INFO)

# Create a User
user = User(
    user_id=os.getenv("KITE_USER_ID"),
    password=os.getenv("KITE_PASSWORD"),
    totp_secret=os.getenv("KITE_TOTP_SECRET"),
    api_key=os.getenv("KITE_API_KEY"),
    api_secret=os.getenv("KITE_API_SECRET"),
)

# Print the User
print("-" * 80)
print("User:")
print("-" * 80)
pprint(user)
print("\n")

# Generate a User Session
try:
    session: UserSession = KiteSessions().generate_session(user)
    # Print the User Session
    print("-" * 80)
    print("User Session:")
    print("-" * 80)
    pprint(session)
    print("-" * 80)
except Exception as e:
    # Print the error
    print("-" * 80)
    print("User Session Error:")
    print("-" * 80)
    print(f"Error Message   : {e.message}")
    print(f"Error Code      : {e.error_code}")
    print(f"Error Type      : {e.error_type}")
    print("-" * 80)
    exit(1)


# Delete the User Session
try:
    KiteSessions().delete_session(session.api_key, session.access_token)
    print("User Session deleted successfully")
    print("-" * 80)
except Exception as e:
    print("User Session deletion failed")
    print(e)
    print("-" * 80)
    exit(1)