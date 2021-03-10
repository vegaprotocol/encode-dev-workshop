import websocket
import json
import flask
import threading

market_id = '2839D9B2329C9E70'
party_id = '9d890eb30ad95f3c41d36831cafc93322cb08db21c30fd211984a0807def1093'

market_data_query = '''
    subscription {
        marketData(
            marketId: "''' + market_id + '''"
        ) {
            markPrice
            bestBidPrice
            bestBidVolume
            bestOfferPrice
            bestOfferVolume
            market {
                name
                decimalPlaces
            }
        }
    }
'''

position_data_query = '''
    subscription {
        positions(
            partyId: "''' + party_id + '''",
            marketId: "''' + market_id + '''"
        ) {
            market {
                name
                id
                decimalPlaces
            }
            openVolume
            realisedPNL
            unrealisedPNL
            averageEntryPrice
        }
    }
'''

subscriptions = [
   market_data_query,
   position_data_query
]

id_names = [ 'MARKET_DATA', 'POSITIONS' ]

markets = []
positions = []

def init_subscriptions(ws):
    ws.send(json.dumps({
        'type': 'connection_init'
    }))
    for i in range(0, len(subscriptions)):
        msg = json.dumps({
            'id': str(i),
            'type': 'start',
            'payload': { 'query': subscriptions[i] }
        })
        ws.send(msg)
        print(f'Connected -> {id_names[i]}')

def on_message(ws, message):
    obj = json.loads(message)
    global markets
    global positions
    try:
        id = obj['id']
        data = obj['payload']['data']
        type = id_names[int(id)]
        if type == 'MARKET_DATA':
            markets = [data['marketData']]
        elif type == 'POSITIONS':
            positions = [data['positions']]
    except:
        pass

def on_error(ws, error):
    print(error)

def on_close(ws):
    connect()

def on_open(ws):
    init_subscriptions(ws)

def connect():
    ws = websocket.WebSocketApp('wss://lb.testnet.vega.xyz/query',
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/markets', methods=['GET'])
def markets():
    return flask.jsonify(markets)

@app.route('/positions', methods=['GET'])
def positions():
    return flask.jsonify(positions)

if __name__ == '__main__':
    t1 = threading.Thread(target=connect)
    t1.start()
    app.run()
