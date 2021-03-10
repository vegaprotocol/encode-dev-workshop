import requests
import time
import random

market_id = '2839D9B2329C9E70'
party_id = '9d890eb30ad95f3c41d36831cafc93322cb08db21c30fd211984a0807def1093'

wallet_name = "mykey"
wallet_passphrase = "password123"
wallet_server_url = "http://localhost:1789"
node_url_rest = "https://lb.testnet.vega.xyz"

def get_token():
    req = {"wallet": wallet_name, "passphrase": wallet_passphrase}
    response = requests.post(f"{wallet_server_url}/api/v1/auth/token", json=req)
    return response.json()["token"]

def prepare_order(size, side):
    req = {
        "submission": {
            "marketId": market_id,
            "partyId": party_id,
            "size": str(size),
            "side": side,
            "timeInForce": "TIME_IN_FORCE_IOC",
            "type": "TYPE_MARKET",
        }
    }
    url = f"{node_url_rest}/orders/prepare/submit"
    response = requests.post(url, json=req)
    return response.json()

def sign_and_send(prepared_order, token):
    auth_header = f'Authorization: Bearer {token}'
    blob = prepared_order["blob"]
    req = {"tx": blob, "pubKey": party_id, "propagate": True}
    url = f"{wallet_server_url}/api/v1/messages"
    response = requests.post(url, headers={
        'Authorization': auth_header
    }, json=req)
    return response

def trade():
    side = "SIDE_BUY" if random.uniform(0, 1) > 0.5 else "SIDE_SELL"
    size = int(random.uniform(1, 5))
    token = get_token()
    prepared_order = prepare_order(size, side)
    response = sign_and_send(prepared_order, token)
    if response.status_code == 200:
        print(f"Executed market order: size = {size}; side = {side}")
    else:
        print(response.json())

if __name__ == '__main__':
    while True:
        trade()
        time.sleep(1)
