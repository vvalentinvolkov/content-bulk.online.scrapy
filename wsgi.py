from src.flask_app import app as application

app = application.app

if __name__ == '__main__':
    app.run(debug=True)
