import os
import sys
import time
import pytest
import unittest
import pyfakefs 
from pyfakefs.fake_filesystem_unittest import Patcher
from mock import patch
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
        RedisHandle.data[ats.CFG_DB] = {ats.AUTO_TS : {ats.CFG_STATE : "enabled", ats.CFG_MAX_TS : "2"}} 
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
        