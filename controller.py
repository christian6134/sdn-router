#!/usr/bin/python
"""
Custom Routing Logic for SDN Router Project
Author: Christian Garces

This POX controller script implements static forwarding and firewall rules
for a simulated university network. The network consists of multiple LANs
(Faculty, Student Housing, IT Department, Data Center) connected via a 
core switch, plus several external Internet hosts.

Key Features:
- Floods ARP packets to ensure address resolution.
- Installs flow table entries for ICMP, TCP, and UDP traffic.
- Applies firewall-like policies (e.g., restricting exam server access, 
  limiting printer access, subnet-specific restrictions).
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of

log = core.getLogger()


class Routing(object):
    def __init__(self, connection):
        # Save switch connection so we can send flow mods
        self.connection = connection
        # Listen for PacketIn events from this switch
        connection.addListeners(self)

    def do_routing(self, packet, packet_in, port_on_switch, switch_id):
        """
        Core routing logic for handling packets.
        """

        # ------------------------------
        # Helper Actions
        # ------------------------------
        def flood_arp():
            """Flood ARP packets to all ports (like a hub)."""
            msg = of.ofp_packet_out()
            msg.data = packet_in
            msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
            self.connection.send(msg)
            print("ARP Packet Flooded")

        def accept(output_port):
            """Install forwarding rule for this flow."""
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(packet)
            msg.data = packet_in
            msg.idle_timeout = 60
            msg.hard_timeout = 300
            msg.buffer_id = packet_in.buffer_id
            msg.actions.append(of.ofp_action_output(port=output_port))
            self.connection.send(msg)
            print(f"Packet Accepted -> Port {output_port}")

        def drop():
            """Drop the packet and install a drop rule in the switch."""
            msg = of.ofp_flow_mod()
            msg.buffer_id = packet_in.buffer_id
            msg.in_port = packet_in.in_port
            self.connection.send(msg)
            print("Packet Dropped")

        # ------------------------------
        # Protocol Detection
        # ------------------------------
        is_arp = packet.find('arp') is not None
        is_icmp = packet.find('icmp') is not None
        is_tcp = packet.find('tcp') is not None
        is_udp = packet.find('udp') is not None

        if is_arp:  # ARP packets are flooded
            flood_arp()
            return

        ipv4 = packet.find('ipv4')
        if ipv4 is not None:
            src_ip = str(ipv4.srcip)
            dst_ip = str(ipv4.dstip)
        else:
            src_ip, dst_ip = None, None

        # ------------------------------
        # Subnet Mapping
        # ------------------------------
        def sub_net(ipaddr):
            """Return subnet string for given IP (or exact IP if /32)."""
            subnet_32 = ['212.26.59.102', '10.100.198.6',
                         '10.100.198.10', '200.10.10.200']
            if ipaddr in subnet_32:
                return ipaddr
            quarters = ipaddr.split('.')
            if len(quarters) == 4:
                return f"{'.'.join(quarters[0:3])}.0"
            return None

        dst_subnet, src_subnet = sub_net(dst_ip), sub_net(src_ip)

        # University subnets
        STUDENT_SUBNET = '169.233.4.0'
        FACULTY_SUBNET = '169.233.3.0'
        UDC_SUBNET = '169.233.2.0'
        IT_SUBNET = '169.233.1.0'
        PC1_SUBNET = '212.26.59.102'
        PC2_SUBNET = '10.100.198.6'
        GUEST_SUBNET = '10.100.198.10'
        DISCORD_SUBNET = '200.10.10.200'

        def is_same_subnet(dst, src):
            return dst == src

        # ------------------------------
        # Switch-Based Forwarding Logic
        # ------------------------------
        output_port = None

        if switch_id == 1:  # Core Switch
            # Forward based on subnet mapping
            if dst_subnet == FACULTY_SUBNET:
                output_port = 2
            elif dst_subnet == STUDENT_SUBNET:
                output_port = 3
            elif dst_subnet == IT_SUBNET:
                output_port = 4
            elif dst_subnet == UDC_SUBNET:
                output_port = 5
            elif dst_subnet == PC1_SUBNET:
                output_port = 6
            elif dst_subnet == PC2_SUBNET:
                output_port = 7
            elif dst_subnet == GUEST_SUBNET:
                output_port = 8
            elif dst_subnet == DISCORD_SUBNET:
                output_port = 9
            else:
                print('Unknown Destination - Dropping Packet')
                drop()
                return

        # Access Switches forward internally or back to core
        elif switch_id == 2:  # Faculty Switch
            if dst_ip == '169.233.3.30':
                output_port = 3
            elif dst_ip == '169.233.3.20':
                output_port = 4
            elif dst_ip == '169.233.3.10':
                output_port = 5
            else:
                output_port = 2

        elif switch_id == 3:  # Student Switch
            if dst_ip == '169.233.4.1':
                output_port = 5
            elif dst_ip == '169.233.4.100':
                output_port = 4
            elif dst_ip == '169.233.4.2':
                output_port = 2
            else:
                output_port = 3

        elif switch_id == 4:  # IT Switch
            if dst_ip == '169.233.1.10':
                output_port = 3
            elif dst_ip == '169.233.1.20':
                output_port = 2
            elif dst_ip == '169.233.1.30':
                output_port = 5
            else:
                output_port = 4

        elif switch_id == 5:  # Data Center Switch
            if dst_ip == '169.233.2.1':
                output_port = 2
            elif dst_ip == '169.233.2.2':
                output_port = 3
            elif dst_ip == '169.233.2.3':
                output_port = 4
            else:
                output_port = 5

        # Internet Hosts -> Core
        elif switch_id in [6, 7, 8, 9]:
            output_port = 1

        # ------------------------------
        # Policy Enforcement
        # ------------------------------

        # Restrict Discord Server: Only Student Subnet can access
        if (dst_ip == '200.10.10.200' and src_subnet == STUDENT_SUBNET) or \
           (src_ip == '200.10.10.200' and dst_subnet == STUDENT_SUBNET):
            print("Discord Server allowed for Student Subnet only")
            accept(output_port)
            return

        # ICMP Policy
        if is_icmp:
            # Printer doesn’t support ICMP
            if dst_ip == '169.233.3.20':
                print("Printer does not accept ICMP - Dropping")
                drop()
                return

            # Allow ICMP between IT<->Faculty, IT<->Student, same-subnet
            if (src_subnet == IT_SUBNET and dst_subnet in [FACULTY_SUBNET, STUDENT_SUBNET]) or \
               (dst_subnet == IT_SUBNET and src_subnet in [FACULTY_SUBNET, STUDENT_SUBNET]) or \
               is_same_subnet(src_subnet, dst_subnet):
                accept(output_port)
                return

        # TCP Policy (selected cases shown)
        if is_tcp:
            # Guest may access Faculty Printer
            if (dst_ip == '169.233.3.20' and src_subnet == GUEST_SUBNET) or \
               (src_ip == '169.233.3.20' and dst_subnet == GUEST_SUBNET):
                print("Guest allowed to use Printer")
                accept(output_port)
                return

            # Allow inter-subnet TCP based on rules (examples: UDC<->IT, UDC<->Faculty, etc.)
            if is_same_subnet(src_subnet, dst_subnet) or \
               (src_subnet in [UDC_SUBNET, IT_SUBNET, FACULTY_SUBNET, STUDENT_SUBNET, PC1_SUBNET, PC2_SUBNET, GUEST_SUBNET] and
                dst_subnet in [UDC_SUBNET, IT_SUBNET, FACULTY_SUBNET, STUDENT_SUBNET, PC1_SUBNET, PC2_SUBNET, GUEST_SUBNET]):
                accept(output_port)
                return

        # UDP Policy (similar to TCP rules)
        if is_udp:
            if is_same_subnet(src_subnet, dst_subnet) or \
               (src_subnet in [UDC_SUBNET, IT_SUBNET, FACULTY_SUBNET, STUDENT_SUBNET] and
                dst_subnet in [UDC_SUBNET, IT_SUBNET, FACULTY_SUBNET, STUDENT_SUBNET]):
                accept(output_port)
                return

        # Default: drop packet
        drop()
        return

    def _handle_PacketIn(self, event):
        """Handles PacketIn events from the switch."""
        packet = event.parsed
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return
        packet_in = event.ofp
        self.do_routing(packet, packet_in, event.port, event.dpid)


def launch():
    """Start the POX routing module."""
    def start_switch(event):
        log.debug("Controlling %s" % (event.connection,))
        Routing(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)

