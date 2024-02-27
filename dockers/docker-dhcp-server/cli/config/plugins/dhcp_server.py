import click
import utilities_common.cli as clicommon

import ipaddress
import string


SUPPORT_TYPE = ["binary", "boolean", "ipv4-address", "string", "uint8", "uint16", "uint32"]


def validate_str_type(type_, value):
    """
    To validate whether type is consistent with string value
    Args:
        type: string, value type
        value: checked value
    Returns:
        True, type consistent with value
        False, type not consistent with value
    """
    if not isinstance(value, str):
        return False
    if type_ not in SUPPORT_TYPE:
        return False
    if type_ == "string":
        return True
    if type_ == "binary":
        if len(value) == 0 or len(value) % 2 != 0:
            return False
        return all(c in set(string.hexdigits) for c in value)
    if type_ == "boolean":
        return value in ["true", "false"]
    if type_ == "ipv4-address":
        try:
            if len(value.split(".")) != 4:
                return False
            return ipaddress.ip_address(value).version == 4
        except ValueError:
            return False
    if type_.startswith("uint"):
        if not value.isdigit():
            return False
        length = int("".join([c for c in type_ if c.isdigit()]))
        return 0 <= int(value) <= int(pow(2, length)) - 1
    return False


@click.group(cls=clicommon.AbbreviationGroup, name="dhcp_server")
def dhcp_server():
    """config DHCP Server information"""
    ctx = click.get_current_context()
    dbconn = db.db
    if dbconn.get("CONFIG_DB", "FEATURE|dhcp_server", "state") != "enabled":
        ctx.fail("Feature dhcp_server is not enabled")


@dhcp_server.group(cls=clicommon.AliasedGroup, name="ipv4")
def dhcp_server_ipv4():
    """Show ipv4 related dhcp_server info"""
    pass


@dhcp_server_ipv4.command(name="add")
@click.argument("dhcp_interface", required=True)
@click.option("--mode", required=True)
@click.option("--lease_time", required=False, default="900")
@click.option("--dup_gw_nm", required=False, default=False, is_flag=True)
@click.option("--gateway", required=False)
@click.option("--netmask", required=False)
@clicommon.pass_db
def dhcp_server_ipv4_add(db, mode, lease_time, dup_gw_nm, gateway, netmask, dhcp_interface):
    ctx = click.get_current_context()
    if mode != "PORT":
        ctx.fail("Only mode PORT is supported")
    if not validate_str_type("uint32", lease_time):
        ctx.fail("lease_time is required and must be nonnegative integer")
    dbconn = db.db
    if not dbconn.exists("CONFIG_DB", "VLAN_INTERFACE|" + dhcp_interface):
        ctx.fail("dhcp_interface {} does not exist".format(dhcp_interface))
    if dup_gw_nm:
        dup_success = False
        for key in dbconn.keys("CONFIG_DB", "VLAN_INTERFACE|" + dhcp_interface + "|*"):
            intf = ipaddress.ip_interface(key.split("|")[2])
            if intf.version != 4:
                continue
            dup_success = True
            gateway, netmask = str(intf.ip), str(intf.netmask)
        if not dup_success:
            ctx.fail("failed to found gateway and netmask for Vlan interface {}".format(dhcp_interface))
    elif not validate_str_type("ipv4-address", gateway) or not validate_str_type("ipv4-address", netmask):
        ctx.fail("gateway and netmask must be valid ipv4 string")
    key = "DHCP_SERVER_IPV4|" + dhcp_interface
    if dbconn.exists("CONFIG_DB", key):
        ctx.fail("Dhcp_interface {} already exist".format(dhcp_interface))
    else:
        dbconn.hmset("CONFIG_DB", key, {
            "mode": mode,
            "lease_time": lease_time,
            "gateway": gateway,
            "netmask": netmask,
            "state": "disabled",
            })


