# -*- coding: utf-8 -*-
"""
    sessions.py

"""
from dataclasses import dataclass
import hashlib
from datetime import datetime
from urllib.parse import parse_qs, urlparse

import pyotp
import requests

@dataclass
class User:
    """
    Kite User Credentials
    """
    user_id: str
    password: str
    totp_secret: str
    api_key: str | None = None
    api_secret: str | None = None

@dataclass
class UserSession:
    """
    Dataclass for User Session
    """
    user_type: str
    email: str
    user_name: str
    user_shortname: str
    broker: str
    exchanges: list[str]
    products: list[str]
    order_types: list[str]
    avatar_url: str
    user_id: str
    api_key: str
    access_token: str
    public_token: str
    refresh_token: str
    enctoken: str
    login_time: str
    meta: dict
    kf_session: str


class KiteException(Exception):
    """Exception raised for Kite-specific errors."""

    def __init__(self, r: requests.Response) -> None:
        r_json = r.json()
        self.error_code = r.status_code
        self.error_type = r_json.get("error_type")
        self.message = r_json.get("message")
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.error_type}: {self.message}"


class TotpException(Exception):
    """Exception raised for TOTP generation errors."""

    def __init__(self, message: str) -> None:
        self.error_code = 500
        self.error_type = "TotpException"
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.error_type}: {self.message}"


class AuthException(Exception):
    """Exception raised for authentication errors."""

    def __init__(self, message: str) -> None:
        self.error_code = 500
        self.error_type = "AuthException"
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.error_type}: {self.message}"


