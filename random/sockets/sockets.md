## Viewing Socket State

- Run `netstat -an`
```
Active Internet connections (including servers)
Proto Recv-Q Send-Q  Local Address          Foreign Address        (state)
tcp4       0      0  127.0.0.1.65432        *.*                    LISTEN
```
- Run `lsof -i -n` to view list of open files where `i` indicates internet sockets
```
COMMAND     PID   USER   FD   TYPE   DEVICE SIZE/OFF NODE NAME
Python    67982 nathan    3u  IPv4 0xecf272      0t0  TCP *:65432 (LISTEN)
```

## Handling Multiple Connections

- Use asynchronous I/O `asyncio` library in Python
- Traditional choice was to use threads
- System call `select()` checks for I/O completion on more than one socket
- Call `select()` to osee which sockets are ready for reading and/or writing
- Use `selectors` module to allow high level and efficient I/O multi-plexing
- `asyncio` uses single-threaded multitasking and event loop to manage tasks