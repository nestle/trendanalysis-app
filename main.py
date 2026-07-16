from flask import Flask
import logging
from routes import initialize_routes
from cache import create_cache

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Initialize the cache database
create_cache()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize routes
initialize_routes(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)