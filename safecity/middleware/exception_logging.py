import logging
#import traceback

class ExceptionLoggingMiddleware(object):
    def process_exception(self, request, exception):
        #tb_text = traceback.format_exc()
        #url = request.build_absolute_uri()
        log = logging.getLogger("safecity.middleware.logging")
        log.exception('Caught exception')
