

class AnonymousSessionMiddleware(object):
    def process_request(self, request):
        if not request.session.session_key:
            request.session.save()
