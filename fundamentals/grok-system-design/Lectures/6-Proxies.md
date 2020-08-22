# Proxies

- Proxy server is an intermediate server between client and backend server
- Clients connect to proxy to make a request for a service e.g., web page, file, connection, etc
- Proxy is a software or hardware that acts as an intermediary for client requests seeking resources from other servers
- Proxies used to:
    * Filter requests
    * Log requests
    * Transform requests e.g., adding/removing headers, encrypting/decrypting, compressing a resource
- Proxy server can also cache requests so requests can be handled without going to remote server

## Proxy Server Types

- Proxies can reside on client's local server or anywhere between client and remote servers
- Popular proxy servers:
    1. Open proxy
        * Proxy server accessible by any internet user
        * Any user on the internet is able to use this forwarding device
        * Two famous types of open proxies:
            + Anonymous proxy: proxy reveals its identity as a server but does not disclose the initial IP address
                - Hides users IP address
            + Transparent proxy: proxy identifies itself and with the support of HTTP headers, the first IP address can be viewed
                - Main benefit is being able to cache websites
    2. Reverse proxy
        * Retrieves resources on behalf of a client from one or more servers
        * Resources are then returned to the client appearing as if they originated from the proxy itself