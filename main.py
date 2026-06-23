"""Application entry point.

Uses Flask's built-in development server when FLASK_DEBUG=1,
or Waitress production WSGI server otherwise.
"""

import os

from App.routes import create_app
from App.config import DEBUG

app = create_app()

if __name__ == "__main__":
    if DEBUG:
        app.run(debug=True)
    else:
        from waitress import serve

        host = os.getenv("FLASK_HOST", "0.0.0.0")
        port = int(os.getenv("FLASK_PORT", "5000"))
        serve(app, host=host, port=port)
