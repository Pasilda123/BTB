import time
import uuid
import jwt
import hashlib
import requests
import json
from urllib.parse import urlencode
from config.settings import API_KEY, SECRET_KEY, API_URL, API_URL_V1

class BithumbAPI:
    def __init__(self, api_key=API_KEY, secret_key=SECRET_KEY):
        self.api_key = api_key
        self.secret_key = secret_key
        self.api_url = API_URL
        self.api_url_v1 = API_URL_V1

    def _private_api_call_v1_jwt(self, endpoint):
        payload = {
            'access_key': self.api_key,
            'nonce': str(uuid.uuid4()),
            'timestamp': round(time.time() * 1000)
        }
        jwt_token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.get(f"{self.api_url_v1}{endpoint}", headers=headers)
        return response.json()

    def _private_api_call_v1_jwt_post(self, endpoint, request_body):
        query = urlencode(request_body).encode('utf-8')
        query_hash = hashlib.sha512(query).hexdigest()
        payload = {
            'access_key': self.api_key,
            'nonce': str(uuid.uuid4()),
            'timestamp': round(time.time() * 1000),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512'
        }
        jwt_token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Content-Type': 'application/json'
        }
        response = requests.post(f"{self.api_url_v1}{endpoint}", data=json.dumps(request_body), headers=headers)
        return response.json()

    def get_orderbook(self, order_currency, payment_currency="KRW"):
        url = f"{self.api_url}/public/orderbook/{order_currency}_{payment_currency}"
        response = requests.get(url)
        data = response.json()
        return data['data'] if data.get('status') == '0000' else None

    def place_order(self, order_currency, payment_currency, units, side, type="limit", price_to_send=None):
        endpoint = "/orders"
        market_id = f"{payment_currency.upper()}-{order_currency.upper()}"
        request_body = {
            "market": market_id,
            "side": side,
            "volume": str(units),
            "ord_type": type
        }
        if type == "market" and side == "bid":
            request_body["price"] = "1000000000"
        elif type == "limit" and price_to_send is not None:
            request_body["price"] = str(price_to_send)
        return self._private_api_call_v1_jwt_post(endpoint, request_body)

    def get_balance(self, currency="ALL"):
        endpoint = "/accounts"
        response = self._private_api_call_v1_jwt(endpoint)
        if not response or not isinstance(response, list):
            return None
        if currency == "ALL":
            return {item['currency'].lower(): item['balance'] for item in response}
        else:
            for item in response:
                if item['currency'].upper() == currency.upper():
                    return float(item['balance'])
        return 0.0 