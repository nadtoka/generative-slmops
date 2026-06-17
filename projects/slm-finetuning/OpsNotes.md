### Q: How do you resolve packet drop and connection timeouts on a Docker Swarm overlay network behind an AWS ALB?
When containers in a Docker Swarm overlay network experience intermittent connection timeouts behind an AWS Application Load Balancer, it is typically caused by an MTU size mismatch due to VXLAN encapsulation overhead. To resolve this, you must explicitly configure the custom overlay network with a reduced MTU by passing `--opt mtu=1450` during the `docker network create` execution, preventing packet fragmentation and traffic drops.

### Q: How do you recover a Proxmox VE node from a lost quorum state after a network partition?
When a Proxmox cluster node loses quorum due to network isolation, it switches to read-only mode, disabling VM and container management. To temporarily force quorum locally and restore read-write operations for emergency maintenance, execute `pvecm expected 1` via SSH on the isolated node. This overrides the required cluster vote count down to 1, allowing you to manage local guests until the underlying network partition is resolved.

### Q: How do you clear Cloudflare cache automatically in a GitHub Actions deployment workflow?
To automate Cloudflare cache purging during CI/CD, use the official `cloudflare/wrangler-action` or execute a direct `curl` HTTP POST request to the Cloudflare API v4 endpoint. You must pass the `CLOUDFLARE_ZONE_ID` in the URL and authenticate by providing your `CLOUDFLARE_API_TOKEN` as a Bearer token in the request headers, specifying `purge_everything: true` in the JSON payload.

### Q: How do you isolate a Kubernetes namespace using NetworkPolicies?
NetworkPolicies act as firewalls for pods within a namespace. To isolate a namespace completely, you apply a default-deny policy that rejects all incoming and outgoing traffic. Then, you explicitly define allow rules for specific pods, ports, or external CIDR blocks using ingress and egress selectors.

### Q: What is the main difference between Docker Compose and Docker Swarm?
Docker Compose is a tool for defining and running multi-container applications on a single host. Docker Swarm, however, is a native orchestration engine that turns a group of Linux hosts into a single, virtual Docker engine, providing high availability, service discovery, load balancing, and scaling across multiple nodes.

### Q: How do you fix a read-only lock error on a Micron NVMe SSD drive?
A read-only lock typically indicates that the SSD drive controller has encountered a critical hardware fault or reached its write endurance limit, locking the drive to protect data integrity. To diagnose and potentially clear the lock, you must use vendor-specific CLI utilities (like Micron Storage Executive), perform a firmware update, or execute an authorized crypto-erase command if hardware health allows.
