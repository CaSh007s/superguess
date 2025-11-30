from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # We need a secret key for Sessions to work (security)
    app.config['SECRET_KEY'] = 'dev-key-change-this-later'

    # Import and register the routes
    from app.routes import main
    app.register_blueprint(main)

    return app