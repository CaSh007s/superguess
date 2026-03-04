import os
from flask import Flask
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

socketio = SocketIO(cors_allowed_origins="*")
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

def create_app():
    app = Flask(__name__)
    
    # We need a secret key for Sessions to work (security)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-this-later')

    # Allow passing Redis from Render securely
    redis_url = os.environ.get("REDIS_URL", "")
    
    if redis_url:
        # Scale to multiple workers
        socketio.init_app(app, message_queue=redis_url)
        # Scale rate-limiter
        limiter.init_app(app, storage_uri=redis_url)
    else:
        # Standard local memory
        socketio.init_app(app)
        limiter.init_app(app)

    # Import and register the routes
    from app.routes import main
    app.register_blueprint(main)

    # Import socket events to ensure they are registered
    from app.engine import multiplayer

    return app