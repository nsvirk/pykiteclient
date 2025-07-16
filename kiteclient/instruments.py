# -*- coding: utf-8 -*-
"""
    instruments.py

"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
import csv
import requests
from io import StringIO


@dataclass
class Instrument:
    """Dataclass representing a single instrument from Kite API."""
    instrument_token: int
    exchange_token: int
    tradingsymbol: str
    name: str
    last_price: float
    expiry: Optional[date]
    strike: float
    tick_size: float
    lot_size: int
    instrument_type: str
    segment: str
    exchange: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Instrument':
        """Create an Instrument instance from a dictionary."""
        # Parse expiry date if present
        expiry = None
        if data.get('expiry') and data['expiry'] != '':
            try:
                expiry = datetime.strptime(data['expiry'], '%Y-%m-%d').date()
            except ValueError:
                pass

        return cls(
            instrument_token=int(data['instrument_token']),
            exchange_token=int(data['exchange_token']),
            tradingsymbol=data['tradingsymbol'],
            name=data['name'],
            last_price=float(data['last_price']),
            expiry=expiry,
            strike=float(data['strike']),
            tick_size=float(data['tick_size']),
            lot_size=int(data['lot_size']),
            instrument_type=data['instrument_type'],
            segment=data['segment'],
            exchange=data['exchange']
        )


class KiteInstruments:
    """
    A class to query Kite Connect instruments data using method chaining.

    """

    INSTRUMENTS_URL = "https://api.kite.trade/instruments"
    _instruments_cache: List[Instrument] = []
    _cache_loaded = False

    def __init__(self):
        self._filters = {}
        self._load_instruments_if_needed()

    @classmethod
    def _load_instruments_if_needed(cls) -> None:
        """Load instruments data from the Kite API if not already loaded."""
        if not cls._cache_loaded:
            try:
                response = requests.get(cls.INSTRUMENTS_URL)
                response.raise_for_status()

                # Parse CSV data
                csv_data = StringIO(response.text)
                reader = csv.DictReader(csv_data)

                cls._instruments_cache = []
                for row in reader:
                    instrument = Instrument.from_dict(row)
                    cls._instruments_cache.append(instrument)

                cls._cache_loaded = True

            except requests.RequestException as e:
                raise Exception(f"Failed to load instruments data: {e}")
            except Exception as e:
                raise Exception(f"Error parsing instruments data: {e}")

    def name(self, name: str) -> 'KiteInstruments':
        """Filter by instrument name."""
        new_instance = KiteInstruments()
        new_instance._filters = self._filters.copy()
        new_instance._filters['name'] = name
        return new_instance

    def instrument_type(self, instrument_type: str) -> 'KiteInstruments':
        """Filter by instrument type (FUT, CE, PE, etc.)."""
        new_instance = KiteInstruments()
        new_instance._filters = self._filters.copy()
        new_instance._filters['instrument_type'] = instrument_type
        return new_instance

    def exchange(self, exchange: str) -> 'KiteInstruments':
        """Filter by exchange."""
        new_instance = KiteInstruments()
        new_instance._filters = self._filters.copy()
        new_instance._filters['exchange'] = exchange
        return new_instance

    def segment(self, segment: str) -> 'KiteInstruments':
        """Filter by segment."""
        new_instance = KiteInstruments()
        new_instance._filters = self._filters.copy()
        new_instance._filters['segment'] = segment
        return new_instance

    def expiry(self, expiry: Union[str, date]) -> 'KiteInstruments':
        """Filter by expiry date. Accepts string in 'YYYY-MM-DD' format or date object."""
        new_instance = KiteInstruments()
        new_instance._filters = self._filters.copy()

        if isinstance(expiry, str):
            try:
                expiry_date = datetime.strptime(expiry, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError("Expiry date must be in YYYY-MM-DD format")
        else:
            expiry_date = expiry

        new_instance._filters['expiry'] = expiry_date
        return new_instance

    def strike(self, strike: float) -> 'KiteInstruments':
        """Filter by strike price."""
        new_instance = KiteInstruments()
        new_instance._filters = self._filters.copy()
        new_instance._filters['strike'] = strike
        return new_instance

    def tradingsymbol(self, tradingsymbol: str) -> 'KiteInstruments':
        """Filter by trading symbol."""
        new_instance = KiteInstruments()
        new_instance._filters = self._filters.copy()
        new_instance._filters['tradingsymbol'] = tradingsymbol
        return new_instance

    def instrument_token(self, instrument_token: int) -> 'KiteInstruments':
        """Filter by instrument token."""
        new_instance = KiteInstruments()
        new_instance._filters = self._filters.copy()
        new_instance._filters['instrument_token'] = instrument_token
        return new_instance

    def exchange_token(self, exchange_token: int) -> 'KiteInstruments':
        """Filter by exchange token."""
        new_instance = KiteInstruments()
        new_instance._filters = self._filters.copy()
        new_instance._filters['exchange_token'] = exchange_token
        return new_instance

    def lot_size(self, lot_size: int) -> 'KiteInstruments':
        """Filter by lot size."""
        new_instance = KiteInstruments()
        new_instance._filters = self._filters.copy()
        new_instance._filters['lot_size'] = lot_size
        return new_instance

    def tick_size(self, tick_size: float) -> 'KiteInstruments':
        """Filter by tick size."""
        new_instance = KiteInstruments()
        new_instance._filters = self._filters.copy()
        new_instance._filters['tick_size'] = tick_size
        return new_instance

    def strike_range(self, min_strike: float, max_strike: float) -> 'KiteInstruments':
        """Filter by strike price range (inclusive)."""
        new_instance = KiteInstruments()
        new_instance._filters = self._filters.copy()
        new_instance._filters['strike_range'] = (min_strike, max_strike)
        return new_instance

    def has_expiry(self, has_expiry: bool = True) -> 'KiteInstruments':
        """Filter instruments that have or don't have expiry."""
        new_instance = KiteInstruments()
        new_instance._filters = self._filters.copy()
        new_instance._filters['has_expiry'] = has_expiry
        return new_instance

    def _matches_filters(self, instrument: Instrument) -> bool:
        """Check if an instrument matches all applied filters."""
        for filter_name, filter_value in self._filters.items():
            if filter_name == 'name' and instrument.name != filter_value:
                return False
            elif filter_name == 'instrument_type' and instrument.instrument_type != filter_value:
                return False
            elif filter_name == 'exchange' and instrument.exchange != filter_value:
                return False
            elif filter_name == 'segment' and instrument.segment != filter_value:
                return False
            elif filter_name == 'expiry' and instrument.expiry != filter_value:
                return False
            elif filter_name == 'strike' and instrument.strike != filter_value:
                return False
            elif filter_name == 'tradingsymbol' and instrument.tradingsymbol != filter_value:
                return False
            elif filter_name == 'instrument_token' and instrument.instrument_token != filter_value:
                return False
            elif filter_name == 'exchange_token' and instrument.exchange_token != filter_value:
                return False
            elif filter_name == 'lot_size' and instrument.lot_size != filter_value:
                return False
            elif filter_name == 'tick_size' and instrument.tick_size != filter_value:
                return False
            elif filter_name == 'strike_range':
                min_strike, max_strike = filter_value
                if not (min_strike <= instrument.strike <= max_strike):
                    return False
            elif filter_name == 'has_expiry':
                has_expiry = instrument.expiry is not None
                if has_expiry != filter_value:
                    return False

        return True

    def get_all(self) -> List[Instrument]:
        """Execute the query and return filtered instruments."""
        results = []

        for instrument in self._instruments_cache:
            # Apply all filters
            if not self._matches_filters(instrument):
                continue
            results.append(instrument)

        return results

    def get_first(self) -> Optional[Instrument]:
        """Get the first instrument matching the filters."""
        results = self.get_all()
        return results[0] if results else None

    def get_count(self) -> int:
        """Count instruments matching the filters."""
        return len(self.get_all())

    def get_exists(self) -> bool:
        """Check if any instruments match the filters."""
        return self.get_count() > 0

    def get_unique(self, field: str) -> List[Any]:
        """Get unique values for a specific field from current filter results."""
        results = self.get_all()
        values = set()
        for instrument in results:
            value = getattr(instrument, field, None)
            if value is not None:
                values.add(value)
        return sorted(list(values))

    def get_expiries(self) -> List[date]:
        """Get unique expiry dates for current filter results."""
        results = self.get_all()
        return sorted(list(set(inst.expiry for inst in results if inst.expiry)))

    def get_strikes(self) -> List[float]:
        """Get unique strikes for current filter results."""
        results = self.get_all()
        return sorted(list(set(inst.strike for inst in results)))

    def get_option_chain(self) -> List[Instrument]:
        """Get option chain for current filter results."""
        results = self.get_all()
        calls = [inst for inst in results if inst.instrument_type == "CE"]
        puts = [inst for inst in results if inst.instrument_type == "PE"]
        return calls + puts

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of filtered instruments."""
        results = self.get_all()

        summary = {
            'total_instruments': len(results),
            'by_type': {},
            'by_exchange': {},
            'by_segment': {},
            'unique_names': set()
        }

        for inst in results:
            # Count by instrument type
            summary['by_type'][inst.instrument_type] = summary['by_type'].get(inst.instrument_type, 0) + 1

            # Count by exchange
            summary['by_exchange'][inst.exchange] = summary['by_exchange'].get(inst.exchange, 0) + 1

            # Count by segment
            summary['by_segment'][inst.segment] = summary['by_segment'].get(inst.segment, 0) + 1

            # Collect unique names
            summary['unique_names'].add(inst.name)

        summary['unique_names'] = len(summary['unique_names'])

        return summary

    def __repr__(self) -> str:
        """String representation showing applied filters."""
        filters_str = ", ".join([f"{k}={v}" for k, v in self._filters.items()])
        return f"KiteInstruments({filters_str})"



