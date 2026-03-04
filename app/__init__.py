from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*")

def create_app():
    app = Flask(__name__)
    
    # We need a secret key for Sessions to work (security)
    app.config['SECRET_KEY'] = 'dev-key-change-this-later'

    # Init SocketIO
    socketio.init_app(app)

    # Import and register the routes
    from app.routes import main
    app.register_blueprint(main)

    # Import socket events to ensure they are registered
    from app.engine import multiplayer

    return app