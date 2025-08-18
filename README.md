SOFTWARE-DEFINED NETWORKING ROUTER

This project implements a custom SDN-based router using Mininet and the POX controller.
The topology simulates a small university network with multiple LANs, a data center, and external “internet” hosts.

The router uses OpenFlow to forward packets, enforce firewall rules, and provide basic connectivity between subnets.

PROJECT STRUCTURE

topo.py → Defines the custom Mininet topology (LANs, Data Center, Internet hosts, Core switch).

router.py → Contains the POX/SDN controller logic for packet forwarding and firewall rules.

NETWORK TOPOLOGY

The simulated network consists of:

Student Housing LAN (3 hosts)

Faculty LAN (3 hosts + printer)

IT Department LAN (3 hosts)

University Data Center (Exam, Web, and DNS servers)

Internet Hosts (trusted PCs, guest, and external server)

Core Switch connecting all subnets

   [Student LAN]       [Faculty LAN]        [IT Dept LAN]        [Data Center]
        s3                  s2                  s4                    s5
         \                  /                   /                     /
                          [ Core Switch (s1) ]
                                 |
                     [ Internet Hosts & Server ]

REQUIREMENTS

Mininet (2.3.0 or later)

POX Controller (OpenFlow 1.0 support)

Python 2.7 or 3.x depending on your Mininet/POX version

RUNNING THE PROJECT

Clone this repository:

git clone https://github.com/<your-username>/sdn-router.git
cd sdn-router


Start the POX controller (from the POX directory):

./pox.py log.level --DEBUG forwarding.l2_learning


Replace forwarding.l2_learning with your custom routing module if implemented.

In another terminal, launch the topology:

sudo python topo.py


Use the Mininet CLI to test connectivity:

mininet> pingall

FEATURES

Forwarding between 4 LANs and 3 internet-facing devices.

30+ firewall rules to control inter-subnet communication.

Simulation of real-world ISP troubleshooting: ARP failures, IP conflicts, and routing errors.

LEARNING OUTCOMES

This project demonstrates:

How Software-Defined Networking (SDN) separates control and data planes.

Using Mininet to simulate realistic multi-subnet topologies.

How firewall and forwarding rules impact network connectivity.

Debugging and troubleshooting common network issues in an SDN environment.

AUTHOR

Christian Garces
Computer Engineering @ UC Santa Cruz
