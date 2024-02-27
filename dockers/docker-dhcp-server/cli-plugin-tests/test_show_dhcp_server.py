import sys
from unittest import mock

from click.testing import CliRunner

import utilities_common.cli as clicommon

sys.path.append('../cli/show/plugins/')
import show_dhcp_server


class TestShowDHCPServer(object):
    def test_plugin_registration(self):
        cli = mock.MagicMock()
        show_dhcp_server.register(cli)

    def test_show_dhcp_server_ipv4_lease_without_dhcpintf(self, mock_db):
        expected_stdout = """\
+---------------------+-------------------+-------------+---------------------+---------------------+
| Interface           | MAC Address       | IP          | Lease Start         | Lease End           |
+=====================+===================+=============+=====================+=====================+
| Vlan1000|Ethernet10 | 10:70:fd:b6:13:00 | 192.168.0.1 | 2023-03-01 03:16:21 | 2023-03-01 03:31:21 |
+---------------------+-------------------+-------------+---------------------+---------------------+
| Vlan1000|Ethernet11 | 10:70:fd:b6:13:01 | 192.168.0.2 | 2023-03-01 03:16:21 | 2023-03-01 03:31:21 |
+---------------------+-------------------+-------------+---------------------+---------------------+
| Vlan1001|<Unknown>  | 10:70:fd:b6:13:02 | 192.168.0.3 | 2023-03-01 03:16:21 | 2023-03-01 03:31:21 |
+---------------------+-------------------+-------------+---------------------+---------------------+
"""
        runner = CliRunner()
        db = clicommon.Db()
        db.db = mock_db
        result = runner.invoke(show_dhcp_server.dhcp_server.commands["ipv4"].commands["lease"], [], obj=db)
        assert result.exit_code == 0, "exit code: {}, Exception: {}, Traceback: {}".format(result.exit_code, result.exception, result.exc_info)
        assert result.stdout == expected_stdout

    def test_show_dhcp_server_ipv4_lease_with_dhcpintf(self, mock_db):
        expected_stdout = """\
+---------------------+-------------------+-------------+---------------------+---------------------+
| Interface           | MAC Address       | IP          | Lease Start         | Lease End           |
+=====================+===================+=============+=====================+=====================+
| Vlan1000|Ethernet10 | 10:70:fd:b6:13:00 | 192.168.0.1 | 2023-03-01 03:16:21 | 2023-03-01 03:31:21 |
+---------------------+-------------------+-------------+---------------------+---------------------+
| Vlan1000|Ethernet11 | 10:70:fd:b6:13:01 | 192.168.0.2 | 2023-03-01 03:16:21 | 2023-03-01 03:31:21 |
+---------------------+-------------------+-------------+---------------------+---------------------+
"""
        runner = CliRunner()
        db = clicommon.Db()
        db.db = mock_db
        result = runner.invoke(show_dhcp_server.dhcp_server.commands["ipv4"].commands["lease"], ["Vlan1000"], obj=db)
        assert result.exit_code == 0, "exit code: {}, Exception: {}, Traceback: {}".format(result.exit_code, result.exception, result.exc_info)
        assert result.stdout == expected_stdout

    def test_show_dhcp_server_ipv4_lease_client_not_in_fdb(self, mock_db):
        expected_stdout = """\
+--------------------+-------------------+-------------+---------------------+---------------------+
| Interface          | MAC Address       | IP          | Lease Start         | Lease End           |
+====================+===================+=============+=====================+=====================+
| Vlan1001|<Unknown> | 10:70:fd:b6:13:02 | 192.168.0.3 | 2023-03-01 03:16:21 | 2023-03-01 03:31:21 |
+--------------------+-------------------+-------------+---------------------+---------------------+
"""
        runner = CliRunner()
        db = clicommon.Db()
        db.db = mock_db
        result = runner.invoke(show_dhcp_server.dhcp_server.commands["ipv4"].commands["lease"], ["Vlan1001"], obj=db)
        assert result.exit_code == 0, "exit code: {}, Exception: {}, Traceback: {}".format(result.exit_code, result.exception, result.exc_info)
        assert result.stdout == expected_stdout

    def test_show_dhcp_server_ipv4_range_without_name(self, mock_db):
        expected_stdout = """\
+---------+------------+------------+------------------------+
| Range   | IP Start   | IP End     | IP Count               |
+=========+============+============+========================+
| range1  | 100.1.1.3  | 100.1.1.5  | 3                      |
+---------+------------+------------+------------------------+
| range2  | 100.1.1.9  | 100.1.1.8  | range value is illegal |
+---------+------------+------------+------------------------+
| range3  | 100.1.1.10 | 100.1.1.10 | 1                      |
+---------+------------+------------+------------------------+
| range5  | 100.1.2.10 | 100.1.2.10 | 1                      |
+---------+------------+------------+------------------------+
| range6  | 100.1.2.11 | 100.1.2.11 | 1                      |
+---------+------------+------------+------------------------+
"""
        runner = CliRunner()
        db = clicommon.Db()
        db.db = mock_db
        result = runner.invoke(show_dhcp_server.dhcp_server.commands["ipv4"].commands["range"], [], obj=db)
        assert result.exit_code == 0, "exit code: {}, Exception: {}, Traceback: {}".format(result.exit_code, result.exception, result.exc_info)
        assert result.stdout == expected_stdout

    def test_show_dhcp_server_ipv4_range_with_name(self, mock_db):
        expected_stdout = """\
+---------+------------+-----------+------------+
| Range   | IP Start   | IP End    |   IP Count |
+=========+============+===========+============+
| range1  | 100.1.1.3  | 100.1.1.5 |          3 |
+---------+------------+-----------+------------+
"""
        runner = CliRunner()
        db = clicommon.Db()
        db.db = mock_db
        result = runner.invoke(show_dhcp_server.dhcp_server.commands["ipv4"].commands["range"], ["range1"], obj=db)
        assert result.exit_code == 0, "exit code: {}, Exception: {}, Traceback: {}".format(result.exit_code, result.exception, result.exc_info)
        assert result.stdout == expected_stdout

    def test_show_dhcp_server_ipv4_range_wrong_data(self, mock_db):
        expected_stdout = """\
+---------+------------+-----------+------------------------+
| Range   | IP Start   | IP End    | IP Count               |
+=========+============+===========+========================+
| range2  | 100.1.1.9  | 100.1.1.8 | range value is illegal |
+---------+------------+-----------+------------------------+
"""
        runner = CliRunner()
        db = clicommon.Db()
        db.db = mock_db
        result = runner.invoke(show_dhcp_server.dhcp_server.commands["ipv4"].commands["range"], ["range2"], obj=db)
        assert result.exit_code == 0, "exit code: {}, Exception: {}, Traceback: {}".format(result.exit_code, result.exception, result.exc_info)
        assert result.stdout == expected_stdout

    def test_show_dhcp_server_ipv4_range_single_ip(self, mock_db):
        expected_stdout = """\
+---------+------------+------------+------------+
| Range   | IP Start   | IP End     |   IP Count |
+=========+============+============+============+
| range3  | 100.1.1.10 | 100.1.1.10 |          1 |
+---------+------------+------------+------------+
"""
        runner = CliRunner()
        db = clicommon.Db()
        db.db = mock_db
        result = runner.invoke(show_dhcp_server.dhcp_server.commands["ipv4"].commands["range"], ["range3"], obj=db)
        assert result.exit_code == 0, "exit code: {}, Exception: {}, Traceback: {}".format(result.exit_code, result.exception, result.exc_info)
        assert result.stdout == expected_stdout

    def test_show_dhcp_server_ipv4_info_without_intf(self, mock_db):
        expected_stdout = """\
+-------------+--------+-----------+---------------+-----------------+----------+
| Interface   | Mode   | Gateway   | Netmask       |   Lease Time(s) | State    |
+=============+========+===========+===============+=================+==========+
| Vlan100     | PORT   | 100.1.1.1 | 255.255.255.0 |            3600 | enabled  |
+-------------+--------+-----------+---------------+-----------------+----------+
| Vlan300     | PORT   | 100.1.1.1 | 255.255.255.0 |            3600 | disabled |
+-------------+--------+-----------+---------------+-----------------+----------+
"""
        runner = CliRunner()
        db = clicommon.Db()
        db.db = mock_db
        result = runner.invoke(show_dhcp_server.dhcp_server.commands["ipv4"].commands["info"], [], obj=db)
        assert result.exit_code == 0, "exit code: {}, Exception: {}, Traceback: {}".format(result.exit_code, result.exception, result.exc_info)
        assert result.stdout == expected_stdout

    def test_show_dhcp_server_ipv4_info_with_intf(self, mock_db):
        expected_stdout = """\
+-------------+--------+-----------+---------------+-----------------+---------+
| Interface   | Mode   | Gateway   | Netmask       |   Lease Time(s) | State   |
+=============+========+===========+===============+=================+=========+
| Vlan100     | PORT   | 100.1.1.1 | 255.255.255.0 |            3600 | enabled |
+-------------+--------+-----------+---------------+-----------------+---------+
"""
        runner = CliRunner()
        db = clicommon.Db()
        db.db = mock_db
        result = runner.invoke(show_dhcp_server.dhcp_server.commands["ipv4"].commands["info"], ["Vlan100"], obj=db)
        assert result.exit_code == 0, "exit code: {}, Exception: {}, Traceback: {}".format(result.exit_code, result.exception, result.exc_info)
        assert result.stdout == expected_stdout

    def test_show_dhcp_server_ipv4_info_with_customized_options(self, mock_db):
        expected_stdout = """\
+-------------+--------+-----------+---------------+-----------------+---------+----------------------+
| Interface   | Mode   | Gateway   | Netmask       |   Lease Time(s) | State   | Customized Options   |
+=============+========+===========+===============+=================+=========+======================+
| Vlan100     | PORT   | 100.1.1.1 | 255.255.255.0 |            3600 | enabled | option60             |
+-------------+--------+-----------+---------------+-----------------+---------+----------------------+
"""
        runner = CliRunner()
        db = clicommon.Db()
        db.db = mock_db
        result = runner.invoke(show_dhcp_server.dhcp_server.commands["ipv4"].commands["info"], ["Vlan100", "--with_customized_options"], obj=db)
        assert result.exit_code == 0, "exit code: {}, Exception: {}, Traceback: {}".format(result.exit_code, result.exception, result.exc_info)
        assert result.stdout == expected_stdout

    def test_show_dhcp_server_ipv4_option_without_name(self, mock_db):
        expected_stdout = """\
+---------------+-------------+-------------+--------+
| Option Name   |   Option ID | Value       | Type   |
+===============+=============+=============+========+
| option60      |          60 | dummy_value | string |
+---------------+-------------+-------------+--------+
"""
        runner = CliRunner()
        db = clicommon.Db()
        db.db = mock_db
        result = runner.invoke(show_dhcp_server.dhcp_server.commands["ipv4"].commands["option"], [], obj=db)
        assert result.exit_code == 0, "exit code: {}, Exception: {}, Traceback: {}".format(result.exit_code, result.exception, result.exc_info)
        assert result.stdout == expected_stdout

    def test_show_dhcp_server_ipv4_option_with_name(self, mock_db):
        expected_stdout = """\
+---------------+-------------+-------------+--------+
| Option Name   |   Option ID | Value       | Type   |
+===============+=============+=============+========+
| option60      |          60 | dummy_value | string |
+---------------+-------------+-------------+--------+
"""
        runner = CliRunner()
        db = clicommon.Db()
        db.db = mock_db
        result = runner.invoke(show_dhcp_server.dhcp_server.commands["ipv4"].commands["option"], ["option60"], obj=db)
        assert result.exit_code == 0, "exit code: {}, Exception: {}, Traceback: {}".format(result.exit_code, result.exception, result.exc_info)
        assert result.stdout == expected_stdout

    def test_show_dhcp_server_ipv4_port_without_intf(self, mock_db):
        expected_stdout = """\
+-------------------+------------+
| Interface         | Bind       |
+===================+============+
| Vlan100|Ethernet4 | 100.1.1.10 |
|                   | 100.1.1.11 |
+-------------------+------------+
| Vlan100|Ethernet7 | range1     |
|                   | range3     |
+-------------------+------------+
| Vlan200|Ethernet8 | range5     |
|                   | range6     |
+-------------------+------------+
| Ethernet9         | range5     |
|                   | range6     |
+-------------------+------------+
"""
        runner = CliRunner()
        db = clicommon.Db()
        db.db = mock_db
        result = runner.invoke(show_dhcp_server.dhcp_server.commands["ipv4"].commands["port"], [], obj=db)
        assert result.exit_code == 0, "exit code: {}, Exception: {}, Traceback: {}".format(result.exit_code, result.exception, result.exc_info)
        assert result.stdout == expected_stdout

    def test_show_dhcp_server_ipv4_port_with_port(self, mock_db):
        expected_stdout = """\
+-------------------+--------+
| Interface         | Bind   |
+===================+========+
| Vlan100|Ethernet7 | range1 |
|                   | range3 |
+-------------------+--------+
"""
        runner = CliRunner()
        db = clicommon.Db()
        db.db = mock_db
        result = runner.invoke(show_dhcp_server.dhcp_server.commands["ipv4"].commands["port"], ["Ethernet7"], obj=db)
        assert result.exit_code == 0, "exit code: {}, Exception: {}, Traceback: {}".format(result.exit_code, result.exception, result.exc_info)
        assert result.stdout == expected_stdout

    def test_show_dhcp_server_ipv4_port_with_vlan(self, mock_db):
        expected_stdout = """\
+-------------------+------------+
| Interface         | Bind       |
+===================+============+
| Vlan100|Ethernet4 | 100.1.1.10 |
|                   | 100.1.1.11 |
+-------------------+------------+
| Vlan100|Ethernet7 | range1     |
|                   | range3     |
+-------------------+------------+
"""
        runner = CliRunner()
        db = clicommon.Db()
        db.db = mock_db
        result = runner.invoke(show_dhcp_server.dhcp_server.commands["ipv4"].commands["port"], ["Vlan100"], obj=db)
        assert result.exit_code == 0, "exit code: {}, Exception: {}, Traceback: {}".format(result.exit_code, result.exception, result.exc_info)
        assert result.stdout == expected_stdout

    def test_show_dhcp_server_ipv4_port_with_port_and_vlan(self, mock_db):
        expected_stdout = """\
+-------------------+--------+
| Interface         | Bind   |
+===================+========+
| Vlan200|Ethernet8 | range5 |
|                   | range6 |
+-------------------+--------+
"""
        runner = CliRunner()
        db = clicommon.Db()
        db.db = mock_db
        result = runner.invoke(show_dhcp_server.dhcp_server.commands["ipv4"].commands["port"], ["Vlan200|Ethernet8"], obj=db)
        assert result.exit_code == 0, "exit code: {}, Exception: {}, Traceback: {}".format(result.exit_code, result.exception, result.exc_info)
        assert result.stdout == expected_stdout

    def test_show_dhcp_server_ipv4_port_with_single_port(self, mock_db):
        expected_stdout = """\
+-------------+--------+
| Interface   | Bind   |
+=============+========+
| Ethernet9   | range5 |
|             | range6 |
+-------------+--------+
"""
        runner = CliRunner()
        db = clicommon.Db()
        db.db = mock_db
        result = runner.invoke(show_dhcp_server.dhcp_server.commands["ipv4"].commands["port"], ["Ethernet9"], obj=db)
        assert result.exit_code == 0, "exit code: {}, Exception: {}, Traceback: {}".format(result.exit_code, result.exception, result.exc_info)
        assert result.stdout == expected_stdout
