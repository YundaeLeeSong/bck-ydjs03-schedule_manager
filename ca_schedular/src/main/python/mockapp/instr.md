# Project: mockapp

A guide to structuring and packaging a simple Python HTTP server application from scratch, following community best practices for modular design and in-code documentation.

```
mockapp/                     # Project root
├── setup.py                  # Installation script
├── run.py                    # Entry point for development
├── config.py                 # Configuration definitions
├── mockapp/                  # Application package
│   ├── __init__.py           # App factory and package-level imports
│   ├── server.py             # HTTP server implementation (WSGI compliant)
│   ├── router.py             # URL routing logic
│   └── utils.py              # Helper functions
└── tests/                    # Test suite
    └── test_app.py
```

---

## 1. `setup.py`
```python
from setuptools import setup, find_packages

setup(
    name='mockapp',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],  # No external dependencies
    entry_points={
        'console_scripts': [
            'mockapp = run:main'
        ],
    },
)
```

- **Purpose**: Defines the package, enables `mockapp` CLI for development.

---

## 2. `config.py`
```python
"""
config.py

Application configuration values.
"""

class BaseConfig:
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = True

config = BaseConfig
```

- Keeps host, port, and debug flags centralized.

---

## 3. `mockapp/__init__.py`
```python
"""
mockapp/__init__.py

Creates and configures the WSGI application.
"""
from .router import Router
from .utils import json_response, text_response


def create_app():
    """
    Application factory.

    Returns:
        WSGI callable implementing the application.
    """
    router = Router()

    # Register routes
    router.add_route('GET', '/', lambda env, start: text_response('Hello, MockApp!'))
    router.add_route('POST', '/api/data', lambda env, start: json_response({'received': env['json']}))

    return router.wsgi_app
```

- Uses a simple `Router` to dispatch requests.

---

## 4. `mockapp/server.py`
```python
"""
mockapp/server.py

Implements a basic WSGI server using Python's built-in modules.
"""
import socket
from io import BytesIO


def run_simple(app, host='0.0.0.0', port=5000):
    """
    Run a simple HTTP server serving the given WSGI app.

    Args:
        app: WSGI application callable.
        host: Listening address.
        port: Listening port.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(1)
        print(f"* Running on http://{host}:{port}/")

        while True:
            client, _ = sock.accept()
            data = client.recv(1024).decode('utf-8')
            if not data:
                client.close()
                continue

            # Parse request line
            request_line, *rest = data.splitlines()
            method, path, _ = request_line.split()

            # Build WSGI environment
            env = {'REQUEST_METHOD': method, 'PATH_INFO': path}
            # Simple JSON body parsing
            if 'Content-Length:' in data:
                body = data.split('\r\n\r\n')[1]
                import json
                env['json'] = json.loads(body)

            # Capture response
            response_body = []
            def start_response(status, headers):
                nonlocal response_status, response_headers
                response_status = status
                response_headers = headers

            result = app(env, start_response)

            # Construct HTTP response
            response = f"HTTP/1.1 {response_status}\r\n"
            for name, value in response_headers:
                response += f"{name}: {value}\r\n"
            response += '\r\n'
            client.sendall(response.encode('utf-8'))
            for chunk in result:
                client.sendall(chunk)
            client.close()
```

---

## 5. `mockapp/router.py`
```python
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
```

---

## 6. `mockapp/utils.py`
```python
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
```

---

## 7. `run.py`
```python
"""
run.py

Entry point to start the server without external frameworks.
"""
from config import config
from mockapp import create_app
from mockapp.server import run_simple


def main():
    app = create_app()
    run_simple(app, host=config.HOST, port=config.PORT)


if __name__ == '__main__':
    main()
```

---

## 8. `tests/test_app.py`
```python
"""
test_app.py

Unit tests for routing logic and utility functions.
"""
import pytest
from mockapp import create_app
from mockapp.router import Router
from mockapp.utils import text_response, json_response


def test_router_not_found():
    router = Router()
    def dummy_start(status, headers): pass
    response = router.wsgi_app({'REQUEST_METHOD':'GET','PATH_INFO':'/'}, dummy_start)
    assert response == [b'Not Found']


def test_text_response():
    responder = text_response('hello')
    status, headers = '', []
    def start(s, h):
        nonlocal status, headers
        status, headers = s, h
    result = responder({}, start)
    assert status.startswith('200')
    assert b'hello' in result[0]


def test_json_response():
    data = {'a':1}
    responder = json_response(data)
    status, headers = '', []
    def start(s, h):
        nonlocal status, headers
        status, headers = s, h
    result = responder({}, start)
    assert status.startswith('200')
    assert b'"a": 1' in result[0]
```

---

### Workflow & Commands

1. **Install**: `pip install -e .`
2. **Run**: `mockapp`
3. **Test**: `pytest`

This bare-bones server replicates the Flask example’s design pattern—app factory, routing, utilities—without external dependencies, perfect for learning from scratch.