@dhcp_server_ipv4.command(name="del")
@click.argument("dhcp_interface", required=True)
@clicommon.pass_db
def dhcp_server_ipv4_del(db, dhcp_interface):
    ctx = click.get_current_context()
    dbconn = db.db
    key = "DHCP_SERVER_IPV4|" + dhcp_interface
    if dbconn.exists("CONFIG_DB", key):
        click.echo("Dhcp interface {} exists in config db, proceed to delete".format(dhcp_interface))
        dbconn.delete("CONFIG_DB", key)
    else:
        ctx.fail("Dhcp interface {} does not exist in config db".format(dhcp_interface))


@dhcp_server_ipv4.command(name="update")
@click.argument("dhcp_interface", required=True)
@click.option("--mode", required=False)
@click.option("--lease_time", required=False)
@click.option("--dup_gw_nm", required=False, default=False, is_flag=True)
@click.option("--gateway", required=False)
@click.option("--netmask", required=False)
@clicommon.pass_db
def dhcp_server_ipv4_update(db, mode, lease_time, dup_gw_nm, gateway, netmask, dhcp_interface):
    ctx = click.get_current_context()
    dbconn = db.db
    key = "DHCP_SERVER_IPV4|" + dhcp_interface
    if not dbconn.exists("CONFIG_DB", key):
        ctx.fail("Dhcp interface {} does not exist in config db".format(dhcp_interface))
    if mode:
        if mode != "PORT":
            ctx.fail("Only mode PORT is supported")
        else:
            dbconn.set("CONFIG_DB", key, "mode", mode)
    if lease_time:
        if not validate_str_type("uint32", lease_time):
            ctx.fail("lease_time is required and must be nonnegative integer")
        else:
            dbconn.set("CONFIG_DB", key, "lease_time", lease_time)
    if dup_gw_nm:
        dup_success = False
        for key in dbconn.keys("CONFIG_DB", "VLAN_INTERFACE|" + dhcp_interface + "|*"):
            intf = ipaddress.ip_interface(key.split("|")[2])
            if intf.version != 4:
                continue
            dup_success = True
            gateway, netmask = str(intf.ip), str(intf.netmask)
        if not dup_success:
            ctx.fail("failed to found gateway and netmask for Vlan interface {}".format(dhcp_interface))
    elif gateway and not validate_str_type("ipv4-address", gateway):
        ctx.fail("gateway must be valid ipv4 string")
    elif netmask and not validate_str_type("ipv4-address", netmask):
        ctx.fail("netmask must be valid ipv4 string")
    if gateway:
        dbconn.set("CONFIG_DB", key, "gateway", gateway)
    if netmask:
        dbconn.set("CONFIG_DB", key, "netmask", netmask)


@dhcp_server_ipv4.command(name="enable")
@click.argument("dhcp_interface", required=True)
@clicommon.pass_db
def dhcp_server_ipv4_enable(db, dhcp_interface):
    ctx = click.get_current_context()
    dbconn = db.db
    key = "DHCP_SERVER_IPV4|" + dhcp_interface
    if dbconn.exists("CONFIG_DB", key):
        dbconn.set("CONFIG_DB", key, "state", "enabled")
    else:
        ctx.fail("Failed to enable, dhcp interface {} does not exist".format(dhcp_interface))


@dhcp_server_ipv4.command(name="disable")
@click.argument("dhcp_interface", required=True)
@clicommon.pass_db
def dhcp_server_ipv4_disable(db, dhcp_interface):
    ctx = click.get_current_context()
    dbconn = db.db
    key = "DHCP_SERVER_IPV4|" + dhcp_interface
    if dbconn.exists("CONFIG_DB", key):
        dbconn.set("CONFIG_DB", key, "state", "disabled")
    else:
        ctx.fail("Failed to disable, dhcp interface {} does not exist".format(dhcp_interface))


@dhcp_server_ipv4.group(cls=clicommon.AliasedGroup, name="range")
def dhcp_server_ipv4_range():
    pass


