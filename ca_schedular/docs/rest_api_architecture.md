# Representational State Transfer (REST) APIs

## Historical Context  
In the late 1990s and early 2000s, most web services relied on protocols like SOAP, which required verbose XML envelopes and strict message formats. In 2000, Roy Fielding introduced REST in his doctoral dissertation as an architectural style for distributed hypermedia systems. His goal was to create a *standard* way for servers to communicate over the Web, focusing on simple web concepts (URIs, HTTP methods, and representations) rather than complex messaging rules. REST quickly gained popularity: companies like eBay and Amazon launched RESTful APIs in the early 2000s to expose resources easily to any client. Today, REST is the backbone of most web and mobile applications, prized for its simplicity and alignment with HTTP.

## Core Principles of REST  
REST is defined by six architectural constraints (the last one optional):

- **Uniform Interface:** Clients and servers communicate through a standardized interface (URIs for resources, HTTP verbs for actions).
- **Statelessness:** Each request contains all the information needed to process it, so the server does not store any client session state between requests.
- **Client-Server Separation:** The client (e.g. user interface) and server (data storage and logic) have clear, independent roles.
- **Cacheable:** Responses must explicitly indicate whether they are cacheable, enabling clients or intermediaries to reuse them and reduce load.
- **Layered System:** The API architecture can have multiple layers (e.g. load balancer, cache, application, database), with each layer unaware of others beyond the next step.
- **Code on Demand (optional):** Servers may extend client functionality by sending executable code (typically scripts) that the client can run locally.

### Uniform Interface  
The **Uniform Interface** constraint standardizes how clients interact with resources. Every resource (e.g. a user, order, or image) is identified by a URI, and HTTP methods (GET, POST, PUT, DELETE, etc.) have agreed-upon meanings. For example, a GET request to `/users/123` retrieves user data, and a DELETE to `/posts/456` removes a post.

```http
GET /users/123 HTTP/1.1
Host: api.example.com

HTTP/1.1 200 OK
Content-Type: application/json

{"id": 123, "name": "Alice", "email": "alice@example.com"}
```

### Statelessness  
Under **Statelessness**, each request from the client must contain all information necessary for the server to understand and fulfill it. The server does not store any session state between requests.

```http
GET /profile HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGci...

HTTP/1.1 200 OK
Content-Type: application/json

{"id": 1, "name": "Alice", "role": "admin"}
```

### Client-Server Separation  
The **Client-Server** constraint enforces a clear separation of concerns: the client handles the user interface and user experience, while the server handles data storage, business logic, and security. This allows each side to evolve independently as long as they adhere to the shared interface.

### Cacheable  
REST APIs must explicitly define whether responses are **cacheable**. If a response is cacheable, clients (or proxies) can store and reuse it. This is done using HTTP headers such as `Cache-Control`.

```http
GET /items HTTP/1.1
Host: api.example.com

HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: max-age=3600

[
  {"id":1,"name":"Item1"},
  {"id":2,"name":"Item2"}
]
```

### Layered System  
A **Layered System** allows an API to be composed of hierarchical layers, with each layer only interacting with the adjacent ones. For example, a REST API might have a gateway, an application server, and a database. Clients can't tell if they're communicating with the end server or an intermediate cache.

- **Example layers:**  
  - API gateway  
  - Business logic server  
  - Database layer  

### Code on Demand (Optional)  
**Code on Demand** allows servers to send executable code to clients. For example, the server can return JavaScript that the browser executes.

```html
<script src="/scripts/chart.js"></script>
```

## REST vs GraphQL vs SOAP

### Architecture  
- **REST**: Resource-based. Uses URIs and HTTP methods to access resources.  
- **GraphQL**: Schema-based query language using a single endpoint.  
- **SOAP**: Protocol specification using XML envelopes and WSDL contracts.

### Flexibility  
- **REST**: Flexible and loosely coupled, but conventions vary.  
- **GraphQL**: Extremely flexible. Clients define what data they want.  
- **SOAP**: Very rigid. Messages follow strict schema definitions.

### Performance  
- **REST**: Simple and supports caching. Can suffer from over-fetching.  
- **GraphQL**: Reduces over-fetching, ideal for mobile. Needs custom caching.  
- **SOAP**: Verbose XML slows parsing. Heavy but predictable.