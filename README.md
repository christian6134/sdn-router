SOFTWARE-DEFINED NETWORKING ROUTER

This project implements a custom SDN-based router using Mininet and the POX controller.

The topology simulates a small university network with multiple LANs, a data center, and external “internet” hosts.

The router uses OpenFlow to forward packets, enforce firewall rules, and provide basic connectivity between subnets.


PROJECT STRUCTURE

topo.py → Defines the custom Mininet topology (LANs, Data Center, Internet hosts, Core switch).

router.py → Contains the POX/SDN controller logic for packet forwarding and firewall rules.


LEARNING OUTCOMES

This project demonstrates:

How Software-Defined Networking (SDN) separates control and data planes.

Using Mininet to simulate realistic multi-subnet topologies.

How firewall and forwarding rules impact network connectivity.

Debugging and troubleshooting common network issues in an SDN environment.




AUTHOR

Christian Garces
Computer Engineering @ UC Santa Cruz
