from app import create_app

app = create_app()

if __name__ == "__main__":
    from app import db
    with app.app_context():
        db.create_all()
    # '0.0.0.0' tells Flask to be visible on your local network
    # Port 5000 is the default. Other devices can visit http://YOUR_IP:5000
    app.run(host='0.0.0.0', port=5000, debug=True)
