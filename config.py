import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:@localhost:5432/project_udacity'
SQLALCHEMY_TRACK_MODIFICATIONS = False