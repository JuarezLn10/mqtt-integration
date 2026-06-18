import atexit
import logging
import os
import signal
import threading

from flask import Flask

from shared.infrastructure.clients import init_mqtt_client, shutdown_mqtt_client

# Create the Flask application.
app = Flask(__name__)

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
    logging.info(f"Received signal {signum}, shutting down server...")
    shutdown_app()


# Register the shutdown function to be called when the program exits.
atexit.register(shutdown_app)

# Register the signal handler for SIGINT and SIGTERM.
signal.signal(signal.SIGINT, signal_handler)  # Closing process in the terminal
signal.signal(signal.SIGTERM, signal_handler)  # Closing process in Docker


def setup():
    pass


if __name__ == '__main__':
    """ Runs the application. """
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        # Only runs a connection once when the main process starts, not on each reload.
        init_mqtt_client()
    logging.info(app.url_map)
    setup()
    app.run(debug=True)
