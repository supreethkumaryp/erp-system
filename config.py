# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database - we are working with
# MongoEngine
MONGODB_SETTINGS = {
    'db': 'parasdoors',
    'host': 'mongodb://localhost:27017/parasdoors'
}
# PyMongo
MONGO_DBNAME = 'parasdoors'
MONGO_URI = 'mongodb://localhost:27017/parasdoors'

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = "f7659fd5b7bcae2b5a8c5a69"

# Secret key for signing cookies
SECRET_KEY = "2186b978d6be9bc14cbd7e7e"

# Secret key for JWT_SECRET_KEY
JWT_SECRET_KEY = "3b659554fe8d18a30df0980e"