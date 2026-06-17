### Q: How do you isolate a Kubernetes namespace using NetworkPolicies?
NetworkPolicies act as firewalls for pods within a namespace. To isolate a namespace completely, you apply a default-deny policy that rejects all incoming and outgoing traffic. Then, you explicitly define allow rules for specific pods, ports, or external CIDR blocks using ingress and egress selectors.

### Q: What is the main difference between Docker Compose and Docker Swarm?
Docker Compose is a tool for defining and running multi-container applications on a single host. Docker Swarm, however, is a native orchestration engine that turns a group of Linux hosts into a single, virtual Docker engine, providing high availability, service discovery, load balancing, and scaling across multiple nodes.

### Q: How do you fix a read-only lock error on a Micron NVMe SSD drive?
A read-only lock typically indicates that the SSD drive controller has encountered a critical hardware fault or reached its write endurance limit, locking the drive to protect data integrity. To diagnose and potentially clear the lock, you must use vendor-specific CLI utilities (like Micron Storage Executive), perform a firmware update, or execute an authorized crypto-erase command if hardware health allows.
