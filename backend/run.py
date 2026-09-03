from app import create_app

app = create_app()

if __name__ == "__main__":
    # In production, use a real WSGI server like gunicorn
    app.run(debug=True, port=5000)