def count_ipv4(start, end):
    ip1 = int(ipaddress.IPv4Address(start))
    ip2 = int(ipaddress.IPv4Address(end))
    return ip2 - ip1 + 1


@dhcp_server_ipv4_range.command(name="add")
@click.argument("range_name", required=True)
@click.argument("ip_start", required=True)
@click.argument("ip_end", required=False)
@clicommon.pass_db
def dhcp_server_ipv4_range_add(db, range_name, ip_start, ip_end):
    ctx = click.get_current_context()
    if not ip_end:
        ip_end = ip_start
    if not validate_str_type("ipv4-address", ip_start) or not validate_str_type("ipv4-address", ip_end):
        ctx.fail("ip_start or ip_end is not valid ipv4 address")
    if count_ipv4(ip_start, ip_end) < 1:
        ctx.fail("range value is illegal")
    dbconn = db.db
    key = "DHCP_SERVER_IPV4_RANGE|" + range_name
    if dbconn.exists("CONFIG_DB", key):
        ctx.fail("Range {} already exist".format(range_name))
    else:
        dbconn.hmset("CONFIG_DB", key, {"range": ip_start + "," + ip_end})


@dhcp_server_ipv4_range.command(name="update")
@click.argument("range_name", required=True)
@click.argument("ip_start", required=True)
@click.argument("ip_end", required=False)
@clicommon.pass_db
def dhcp_server_ipv4_range_update(db, range_name, ip_start, ip_end):
    ctx = click.get_current_context()
    if not ip_end:
        ip_end = ip_start
    if not validate_str_type("ipv4-address", ip_start) or not validate_str_type("ipv4-address", ip_end):
        ctx.fail("ip_start or ip_end is not valid ipv4 address")
    if count_ipv4(ip_start, ip_end) < 1:
        ctx.fail("range value is illegal")
    dbconn = db.db
    key = "DHCP_SERVER_IPV4_RANGE|" + range_name
    if dbconn.exists("CONFIG_DB", key):
        dbconn.set("CONFIG_DB", key, "range", ip_start + "," + ip_end)
    else:
        ctx.fail("Range {} does not exist, cannot update".format(range_name))


@dhcp_server_ipv4_range.command(name="del")
@click.argument("range_name", required=True)
@click.option("--force", required=False, default=False, is_flag=True)
@clicommon.pass_db
def dhcp_sever_ipv4_range_del(db, range_name, force):
    ctx = click.get_current_context()
    dbconn = db.db
    key = "DHCP_SERVER_IPV4_RANGE|" + range_name
    if dbconn.exists("CONFIG_DB", key):
        if not force:
            for port in dbconn.keys("CONFIG_DB", "DHCP_SERVER_IPV4_PORT*"):
                ranges = dbconn.get("CONFIG_DB", port, "ranges")
                if ranges and range_name in ranges.split(","):
                    ctx.fail("Range {} is referenced in {}, cannot delete, add --force to bypass or range unbind to unbind range first".format(range_name, port))
        dbconn.delete("CONFIG_DB", key)
    else:
        ctx.fail("Range {} does not exist, cannot delete".format(range_name))


