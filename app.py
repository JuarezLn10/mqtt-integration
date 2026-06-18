import atexit
import logging
import signal
import threading

from flask import Flask

from shared.infrastructure.clients import init_mqtt_client, shutdown_mqtt_client
from shared.infrastructure.database import init_db

# Create the Flask application.
app = Flask(__name__)

# Configure logging.
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

# Lock to ensure that shutdown is only called once.
_shutdown_lock = threading.Lock()
_shutdown_done = False


def shutdown_app():
    """ Shuts down the application. """
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
    """ Handles SIGINT and SIGTERM signals to gracefully shut down the application. """
    app.logger.info(f"Received signal {signum}, shutting down server...")
    shutdown_app()

first_request = True

@app.before_request
def setup():
    """ Initializes the MQTT client and the database before handling any requests. """

    global first_request

    if first_request:
        first_request = False
        init_mqtt_client()
        app.logger.info("MQTT Client Initialized")
        init_db()
        app.logger.info("Database Initialized")

# Register the shutdown function to be called when the program exits.
atexit.register(shutdown_app)

# Register the signal handler for SIGINT and SIGTERM.
signal.signal(signal.SIGINT, signal_handler)  # Closing process in the terminal
signal.signal(signal.SIGTERM, signal_handler)  # Closing process in Docker


if __name__ == '__main__':
    """ Runs the application. """
    app.logger.info(app.url_map)
    app.run(host = "0.0.0.0", port = 5000, debug = True)
