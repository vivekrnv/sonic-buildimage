#!/usr/bin/env python

import ipaddress
import os
import syslog

from jinja2 import Environment, FileSystemLoader
from dhcp_server.common.utils import merge_intervals, validate_str_type

PORT_MAP_PATH = "/tmp/port-name-alias-map.txt"
UNICODE_TYPE = str
DHCP_SERVER_IPV4 = "DHCP_SERVER_IPV4"
DHCP_SERVER_IPV4_CUSTOMIZED_OPTIONS = "DHCP_SERVER_IPV4_CUSTOMIZED_OPTIONS"
DHCP_SERVER_IPV4_RANGE = "DHCP_SERVER_IPV4_RANGE"
DHCP_SERVER_IPV4_PORT = "DHCP_SERVER_IPV4_PORT"
VLAN_INTERFACE = "VLAN_INTERFACE"
VLAN_MEMBER = "VLAN_MEMBER"
PORT_MODE_CHECKER = ["DhcpServerTableCfgChangeEventChecker", "DhcpPortTableEventChecker", "DhcpRangeTableEventChecker",
                     "DhcpOptionTableEventChecker", "VlanTableEventChecker", "VlanIntfTableEventChecker",
                     "VlanMemberTableEventChecker"]
LEASE_UPDATE_SCRIPT_PATH = "/etc/kea/lease_update.sh"
DEFAULT_LEASE_TIME = 900
DEFAULT_LEASE_PATH = "/tmp/kea-lease.csv"
KEA_DHCP4_CONF_TEMPLATE_PATH = "/usr/share/sonic/templates/kea-dhcp4.conf.j2"
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DHCP_OPTION_FILE = f"{SCRIPT_DIR}/dhcp_option.csv"
SUPPORT_DHCP_OPTION_TYPE = ["binary", "boolean", "ipv4-address", "string", "uint8", "uint16", "uint32"]


