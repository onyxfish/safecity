from safecity.configs.common.settings import *

# Debugging
DEBUG = False
TEMPLATE_DEBUG = DEBUG

# Database
DATABASE_HOST = 'safecitychicago.org'
DATABASE_PORT = '5433'
DATABASE_USER = 'safecity'
DATABASE_PASSWORD = 'W34QXl0AER'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://media.safecitychicago.org/'

# Predefined domain
MY_SITE_DOMAIN = 'safecitychicago.org'

# Email
# EMAIL_HOST = 'mail.tribapps.com'
# EMAIL_PORT = 25

# Caching
CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

# S3
AWS_S3_URL = 's3://media.safecitychicago.org/'

# logging
import logging.config
LOG_FILENAME = os.path.join(os.path.dirname(__file__), 'logging.conf')
logging.config.fileConfig(LOG_FILENAME)