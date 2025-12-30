"""
mockapp/router.py

Simple URL router mapping to WSGI callables.
"""

class Router:
    def __init__(self):
        self.routes = {}

    def add_route(self, method: str, path: str, view_func):
        """
        Register a view function for method & path.
        """
        self.routes[(method.upper(), path)] = view_func

    def wsgi_app(self, env, start_response):
        """
        WSGI entry point.
        """
        key = (env['REQUEST_METHOD'], env['PATH_INFO'])
        view = self.routes.get(key)
        if not view:
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [b'Not Found']
        return view(env, start_response)

    def __call__(self, env, start_response):
        return self.wsgi_app(env, start_response)