# Long-Polling vs WebSockets vs Server-Sent Events

- All three are popular communication protocols between client and server
- Standard HTTP request:
    1. Client opens a connection and requests data from server
    2. Server calculates response
    3. Server sends response back to the client

## Ajax Polling

- Client repeatedly polls (requests) server for data
- If no data available, empty response is returned
- Procedure:
    1. Client opens connection, requests data via HTTP
    2. Requested webpage sends requests to server at regular intervals
    3. Server calculates response and sends it back
    4. Client repeats above three steps to get updates from server
- Problem is that client has to keep asking, resulting in many empty responses creating overhead

## HTTP Long-Polling

- Server push info to client when data is available
- Client requests info from server as normal polling but with expectation that server may not respond immediately
- Also known as `Hanging GET`
    * If server does not have data available for client, it holds request and waits until data is available
    * Once data is available, a full response is sent to client
    * Client immediately re-request information
- Procedure:
    1. Client makes initial request using regular HTTP
    2. Server delays response until update available
    3. Update available and server sends a full response
    4. Client sends new long-poll request either immediately upon receiving response or after a pause to allow acceptable latency period
    5. Each long-poll request has a timeout; client has to reconnect periodically after connection is closed due to timeouts

## WebSockets

- Provides full duplex communication channels over a single TCP connection
- Persistent connection between a client and a server that both parties can use to send data at any time
- Client establishes websocket connection theough websocket handshake
- If process succeeds, server and client can exchange data in both directions at any time
- Lower overhead, facilitating real-time data transfer from and to the server
- Messages passed back and forth while keeping connection open

## Server-Sent Events (SSEs)

- Client establishes a persistent and long-term connection with the server
- Server uses this connection to send data to client
- If client wants to send data to server, it would need another protocol to do so
- Procedure
    1. Client requests data from server using HTTP
    2. Requested webpage opens connection to server
    3. Server sends data to client when new info is available
- SSEs best when we need real-time traffic from the server to client