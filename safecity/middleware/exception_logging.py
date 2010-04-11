import logging

class ExceptionLoggingMiddleware(object):
    """
    Logs exceptions that occur in views with standard Python logging.
    """
    def process_exception(self, request, exception):
        url = request.build_absolute_uri()
        log = logging.getLogger("safecity.middleware.logging")
        log.exception('Caught exception in request for "%s"' % url)

        # Continue with standard Django error-handling
        return None