@dhcp_server_ipv4.command(name="bind")
@click.argument("dhcp_interface", required=True)
@click.argument("member_interface", required=True)
@click.option("--range", "range_", required=False)
@click.argument("ip_list", required=False)
@clicommon.pass_db
def dhcp_server_ipv4_ip_bind(db, dhcp_interface, member_interface, range_, ip_list):
    ctx = click.get_current_context()
    dbconn = db.db
    if not dbconn.exists("CONFIG_DB", "VLAN_MEMBER|" + dhcp_interface + "|" + member_interface):
        ctx.fail("Cannot confirm member interface {} is really in dhcp interface {}".format(member_interface, dhcp_interface))
    vlan_prefix = "VLAN_INTERFACE|" + dhcp_interface + "|"
    subnets = [ipaddress.ip_network(key[len(vlan_prefix):], strict=False) for key in dbconn.keys("CONFIG_DB", vlan_prefix + "*")]
    if range_:
        range_ = set(range_.split(","))
        for r in range_:
            if not dbconn.exists("CONFIG_DB", "DHCP_SERVER_IPV4_RANGE|" + r):
                ctx.fail("Cannot bind nonexistent range {} to interface".format(r))
            ip_range = dbconn.get("CONFIG_DB", "DHCP_SERVER_IPV4_RANGE|" + r, "range").split(",")
            if len(ip_range) == 1:
                ip_start = ip_range[0]
                ip_end = ip_range[0]
            if len(ip_range) == 2:
                ip_start = ip_range[0]
                ip_end = ip_range[1]
            if not any([ipaddress.ip_address(ip_start) in subnet and ipaddress.ip_address(ip_end) in subnet for subnet in subnets]):
                ctx.fail("Range {} is not in any subnet of vlan {}".format(r, dhcp_interface))
    if ip_list:
        ip_list = set(ip_list.split(","))
        for ip in ip_list:
            if not validate_str_type("ipv4-address", ip):
                ctx.fail("Illegal IP address {}".format(ip))
            if not any([ipaddress.ip_address(ip) in subnet for subnet in subnets]):
                ctx.fail("IP {} is not in any subnet of vlan {}".format(ip, dhcp_interface))
    if range_ and ip_list or not range_ and not ip_list:
        ctx.fail("Only one of range and ip list need to be provided")
    key = "DHCP_SERVER_IPV4_PORT|" + dhcp_interface + "|" + member_interface
    key_exist = dbconn.exists("CONFIG_DB", key)
    for bind_value_name, bind_value in [["ips", ip_list], ["ranges", range_]]:
        if key_exist:
            existing_value = dbconn.get("CONFIG_DB", key, bind_value_name)
            if (not not existing_value) == (not bind_value):
                ctx.fail("IP bind cannot have ip range and ip list configured at the same time")
            if bind_value:
                value_set = set(existing_value.split(",")) if existing_value else set()
                new_value_set = value_set.union(bind_value)
                dbconn.set("CONFIG_DB", key, bind_value_name, ",".join(new_value_set))
        elif bind_value:
            dbconn.hmset("CONFIG_DB", key, {bind_value_name: ",".join(bind_value)})


@dhcp_server_ipv4.command(name="unbind")
@click.argument("dhcp_interface", required=True)
@click.argument("member_interface", required=True)
@click.option("--range", "range_", required=False)
@click.argument("ip_list", required=False)
@clicommon.pass_db
def dhcp_server_ipv4_ip_unbind(db, dhcp_interface, member_interface, range_, ip_list):
    ctx = click.get_current_context()
    dbconn = db.db
    key = "DHCP_SERVER_IPV4_PORT|" + dhcp_interface + "|" + member_interface
    if ip_list == "all":
        dbconn.delete("CONFIG_DB", key)
        return
    if range_ and ip_list or not range_ and not ip_list:
        ctx.fail("Only one of range and ip list need to be provided")
    if not dbconn.exists("CONFIG_DB", key):
        ctx.fail("The specified dhcp_interface and member interface is not bind to ip or range")
    for unbind_value_name, unbind_value in [["ips", ip_list], ["ranges", range_]]:
        if unbind_value:
            unbind_value = set(unbind_value.split(","))
            existing_value = dbconn.get("CONFIG_DB", key, unbind_value_name)
            value_set = set(existing_value.split(",")) if existing_value else set()
            if value_set.issuperset(unbind_value):
                new_value_set = value_set.difference(unbind_value)
                if new_value_set:
                    dbconn.set("CONFIG_DB", key, unbind_value_name, ",".join(new_value_set))
                else:
                    dbconn.delete("CONFIG_DB", key)
            else:
                ctx.fail("Attempting to unbind range or ip that is not binded")


def register(cli):
    # cli.add_command(dhcp_server)
    pass


if __name__ == '__main__':
    dhcp_server()
