from flask import Flask

from shared.infrastructure.clients import MQTTClient, init_mqtt_client

app = Flask(__name__)

first_request = True

@app.before_request
def setup():
    global first_request
    if first_request:
        first_request = False


if __name__ == '__main__':
    init_mqtt_client()
    app.run(debug=True)
