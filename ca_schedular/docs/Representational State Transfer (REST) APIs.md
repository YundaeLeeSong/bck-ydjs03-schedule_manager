# Representational State Transfer (REST) APIs

## Historical Context  
In the late 1990s and early 2000s, most web services relied on protocols like SOAP, which required verbose XML envelopes and strict message formats[^1][^2]. In 2000, Roy Fielding introduced REST in his doctoral dissertation as an architectural style for distributed hypermedia systems[^3][^4]. His goal was to create a *standard* way for servers to communicate over the Web, focusing on simple web concepts (URIs, HTTP methods, and representations) rather than complex messaging rules[^1][^3]. REST quickly gained popularity: companies like eBay and Amazon launched RESTful APIs in the early 2000s to expose resources easily to any client[^5][^1]. Today, REST is the backbone of most web and mobile applications, prized for its simplicity and alignment with HTTP.

## Core Principles of REST  
REST is defined by six architectural constraints (the last one optional)[^4]:

- **Uniform Interface:** Clients and servers communicate through a standardized interface (URIs for resources, HTTP verbs for actions)[^6][^7].
- **Statelessness:** Each request contains all the information needed to process it, so the server does not store any client session state between requests[^7][^8].
- **Client-Server Separation:** The client (e.g. user interface) and server (data storage and logic) have clear, independent roles[^9][^3].
- **Cacheable:** Responses must explicitly indicate whether they are cacheable, enabling clients or intermediaries to reuse them and reduce load[^9][^10].
- **Layered System:** The API architecture can have multiple layers (e.g. load balancer, cache, application, database), with each layer unaware of others beyond the next step[^11][^9].
- **Code on Demand (optional):** Servers may extend client functionality by sending executable code (typically scripts) that the client can run locally[^12][^9].

Each of these constraints simplifies design and improves scalability and flexibility. They are typically applied together to create a truly RESTful API[^4].

### Uniform Interface  
The **Uniform Interface** constraint standardizes how clients interact with resources. Every resource (e.g. a user, order, or image) is identified by a URI, and HTTP methods (GET, POST, PUT, DELETE, etc.) have agreed-upon meanings[^6][^7]. For example, a GET request to `/users/123` retrieves user data, and a DELETE to `/posts/456` removes a post. By using a consistent interface, clients can predict how to use the API and reuse generic tools. HTTP responses typically include a status code and a body with the representation (often JSON) of the resource.

```http
GET /users/123 HTTP/1.1
Host: api.example.com

HTTP/1.1 200 OK
Content-Type: application/json

{"id": 123, "name": "Alice", "email": "alice@example.com"}
