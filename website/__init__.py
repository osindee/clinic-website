from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

#create SQLALchemy instance
clinicDB = SQLAlchemy()
login_manager =  LoginManager()

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'SUCKMYMEAT101'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clinic.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

     # Flask-Mail config
    app.config['MAIL_SERVER'] = 'smtp-relay.brevo.com'  
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'a3cb33001@smtp-brevo.com'
    app.config['MAIL_PASSWORD'] = 'xsmtpsib-d1684f03af04f8ecb647b810af35f760d0e791653d46af9389730aa50bf135d4-4mb87RsgjQA1877n'
    app.config['MAIL_DEFAULT_SENDER'] = 'dobbsdarien@gmail.com'
    
    # Configure the database URI
    clinicDB.init_app(app)
    mail.init_app(app)


     # Initialize Flask-Login
    
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    with app.app_context():
        from .models import Admin, SiteContent
        clinicDB.create_all()

        # Context processor for global site_content
        @app.context_processor
        def inject_site_content():
            content = SiteContent.query.all()
            return dict(site_content={item.key: item.value for item in content})



# Define the user_loader function
    from website.models import Admin  # Import User model here
    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))
    

    from .views import views
    from .auth import auth
    app.register_blueprint(views)
    app.register_blueprint(auth)
    
    with app.app_context():
        clinicDB.create_all()

    
    return app