class KiteSessions:
    """
    Generate Kite Sessions.
    """
    KITE_VERSION: str = "3"

    def __init__(self):
        self._session = requests.Session()
        self.timeout: int = 7
        self._session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Kite-Version": self.KITE_VERSION,
            }
        )

    def generate_session(self, user: User) -> UserSession:
        try:
            self.user_id = user.user_id
            self.password = user.password
            self.totp_secret = user.totp_secret
            self.api_key = user.api_key
            self.api_secret = user.api_secret
            if self.api_key and self.api_secret:
                api_session = self._generate_api_session()
                return UserSession(**api_session)
            else:
                oms_session = self._generate_oms_session()
                oms_profile = self._get_oms_profile(oms_session["enctoken"])
                oms_session.update(oms_profile)
                oms_session["login_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                oms_session["api_key"] = None
                oms_session["access_token"] = None
                oms_session["refresh_token"] = None
                return UserSession(**oms_session)

        except Exception as e:
            raise e

        finally:
            self._session.close()

    def delete_session(self, api_key: str, access_token: str) -> None:
        try:
            url = "https://api.kite.trade/session/token"
            data = {
                "api_key": api_key,
                "access_token": access_token,
            }
            r = self._session.delete(url, params=data)
            if r.status_code != 200:
                raise KiteException(r)

        except Exception as e:
            raise e
        finally:
            self._session.close()

    def generate_twofa_value(self, totp_secret: str) -> str:
        try:
            return pyotp.TOTP(totp_secret).now()
        except Exception as e:
            raise TotpException(e)

    def is_oms_session_valid(self, enctoken: str) -> bool:
        try:
            url = "https://kite.zerodha.com/oms/user/profile"
            self._session.headers.update({"Authorization": f"enctoken {enctoken}"})
            r = self._session.get(url)
            return r.status_code == 200
        except Exception as e:
            raise e

    def is_api_session_valid(self, api_key: str, access_token: str) -> bool:
        try:
            url = "https://api.kite.trade/user/profile"
            self._session.headers.update(
                {"Authorization": f"token {api_key}:{access_token}"}
            )
            r = self._session.get(url)
            return r.status_code == 200
        except Exception as e:
            raise e

    def _generate_oms_session(self) -> dict:
        try:
            # step 1: login request
            url = "https://kite.zerodha.com/api/login"
            data = {
                "user_id": self.user_id,
                "password": self.password,
                "type": "user_id",
            }
            r = self._session.post(url, data=data, timeout=self.timeout)
            if r.status_code != 200:
                raise KiteException(r)

            # step 1a: extract request_id and twofa_type from the response data
            r_json = r.json()
            r_data = r_json.get("data", {})
            request_id = r_data["request_id"]
            twofa_type = r_data["twofa_type"]

            # step 1b: extract profile data from response
            user_name = r_data.get("profile", {}).get("user_name")
            user_shortname = r_data.get("profile", {}).get("user_shortname")
            avatar_url = r_data.get("profile", {}).get("avatar_url")

            # step 1b: generate the twofa_value
            twofa_value = self.generate_twofa_value(self.totp_secret)

            # step 2: twofa request
            url = "https://kite.zerodha.com/api/twofa"
            data = {
                "user_id": self.user_id,
                "request_id": request_id,
                "twofa_type": twofa_type,
                "twofa_value": twofa_value,
            }
            r = self._session.post(url, data=data)
            if r.status_code != 200:
                raise KiteException(r)

            # step 2a: extract the response data
            r_json = r.json()
            r_data = r_json.get("data", {})
            r_cookies = self._session.cookies.get_dict()

            # step 2b: extract cookie data
            kf_session = r_cookies.get("kf_session")
            enctoken = r_cookies.get("enctoken")
            public_token = r_cookies.get("public_token")

            # step: geterate login_time
            login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # step 3 create result dict
            result = {
                "user_id": self.user_id,
                "user_name": user_name,
                "user_shortname": user_shortname,
                "avatar_url": avatar_url,
                "kf_session": kf_session,
                "enctoken": enctoken,
                "public_token": public_token,
                "login_time": login_time,
            }
            return result

        except Exception as e:
            raise e

    def _get_oms_profile(self, enctoken: str) -> dict:
        try:
            url = "https://kite.zerodha.com/oms/user/profile"
            self._session.headers.update({"Authorization": f"enctoken {enctoken}"})
            r = self._session.get(url)
            r_json = r.json()
            r_data = r_json.get("data", {})
            return r_data
        except Exception as e:
            raise e

    def _generate_api_session(self) -> dict:
        try:
            # step 1: connect login request
            url = f"https://kite.zerodha.com/connect/login?v=3&api_key={self.api_key}"
            r = self._session.get(url, allow_redirects=False)
            if r.status_code != 302:
                raise AuthException(f"Connect login failed: [{r.status_code}]")

            # step 1a: extract the location header
            location = r.headers.get("location")
            if not location:
                raise AuthException(
                    "Location header not found in connect login response"
                )

            # step 1b: extract the sess_id from the location header, using urlparse
            location_query = urlparse(location).query
            sess_id = parse_qs(location_query).get("sess_id", [None])[0]

            # step 2: generate oms session
            oms_session = self._generate_oms_session()

            # step 3: get finish response
            finish_url = f"https://kite.zerodha.com/connect/finish?v=3&api_key={self.api_key}&sess_id={sess_id}"
            r = self._session.get(finish_url, allow_redirects=False)
            if r.status_code != 302:
                raise AuthException(f"Connect finish failed: [{r.status_code}]")

            # step 3a: extract the location header
            location = r.headers.get("location")
            if not location:
                raise AuthException(
                    "Location header not found in connect finish response"
                )

            # step 3b: extract the request_token from the location header
            location_query = urlparse(location).query
            request_token = parse_qs(location_query).get("request_token", [None])[0]

            # step 3c: generate the checksum
            h = hashlib.sha256(
                self.api_key.encode("utf-8")
                + request_token.encode("utf-8")
                + self.api_secret.encode("utf-8")
            )
            checksum = h.hexdigest()

            # step 4: get the access_token
            url = "https://api.kite.trade/session/token"
            data = {
                "api_key": self.api_key,
                "request_token": request_token,
                "checksum": checksum,
            }
            r = self._session.post(url, data=data)
            if r.status_code != 200:
                raise KiteException(r)
            r_json = r.json()
            r_data = r_json.get("data", {})

            # step 4a: add kf_session
            r_data["kf_session"] = oms_session["kf_session"]

            # step 5: return the response data
            return r_data

        except Exception as e:
            raise e




