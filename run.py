from app import create_app

app = create_app()

if __name__ == '__main__':
    # Debug=True allows auto-reload when you change code
    app.run(debug=True)