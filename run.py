from app import create_app, socketio
from dotenv import load_dotenv

load_dotenv()
app = create_app()

if __name__ == '__main__':
    # Debug=True allows auto-reload when you change code
    socketio.run(app, debug=True)