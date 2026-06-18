import atexit
import logging
import os
import signal
import threading

from flask import Flask

from shared.infrastructure.clients import init_mqtt_client, shutdown_mqtt_client

app = Flask(__name__)

_shutdown_lock = threading.Lock()
_shutdown_done = False

def shutdown_app():
    global _shutdown_done

    with _shutdown_lock:
        if _shutdown_done:
            return

        _shutdown_done = True

        try:
            shutdown_mqtt_client()
        except Exception as e:
            logging.exception(f"Error during shutdown: {e}")


def signal_handler(signum, frame):
    logging.info(f"Received signal {signum}, shutting down server...")
    shutdown_app()

atexit.register(shutdown_app)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def setup():
    pass

if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        # Only runs a connection once when the main process starts, not on each reload.
        init_mqtt_client()
    logging.info(app.url_map)
    setup()
    app.run(debug=True)