class DhcpServCfgGenerator(object):
    port_alias_map = {}
    lease_update_script_path = ""
    lease_path = ""

    def __init__(self, dhcp_db_connector, lease_path=DEFAULT_LEASE_PATH, port_map_path=PORT_MAP_PATH,
                 lease_update_script_path=LEASE_UPDATE_SCRIPT_PATH, dhcp_option_path=DHCP_OPTION_FILE,
                 kea_conf_template_path=KEA_DHCP4_CONF_TEMPLATE_PATH):
        self.db_connector = dhcp_db_connector
        self.lease_path = lease_path
        self.lease_update_script_path = lease_update_script_path
        # Read port alias map file, this file is render after container start, so it would not change any more
        self._parse_port_map_alias(port_map_path)
        # Get kea config template
        self._get_render_template(kea_conf_template_path)
        self._read_dhcp_option(dhcp_option_path)

    def generate(self):
        """
        Generate dhcp server config
        Returns:
            config string
            set of ranges used
            set of enabled dhcp interface
            set of used options
            set of db table need to be monitored
        """
        # Generate from running config_db
        # Get host name
        device_metadata = self.db_connector.get_config_db_table("DEVICE_METADATA")
        hostname = self._parse_hostname(device_metadata)
        # Get ip information of vlan
        vlan_interface = self.db_connector.get_config_db_table(VLAN_INTERFACE)
        vlan_member_table = self.db_connector.get_config_db_table(VLAN_MEMBER)
        vlan_interfaces, vlan_members = self._parse_vlan(vlan_interface, vlan_member_table)
        dhcp_server_ipv4, customized_options_ipv4, range_ipv4, port_ipv4 = self._get_dhcp_ipv4_tables_from_db()
        # Parse range table
        ranges = self._parse_range(range_ipv4)

        # Parse port table
        port_ips, used_ranges = self._parse_port(port_ipv4, vlan_interfaces, vlan_members, ranges)
        customized_options = self._parse_customized_options(customized_options_ipv4)
        render_obj, enabled_dhcp_interfaces, used_options, subscribe_table = \
            self._construct_obj_for_template(dhcp_server_ipv4, port_ips, hostname, customized_options)
        return self._render_config(render_obj), used_ranges, enabled_dhcp_interfaces, used_options, subscribe_table

    def _parse_customized_options(self, customized_options_ipv4):
        customized_options = {}
        for option_name, config in customized_options_ipv4.items():
            if config["id"] not in self.dhcp_option.keys():
                syslog.syslog(syslog.LOG_ERR, "Unsupported option: {}, currently only support unassigned options"
                              .format(config["id"]))
                continue
            option_type = config["type"] if "type" in config else "string"
            if option_type not in SUPPORT_DHCP_OPTION_TYPE:
                syslog.syslog(syslog.LOG_ERR, "Unsupported type: {}, currently only support {}"
                              .format(option_type, SUPPORT_DHCP_OPTION_TYPE))
                continue
            if not validate_str_type(option_type, config["value"]):
                syslog.syslog(syslog.LOG_ERR, "Option type [{}] and value [{}] are not consistent"
                              .format(option_type, config["value"]))
                continue
            if option_type == "string" and len(config["value"]) > 253:
                syslog.syslog(syslog.LOG_ERR, "String option value too long: {}".format(option_name))
                continue
            always_send = config["always_send"] if "always_send" in config else "true"
            customized_options[option_name] = {
                "id": config["id"],
                "value": config["value"],
                "type": option_type,
                "always_send": always_send
            }
        return customized_options

    def _render_config(self, render_obj):
        output = self.kea_template.render(render_obj)
        return output

    def _parse_vlan(self, vlan_interface, vlan_member):
        vlan_interfaces = self._get_vlan_ipv4_interface(vlan_interface.keys())
        vlan_members = vlan_member.keys()
        return vlan_interfaces, vlan_members

    def _parse_hostname(self, device_metadata):
        localhost_entry = device_metadata.get("localhost", {})
        if localhost_entry is None or "hostname" not in localhost_entry:
            syslog.syslog(syslog.LOG_ERR, "Cannot get hostname")
            raise Exception("Cannot get hostname")
        return localhost_entry["hostname"]

    def _get_render_template(self, kea_conf_template_path):
        # Semgrep does not allow to use jinja2 directly, but we do need jinja2 for SONiC
        env = Environment(loader=FileSystemLoader(os.path.dirname(kea_conf_template_path)))  # nosemgrep
        self.kea_template = env.get_template(os.path.basename(kea_conf_template_path))

    def _parse_port_map_alias(self, port_map_path):
        with open(port_map_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                splits = line.strip().split(" ")
                if len(splits) != 2:
                    continue
                self.port_alias_map[splits[0]] = splits[1]

    def _construct_obj_for_template(self, dhcp_server_ipv4, port_ips, hostname, customized_options):
        subnets = []
        client_classes = []
        enabled_dhcp_interfaces = set()
        used_options = set()
        # Different mode would subscribe different table, always subscribe DHCP_SERVER_IPV4
        subscribe_table = set(["DhcpServerTableCfgChangeEventChecker"])
        for dhcp_interface_name, dhcp_config in dhcp_server_ipv4.items():
            if "state" not in dhcp_config or dhcp_config["state"] != "enabled":
                continue
            enabled_dhcp_interfaces.add(dhcp_interface_name)
            if dhcp_config["mode"] == "PORT":
                subscribe_table |= set(PORT_MODE_CHECKER)
                if dhcp_interface_name not in port_ips:
                    syslog.syslog(syslog.LOG_WARNING, "Cannot get DHCP port config for {}"
                                  .format(dhcp_interface_name))
                    continue
                curr_options = {}
                for option in dhcp_config["customized_options"]:
                    if option in customized_options.keys():
                        curr_options[option] = {
                            "always_send": customized_options[option]["always_send"],
                            "value": customized_options[option]["value"]
                        }
                for dhcp_interface_ip, port_config in port_ips[dhcp_interface_name].items():
                    pools = []
                    for port_name, ip_ranges in port_config.items():
                        ip_range = None
                        for ip_range in ip_ranges:
                            client_class = "{}:{}".format(hostname, port_name)
                            ip_range = {
                                "range": "{} - {}".format(ip_range[0], ip_range[1]),
                                "client_class": client_class
                            }
                            pools.append(ip_range)
                        if ip_range is not None:
                            class_len = len(client_class)
                            client_classes.append({
                                "name": client_class,
                                "condition": "substring(relay4[1].hex, -{}, {}) == '{}'".format(class_len, class_len,
                                                                                                client_class)
                            })
                    subnet_obj = {
                        "subnet": str(ipaddress.ip_network(dhcp_interface_ip, strict=False)),
                        "pools": pools,
                        "gateway": dhcp_config["gateway"],
                        "server_id": dhcp_interface_ip.split("/")[0],
                        "lease_time": dhcp_config["lease_time"] if "lease_time" in dhcp_config else DEFAULT_LEASE_TIME,
                        "customized_options": curr_options
                    }
                    used_options = used_options | set(subnet_obj["customized_options"])
                    subnets.append(subnet_obj)
        render_obj = {
            "subnets": subnets,
            "client_classes": client_classes,
            "lease_update_script_path": self.lease_update_script_path,
            "lease_path": self.lease_path,
            "customized_options": customized_options
        }
        return render_obj, enabled_dhcp_interfaces, used_options, subscribe_table

    def _get_dhcp_ipv4_tables_from_db(self):
        """
        Get DHCP Server IPv4 related table from config_db.
        Returns:
            Four table objects.
        """
        dhcp_server_ipv4 = self.db_connector.get_config_db_table(DHCP_SERVER_IPV4)
        customized_options_ipv4 = self.db_connector.get_config_db_table(DHCP_SERVER_IPV4_CUSTOMIZED_OPTIONS)
        range_ipv4 = self.db_connector.get_config_db_table(DHCP_SERVER_IPV4_RANGE)
        port_ipv4 = self.db_connector.get_config_db_table(DHCP_SERVER_IPV4_PORT)
        return dhcp_server_ipv4, customized_options_ipv4, range_ipv4, port_ipv4

    def _get_vlan_ipv4_interface(self, vlan_interface_keys):
        """
        Get ipv4 info of vlans
        Args:
            vlan_interface_keys: Keys of vlan_interfaces, sample:
                [
                    "Vlan1000|192.168.0.1/21",
                    "Vlan1000|fc02:1000::1/64"
                ]
        Returns:
            Vlans infomation, sample:
                {
                    'Vlan1000': [{
                        'network': IPv4Network('192.168.0.0/24'),
                        'ip': '192.168.0.1/24'
                    }]
                }
        """
        ret = {}
        for key in vlan_interface_keys:
            splits = key.split("|")
            # Skip with no ip address
            if len(splits) != 2:
                continue
            network = ipaddress.ip_network(UNICODE_TYPE(splits[1]), False)
            # Skip ipv6
            if network.version != 4:
                continue
            if splits[0] not in ret:
                ret[splits[0]] = []
            ret[splits[0]].append({"network": network, "ip": splits[1]})
        return ret

    def _parse_range(self, range_ipv4):
        """
        Parse content in DHCP_SERVER_IPV4_RANGE table to below format:
        {
            'range2': [IPv4Address('192.168.0.3'), IPv4Address('192.168.0.6')],
            'range1': [IPv4Address('192.168.0.2'), IPv4Address('192.168.0.5')],
            'range3': [IPv4Address('192.168.0.10'), IPv4Address('192.168.0.10')]
        }
        Args:
            range_ipv4: Table object or dict of range.
        """
        ranges = {}
        for range in list(range_ipv4.keys()):
            curr_range = range_ipv4.get(range, {}).get("range", {})
            if len(curr_range) != 2:
                syslog.syslog(syslog.LOG_WARNING, f"Length of {curr_range} != 2")
                continue
            address_1 = ipaddress.ip_address(curr_range[0])
            address_2 = ipaddress.ip_address(curr_range[1])
            # To make sure order of range is correct
            range_start = address_1 if address_1 < address_2 else address_2
            range_end = address_2 if address_1 < address_2 else address_1
            ranges[range] = [range_start, range_end]

        return ranges

    def _match_range_network(self, dhcp_interface, dhcp_interface_name, port, range, port_ips):
        """
        Loop the IP of the dhcp interface and find the network that target range is in this network. And to construct
        below data to record range - port map
        {
            'Vlan1000': {
                '192.168.0.1/24': {
                    'etp2': [
                        [IPv4Address('192.168.0.7'), IPv4Address('192.168.0.7')]
                    ]
                }
            }
        }
        Args:
            dhcp_interface: Ip and network information of current DHCP interface, sample:
                [{
                    'network': IPv4Network('192.168.0.0/24'),
                    'ip': '192.168.0.1/24'
                }]
            dhcp_interface_name: Name of DHCP interface.
            port: Name of DHCP member port.
            range: Ip Range, sample:
                [IPv4Address('192.168.0.2'), IPv4Address('192.168.0.5')]
        """
        for dhcp_interface_ip in dhcp_interface:
            if not range[0] in dhcp_interface_ip["network"] or \
               not range[1] in dhcp_interface_ip["network"]:
                continue
            dhcp_interface_ip_str = dhcp_interface_ip["ip"]
            if dhcp_interface_ip_str not in port_ips[dhcp_interface_name]:
                port_ips[dhcp_interface_name][dhcp_interface_ip_str] = {}
            if port not in port_ips[dhcp_interface_name][dhcp_interface_ip_str]:
                port_ips[dhcp_interface_name][dhcp_interface_ip_str][port] = []
            port_ips[dhcp_interface_name][dhcp_interface_ip_str][port].append([range[0], range[1]])
            break

    def _parse_port(self, port_ipv4, vlan_interfaces, vlan_members, ranges):
        """
        Parse content in DHCP_SERVER_IPV4_PORT table to below format, which indicate ip ranges assign to interface.
        Args:
            port_ipv4: Table object.
            vlan_interfaces: Vlan information, sample:
                {
                    'Vlan1000': [{
                        'network': IPv4Network('192.168.0.0/24'),
                        'ip': '192.168.0.1/24'
                    }]
                }
            vlan_members: List of vlan members
            ranges: Dict of ranges
        Returns:
            Dict of dhcp conf, sample:
                {
                    'Vlan1000': {
                        '192.168.0.1/24': {
                            'etp2': [
                                ['192.168.0.7', '192.168.0.7']
                            ],
                            'etp3': [
                                ['192.168.0.2', '192.168.0.6'],
                                ['192.168.0.10', '192.168.0.10']
                            ]
                        }
                    }
                }
            Set of used ranges.
        """
        port_ips = {}
        ip_ports = {}
        used_ranges = set()
        for port_key in list(port_ipv4.keys()):
            port_config = port_ipv4.get(port_key, {})
            # Cannot specify both 'ips' and 'ranges'
            if "ips" in port_config and len(port_config["ips"]) != 0 and "ranges" in port_config \
               and len(port_config["ranges"]) != 0:
                syslog.syslog(syslog.LOG_WARNING, f"Port config for {port_key} contains both ips and ranges, skip")
                continue
            splits = port_key.split("|")
            # Skip port not in correct vlan
            if port_key not in vlan_members:
                syslog.syslog(syslog.LOG_WARNING, f"Port {splits[1]} is not in {splits[0]}")
                continue
            # Get dhcp interface name like Vlan1000
            dhcp_interface_name = splits[0]
            # Get dhcp member interface name like etp1
            if splits[1] not in self.port_alias_map:
                syslog.syslog(syslog.LOG_WARNING, f"Cannot find {splits[1]} in port_alias_map")
                continue
            port = self.port_alias_map[splits[1]]
            if dhcp_interface_name not in port_ips:
                port_ips[dhcp_interface_name] = {}
            # Get ip information of Vlan
            dhcp_interface = vlan_interfaces[dhcp_interface_name]

            for dhcp_interface_ip in dhcp_interface:
                ip_ports[str(dhcp_interface_ip["network"])] = dhcp_interface_name

            if "ips" in port_config and len(port_config["ips"]) != 0:
                for ip in set(port_config["ips"]):
                    ip_address = ipaddress.ip_address(ip)
                    # Loop the IP of the dhcp interface and find the network that target ip is in this network.
                    self._match_range_network(dhcp_interface, dhcp_interface_name, port, [ip_address, ip_address],
                                              port_ips)
            if "ranges" in port_config and len(port_config["ranges"]) != 0:
                for range_name in list(port_config["ranges"]):
                    if range_name not in ranges:
                        syslog.syslog(syslog.LOG_WARNING, f"Range {range_name} is not in range table, skip")
                        continue
                    used_ranges.add(range_name)
                    range = ranges[range_name]
                    # Loop the IP of the dhcp interface and find the network that target range is in this network.
                    self._match_range_network(dhcp_interface, dhcp_interface_name, port, range, port_ips)
        # Merge ranges to avoid overlap
        for dhcp_interface_name, value in port_ips.items():
            for dhcp_interface_ip, port_range in value.items():
                for port_name, ip_range in port_range.items():
                    ranges = merge_intervals(ip_range)
                    ranges = [[str(range[0]), str(range[1])] for range in ranges]
                    port_ips[dhcp_interface_name][dhcp_interface_ip][port_name] = ranges
        return port_ips, used_ranges

    def _read_dhcp_option(self, file_path):
        # TODO current only support unassigned options, use dict in case support more options in the future
        # key: option cod, value: option type list
        self.dhcp_option = {}
        with open(file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                if "Code,Type,Customized Type" in line:
                    continue
                splits = line.strip().split(",")
                if splits[-1] == "unassigned":
                    self.dhcp_option[splits[0]] = []
