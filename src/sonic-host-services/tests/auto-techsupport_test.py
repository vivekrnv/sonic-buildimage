import os
import sys
import time
import pytest
import unittest
import pyfakefs 
from pyfakefs.fake_filesystem_unittest import Patcher
from mock import patch, create_autospec
from sonic_py_common.general import load_module_from_source
import swsssdk
from .mock_connector import MockConnector, RedisSingleton

# Mock the SonicV2Connector
swsssdk.SonicV2Connector = MockConnector

test_path = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(test_path)
scripts_path = os.path.join(modules_path, "scripts")
sys.path.insert(0, modules_path)

# Load the file under test
ats_path = os.path.join(scripts_path, 'auto-techsupport')
ats = load_module_from_source('auto-techsupport', ats_path)


# Handle to Check the Updates made by the script
RedisHandle = RedisSingleton.getInstance()

def clear_redis():
    RedisHandle.data[ats.CFG_DB].clear()

class TestTechsupportCreationEvent(unittest.TestCase):
    
    def setUp(self):
        self.orig_time_buf = ats.TIME_BUF
        ats.TIME_BUF = 1 # Path the buf to 1 sec
    
    def tearDown(self):
        ats.TIME_BUF = self.orig_time_buf
    
    def assert_clean_exit(self, func, *args, **kwargs):
        with pytest.raises(SystemExit) as exc:
            func(*args, **kwargs)
        assert exc.value.code == 0, "{} did not exit with success".format(func.__name__)
    
    def test_spurious_invoc(self):
        """ Scenario: Event Notification by the systemd is not because of techsupport dump. """
        clear_redis()
        with Patcher() as patcher:
            patcher.fs.create_file('/var/dump/random.txt')
            ats.handle_techsupport_creation_event()
    
    def test_legit_invoc(self):
        """ Scenario: Legit Event Notification."""
        clear_redis()
        RedisHandle.data[ats.CFG_DB] = {ats.AUTO_TS : {ats.CFG_STATE : "enabled"}} # Enable the Feature
        with Patcher() as patcher:
            patcher.fs.create_file("/var/dump/sonic_dump_random.tar.gz")
            ats.handle_techsupport_creation_event()
            current_fs = os.listdir(ats.TS_DIR)
            print(current_fs)
            assert len(current_fs) == 1 # Shouldn't be deleted
            assert "sonic_dump_random.tar.gz" in current_fs
            
            
    def test_cleanup_process(self):
        """ Scenario: Check TechSupport Cleanup is properly performed """
        clear_redis()
        RedisHandle.data[ats.CFG_DB] = {ats.AUTO_TS : {ats.CFG_STATE : "enabled", ats.CFG_MAX_TS : "2"}} 
        print(RedisHandle.data[ats.CFG_DB])
        with Patcher() as patcher:
            patcher.fs.create_file("/var/dump/sonic_dump_random1.tar.gz")
            patcher.fs.create_file("/var/dump/sonic_dump_random2.tar.gz")
            patcher.fs.create_file("/var/dump/sonic_dump_random3.tar.gz") 
            ats.handle_techsupport_creation_event()
            current_fs = os.listdir(ats.TS_DIR)
            print(current_fs)
            assert len(current_fs) == 2
            assert "sonic_dump_random2.tar.gz" in current_fs
            assert "sonic_dump_random3.tar.gz" in current_fs
            assert "sonic_dump_random1.tar.gz" not in current_fs 
    
    def test_multiple_file_cleanup(self):
        clear_redis()
        RedisHandle.data[ats.CFG_DB] = {ats.AUTO_TS : {ats.CFG_STATE : "enabled", ats.CFG_MAX_TS : "2"}} 
        print(RedisHandle.data[ats.CFG_DB])
        with Patcher() as patcher:
            patcher.fs.create_file("/var/dump/sonic_dump_random1.tar.gz")
            patcher.fs.create_file("/var/dump/sonic_dump_random2.tar.gz")
            patcher.fs.create_file("/var/dump/sonic_dump_random3.tar.gz") 
            patcher.fs.create_file("/var/dump/sonic_dump_random4.tar.gz")
            patcher.fs.create_file("/var/dump/sonic_dump_random5.tar.gz")
            ats.handle_techsupport_creation_event()
            current_fs = os.listdir(ats.TS_DIR)
            print(current_fs)
            assert len(current_fs) == 2
            assert "sonic_dump_random4.tar.gz" in current_fs
            assert "sonic_dump_random5.tar.gz" in current_fs
            assert "sonic_dump_random1.tar.gz" not in current_fs
            assert "sonic_dump_random2.tar.gz" not in current_fs
            assert "sonic_dump_random3.tar.gz" not in current_fs
                      
    def test_no_cleanup(self):
        """ Scenario: Check TechSupport Cleanup is properly performed """
        clear_redis()
        RedisHandle.data[ats.CFG_DB] = {ats.AUTO_TS : {ats.CFG_STATE : "enabled", ats.CFG_MAX_TS : "5"}} 
        print(RedisHandle.data[ats.CFG_DB])
        with Patcher() as patcher:
            patcher.fs.create_file("/var/dump/sonic_dump_random1.tar.gz")
            patcher.fs.create_file("/var/dump/sonic_dump_random2.tar.gz")
            patcher.fs.create_file("/var/dump/sonic_dump_random3.tar.gz") # Event Trigger
            ats.handle_techsupport_creation_event()
            current_fs = os.listdir(ats.TS_DIR)
            print(current_fs)
            assert len(current_fs) == 3
            assert "sonic_dump_random2.tar.gz" in current_fs
            assert "sonic_dump_random3.tar.gz" in current_fs
            assert "sonic_dump_random1.tar.gz" in current_fs
    
    def test_spurious_invoc_with_prev_dump(self):
        """ Scenario: Spurious Event with previous TS Dumps """
        clear_redis()
        RedisHandle.data[ats.CFG_DB] = {ats.AUTO_TS : {ats.CFG_STATE : "enabled", ats.CFG_MAX_TS : "3"}} 
        print(RedisHandle.data[ats.CFG_DB])
        
        with Patcher() as patcher:
            patcher.fs.create_file("/var/dump/sonic_dump_random1.tar.gz")
            patcher.fs.create_file("/var/dump/sonic_dump_random2.tar.gz")
            patcher.fs.create_file("/var/dump/sonic_dump_random3.tar.gz") 
            time.sleep(1)
            patcher.fs.create_file("/var/dump/sonic_dump.txt") # Spurious Event
            ats.handle_techsupport_creation_event()
            current_fs = os.listdir(ats.TS_DIR)
            print(current_fs)
            assert "sonic_dump_random2.tar.gz" in current_fs
            assert "sonic_dump_random3.tar.gz" in current_fs
            assert "sonic_dump_random1.tar.gz" in current_fs
        ats.TIME_BUF = 20
    
    def tes_deletion_event(self):
        """ Scenario: TS Dump Deletion Event. Basically, Nothing should happen """
        clear_redis()
        RedisHandle.data[ats.CFG_DB] = {ats.AUTO_TS : {ats.CFG_STATE : "enabled", ats.CFG_MAX_TS : "3"}} 
        print(RedisHandle.data[ats.CFG_DB])
        ats.TIME_BUF = 1 # Patch the buf to 1 sec
        with Patcher() as patcher:
            patcher.fs.create_file("/var/dump/sonic_dump_random1.tar.gz")
            patcher.fs.create_file("/var/dump/sonic_dump_random2.tar.gz")
            patcher.fs.create_file("/var/dump/sonic_dump_random3.tar.gz") 
            time.sleep(1)
            patcher.fs.delete_file("/var/dump/sonic_dump_random2.tar.gz") # Spurious Event
            ats.handle_techsupport_creation_event()
            current_fs = os.listdir(ats.TS_DIR)
            print(current_fs)
            assert "sonic_dump_random3.tar.gz" not in current_fs
            assert "sonic_dump_random3.tar.gz" in current_fs
            assert "sonic_dump_random1.tar.gz" in current_fs
        ats.TIME_BUF = 20
    
