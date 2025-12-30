"""
mockapp/utils.py

Helper functions for building HTTP responses.
"""
import json


def text_response(body: str):
    """
    Build a plain text HTTP response.
    """
    def responder(env, start_response):
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return [body.encode('utf-8')]
    return responder


def json_response(data):
    """
    Build a JSON HTTP response.
    """
    def responder(env, start_response):
        payload = json.dumps(data).encode('utf-8')
        start_response('200 OK', [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(payload)))
        ])
        return [payload]
    return responder