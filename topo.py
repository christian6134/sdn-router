#!/usr/bin/python
"""
Custom Mininet Topology for SDN Router Project
Author: Christian Garces

This script defines a university network topology with multiple LANs
(Student Housing, Faculty, IT Department, Data Center) connected through 
a core switch. Internet hosts are also attached to simulate external access.

The topology is controlled by a remote POX controller.
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import RemoteController


class UniversityTopology(Topo):
    def __init__(self):
        # Initialize parent class
        Topo.__init__(self)

        # ----------------------------
        # Define Hosts by Subnet
        # ----------------------------

        # Student Housing LAN
        studentPC1 = self.addHost('studentPC1', ip='169.233.4.1/24')
        studentPC2 = self.addHost('studentPC2', ip='169.233.4.2/24')
        labWS      = self.addHost('labWS', ip='169.233.4.100/24')

        # Faculty LAN
        facultyWS  = self.addHost('facultyWS', ip='169.233.3.10/24')
        printer    = self.addHost('printer', ip='169.233.3.20/24')
        facultyPC  = self.addHost('facultyPC', ip='169.233.3.30/24')

        # IT Department LAN
        itWS       = self.addHost('itWS', ip='169.233.1.10/24')
        itPC       = self.addHost('itPC', ip='169.233.1.20/24')
        itBackup   = self.addHost('itBackup', ip='169.233.1.30/24')

        # University Data Center
        examServer = self.addHost('examServer', ip='169.233.2.1/24')
        webServer  = self.addHost('webServer', ip='169.233.2.2/24')
        dnsServer  = self.addHost('dnsServer', ip='169.233.2.3/24')

        # Internet Hosts (external simulation)
        trustedPC1 = self.addHost('trustedPC1', ip='212.26.59.102/32')
        trustedPC2 = self.addHost('trustedPC2', ip='10.100.198.6/32')
        guest      = self.addHost('guest', ip='10.100.198.10/32')
        dServer    = self.addHost('dServer', ip='200.10.10.200/32')

        # ----------------------------
        # Define Switches
        # ----------------------------
        coreSwitch       = self.addSwitch('s1')  # Core backbone switch
        facultySwitch    = self.addSwitch('s2')
        studentSwitch    = self.addSwitch('s3')
        itSwitch         = self.addSwitch('s4')
        dataCenterSwitch = self.addSwitch('s5')

        # ----------------------------
        # Connect Hosts to Switches
        # ----------------------------

        # Faculty LAN
        self.addLink(facultyWS, facultySwitch)
        self.addLink(printer, facultySwitch)
        self.addLink(facultyPC, facultySwitch)

        # Student Housing LAN
        self.addLink(studentPC1, studentSwitch)
        self.addLink(studentPC2, studentSwitch)
        self.addLink(labWS, studentSwitch)

        # IT Department LAN
        self.addLink(itWS, itSwitch)
        self.addLink(itPC, itSwitch)
        self.addLink(itBackup, itSwitch)

        # Data Center
        self.addLink(examServer, dataCenterSwitch)
        self.addLink(webServer, dataCenterSwitch)
        self.addLink(dnsServer, dataCenterSwitch)

        # ----------------------------
        # Inter-Switch Links
        # ----------------------------
        self.addLink(facultySwitch, coreSwitch)
        self.addLink(studentSwitch, coreSwitch)
        self.addLink(itSwitch, coreSwitch)
        self.addLink(dataCenterSwitch, coreSwitch)

        # Internet connections → Core
        self.addLink(trustedPC1, coreSwitch)
        self.addLink(trustedPC2, coreSwitch)
        self.addLink(guest, coreSwitch)
        self.addLink(dServer, coreSwitch)


# ----------------------------
# Run the Topology
# ----------------------------
if __name__ == '__main__':
    topo = UniversityTopology()
    controller = RemoteController(name='c0', ip='127.0.0.1', port=6633)

    # Load network with topology + controller
    net = Mininet(topo=topo, controller=controller)
    net.start()

    print("\nNetwork is up. Use the Mininet CLI to test connectivity.\n")
    CLI(net)

    net.stop()

