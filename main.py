"""Application entry point."""

import os
from App.routes import create_app
from App.config import DEBUG

app = create_app()

if __name__ == "__main__":
    app.run(debug=DEBUG)
