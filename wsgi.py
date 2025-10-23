# wsgi.py
from app import create_app  # import your function from app.py
app = create_app()          # call the function to get the Flask app
