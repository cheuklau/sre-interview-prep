# File Transfer

## Functional Requirements

- Distribute file from a local computer to a fleet of servers
- Consider:
    - Small files
    - Large files
    - Same local network
    - Globally distributed network

## Methods

### scp

- Secure copy command
- `scp /path/to/local/file user@host:/path/to/remote/dir`
- `scp user@server1:/path/to/remote/file user@server2:/path/to/remote/file`
- Uses SSH so communication is encrypted

### rsync

- `rsync /path/to/local/file user@host:/path/to/remote/file`
- Use `-rsh=ssh` to use SSH encryption; otherwise unencrypted
- In general `rsync` faster than `scp` as it uses optimization e.g., delta algorithm

### Central WebServer

- Host file on a central webserver e.g., S3 and run a `wget` command on each server
- Amount of machines that can perform concurrently would depend on bandwidth and max connections allowed by webserver
- Most liklely will not reach S3 limit

## Case 1) Small file, few servers

- `scp` might be sufficient since file is small
    * Provides encryption via ssh and simple
- `rsync` would also work but since file is small, optimization with delta algorithm less obvious
- Central webserver will be overkill for only a few servers

## Case 2) Large file, few servers

- `rsync` would work best since file is large so delta algorithm shines
    * Can run with `ssh` option to enable ssh encryption
- Central webserver will be overkill for only a few servers

## Case 3) Small or large file, many servers

- Central webserver should be the best for this scenario
- Each server will connect with the webserver e.g., `wget` to download the file
- This requires the webserver to handle all of the necessary oncurrent connections and handle the resulting bandwidth
- Alternatively, we could use a configuration management software e.g., Ansible to have only a subset of servers download at a time to meet webserver resource limits
- If we don't have a central webserver, we could try using `rsync` to distribute file to `k` servers and then those `k` servers distribute to `k` additional servers and so on until all servers have been updated.
    + This allows us to parallelize file transfer.

## Case 4) Small or large file, many servers different geographical locations

- Same as Case 3 but perhaps try using a hosted solution e.g., S3 that has geographic content distribution networks at locations where servers are hosted in order to minimize latency