#imports
from website import create_app, clinicDB
from flask import render_template, views, Blueprint
from website.models import Admin, SiteContent
from werkzeug.security import generate_password_hash

#my App
app = create_app()


import os
if __name__ == "__main__":
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
    
    