class TestCoreDumpCreation(unittest.TestCase):
    
    def setUp(self):
        self.orig_time_buf = ats.TIME_BUF
        self.orig_mock_exec = ats.subprocess_exec
        ats.TIME_BUF = 1 # Patch the buf to 1 sec
        
    def tearDown(self):
        ats.TIME_BUF = self.orig_time_buf
        ats.subprocess_exec = self.orig_mock_exec
    
    def test_spurious_invoc(self):
        clear_redis()
        with Patcher() as patcher:
            patcher.fs.create_file("/var/dump/random.txt")
            ats.handle_core_dump_creation_event()
    
    def test_invoc_ts_without_cooloff(self):
        RedisHandle.data[ats.CFG_DB] = {ats.AUTO_TS : {ats.CFG_STATE : "enabled"}}
        with Patcher() as patcher:
            def mock_ts_invoc(cmd):
                cmd_str = " ".join(cmd)
                assert cmd_str == "show techsupport" 
                patcher.fs.create_file("/var/dump/sonic_dump_random999.tar.gz")
                return 0, "", ""
            ats.subprocess_exec = mock_ts_invoc
            patcher.fs.create_file("/var/core/random.12345.123.core.gz")
            ats.handle_core_dump_creation_event()
            assert "sonic_dump_random999.tar.gz" in os.listdir(ats.TS_DIR)
            assert "random.12345.123.core.gz" in os.listdir(ats.CORE_DUMP_DIR)
    
    def test_cooloff_active(self):
        RedisHandle.data[ats.CFG_DB] = {ats.AUTO_TS : {ats.CFG_STATE : "enabled", ats.CFG_COOLOFF : "5"}}
        with Patcher() as patcher:
            def mock_ts_invoc(cmd): 
                patcher.fs.create_file("/var/dump/sonic_dump_random999.tar.gz")
                return 0, "", ""
            ats.subprocess_exec = mock_ts_invoc
            patcher.fs.create_file("/var/dump/sonic_dump_random998.tar.gz")
            patcher.fs.create_file("/var/core/random.12345.123.core.gz")
            ats.handle_core_dump_creation_event()
            assert "sonic_dump_random999.tar.gz" not in os.listdir(ats.TS_DIR)
            assert "sonic_dump_random998.tar.gz" in os.listdir(ats.TS_DIR)
            assert "random.12345.123.core.gz" in os.listdir(ats.CORE_DUMP_DIR)
    
    def test_invoc_ts_after_cooloff(self):
        RedisHandle.data[ats.CFG_DB] = {ats.AUTO_TS : {ats.CFG_STATE : "enabled", ats.CFG_COOLOFF : "1"}}
        with Patcher() as patcher:
            def mock_ts_invoc(cmd):
                cmd_str = " ".join(cmd)
                assert cmd_str == "show techsupport" 
                patcher.fs.create_file("/var/dump/sonic_dump_random999.tar.gz")
                return 0, "", ""
            ats.subprocess_exec = mock_ts_invoc
            patcher.fs.create_file("/var/dump/sonic_dump_random998.tar.gz")
            patcher.fs.create_file("/var/core/random.12345.123.core.gz")
            time.sleep(1) #Wait for the cooloff
            ats.handle_core_dump_creation_event()
            assert "sonic_dump_random999.tar.gz" in os.listdir(ats.TS_DIR)
            assert "sonic_dump_random998.tar.gz" in os.listdir(ats.TS_DIR)
            assert "random.12345.123.core.gz" in os.listdir(ats.CORE_DUMP_DIR)
        
    def test_core_cleanup(self):
        RedisHandle.data[ats.CFG_DB] = {ats.AUTO_TS : {ats.CFG_STATE : "enabled", ats.CFG_CORE_USAGE : "5"}}
        with Patcher() as patcher:
            patcher.fs.set_disk_usage(5000, path="/var/core/")
            def mock_ts_invoc(cmd):
                cmd_str = " ".join(cmd)
                assert cmd_str == "show techsupport" 
                patcher.fs.create_file("/var/dump/sonic_dump_random999.tar.gz")
                return 0, "", ""
            ats.subprocess_exec = mock_ts_invoc
            patcher.fs.create_file("/var/core/sflowmgrd.1624582972.161.core.gz", st_size=80)
            patcher.fs.create_file("/var/core/caclmgrd.1624582976.22344.core.gz", st_size=80)
            patcher.fs.create_file("/var/core/portsyncd.1624582977.113.core.gz", st_size=80)
            patcher.fs.create_file("/var/core/python3.1624582800.34567.core.gz", st_size=80)
            ats.handle_core_dump_creation_event()
            assert "sonic_dump_random999.tar.gz" in os.listdir(ats.TS_DIR) 
            assert "sflowmgrd.1624582972.161.core.gz" not in os.listdir(ats.CORE_DUMP_DIR)
            assert "caclmgrd.1624582976.22344.core.gz" in os.listdir(ats.CORE_DUMP_DIR)
            assert "portsyncd.1624582977.113.core.gz" in os.listdir(ats.CORE_DUMP_DIR)
            assert "python3.1624582800.34567.core.gz" in os.listdir(ats.CORE_DUMP_DIR)
    
    def test_core_cleanup_with_cooloff(self):
        RedisHandle.data[ats.CFG_DB] = {ats.AUTO_TS : {ats.CFG_STATE : "enabled", ats.CFG_CORE_USAGE : "20", ats.CFG_COOLOFF : "5"}}
        with Patcher() as patcher:
            patcher.fs.set_disk_usage(1000, path="/var/core/")
            def mock_ts_invoc(cmd):
                cmd_str = " ".join(cmd)
                assert cmd_str == "show techsupport" 
                patcher.fs.create_file("/var/dump/sonic_dump_random999.tar.gz")
                return 0, "", ""
            ats.subprocess_exec = mock_ts_invoc
            patcher.fs.create_file("/var/core/portsyncd.1624582970.113.core.gz", st_size=60)
            patcher.fs.create_file("/var/core/sflowmgrd.1624582972.161.core.gz", st_size=60)
            patcher.fs.create_file("/var/core/caclmgrd.1624582976.22344.core.gz", st_size=60)
            patcher.fs.create_file("/var/core/python3.1624582800.34567.core.gz", st_size=60)
            patcher.fs.create_file("/var/dump/sonic_dump_random998.tar.gz")
            time.sleep(1)
            ats.handle_core_dump_creation_event()
            assert "sonic_dump_random999.tar.gz" not in os.listdir(ats.TS_DIR)
            assert "sonic_dump_random998.tar.gz" in os.listdir(ats.TS_DIR)
            assert "sflowmgrd.1624582972.161.core.gz"  in os.listdir(ats.CORE_DUMP_DIR)
            assert "caclmgrd.1624582976.22344.core.gz" in os.listdir(ats.CORE_DUMP_DIR)
            assert "portsyncd.1624582970.113.core.gz" not in os.listdir(ats.CORE_DUMP_DIR)
            assert "python3.1624582800.34567.core.gz" in os.listdir(ats.CORE_DUMP_DIR)
    
    
    
    