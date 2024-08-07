from flask import Flask

def create_app():
    app = Flask(__name__, static_folder='static')
    app.secret_key = "we will do it"
    
    # Import and register blueprints
    from .controllers import auths, reading, listening, writing, speaking, chatbot
    
    app.register_blueprint(auths.auths_bp)
    app.register_blueprint(reading.reading_bp, url_prefix='/reading')
    app.register_blueprint(listening.listening_bp, url_prefix='/listening')
    app.register_blueprint(writing.writing_bp, url_prefix='/writing')
    app.register_blueprint(speaking.speaking_bp, url_prefix='/speaking')
    app.register_blueprint(chatbot.chatbot_bp, url_prefix='/chatbot')

    return app
