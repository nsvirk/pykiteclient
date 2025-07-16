from kiteclient import KiteInstruments, Instrument


print("-" * 80)
print("KiteInstruments Examples")
print()
print("-" * 80)

# Example 1: Get NIFTY futures
nifty_futures = KiteInstruments().name("NIFTY").instrument_type("FUT").get_all()
print(f"NIFTY Futures: {len(nifty_futures)} found")
print()
print("-" * 80)

# Example 2: Get first NIFTY future
nifty_future = KiteInstruments().name("NIFTY").instrument_type("FUT").get_first()
print(f"NIFTY First Future: {nifty_future.tradingsymbol}")
print()
print("-" * 80)

# Example 3: Get BANKEX call options
bankex_calls = KiteInstruments().name("BANKEX").instrument_type("CE").strike(64000.0).get_count()
print(f"BANKEX 64000 Calls: {bankex_calls} found")
print()
print("-" * 80)

# Example 4: Check if NIFTY futures exist
nifty_exists = KiteInstruments().name("NIFTY").instrument_type("FUT").get_exists()
print(f"NIFTY Futures exists: {nifty_exists}")
print()
print("-" * 80)

# Example 5: Get expiries and first expiry
expiries = KiteInstruments().name("NIFTY").instrument_type("CE").get_expiries()
first_expiry = KiteInstruments().name("NIFTY").instrument_type("CE").get_first().expiry
print(f"NIFTY Expiries: {len(expiries)} found")
print(f"NIFTY First Expiry: {first_expiry}")
print()
print("-" * 80)

# Example 6: Get strikes
strikes = KiteInstruments().name("NIFTY").instrument_type("CE").expiry(first_expiry).get_strikes()
print(f"NIFTY CE Strikes: {len(strikes)} found")
print()
print("-" * 80)

# Example 7: Get strikes in a range
strikes_in_range = KiteInstruments().name("NIFTY").instrument_type("CE").expiry(first_expiry).strike_range(25000, 25200).get_all()
print(f"NIFTY Calls strikes in range 25000-25200: {len(strikes_in_range)} found")
print()
print("-" * 80)

# Example 8: Get option chain
option_chain = KiteInstruments().name("NIFTY").expiry(first_expiry).get_option_chain()
print(f"NIFTY Option Chain: {len(option_chain)} found")
print()
print("-" * 80)

# Example 9: Using as dataclass
nifty_future_dataclass = KiteInstruments().name("NIFTY").instrument_type("FUT").get_first()
print(f"NIFTY Future as dataclass: {nifty_future_dataclass}")
print()
print("-" * 80)

# Example 10: Get summary
summary = KiteInstruments().name("NIFTY").expiry(first_expiry).get_summary()
print(f"NIFTY Summary for {first_expiry} expiry: {summary}")
print()
print("-" * 80)