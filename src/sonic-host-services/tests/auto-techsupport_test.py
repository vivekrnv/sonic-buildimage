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
    RedisHandle.data[ats.STATE_DB].clear()

class TestTechsupportCreationEvent(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def assert_clean_exit(self, func, *args, **kwargs):
        with pytest.raises(SystemExit) as exc:
            func(*args, **kwargs)
        assert exc.value.code == 0, "{} did not exit with success".format(func.__name__)
    
    def test_spurious_invoc_with_no_state_info(self):
        """ Scenario: Event Notification by the systemd is not because of techsupport dump with No prev state info """
        with Patcher() as patcher:
            patcher.fs.create_dir('/var/dump/')
            self.assert_clean_exit(ats.handle_techsupport_creation_event)
    
    def test_legit_invoc_with_no_state_info(self):
        """ Scenario: Legit Event Notification with no prev state info """
        clear_redis()
        RedisHandle.data[ats.CFG_DB] = {ats.AUTO_TS : {ats.CFG_STATE : "enabled"}} # Enable the Feature
        with Patcher() as patcher:
            patcher.fs.create_file("/var/dump/sonic_dump_random.tar.gz")
            self.assert_clean_exit(ats.handle_techsupport_creation_event)
        print(RedisHandle.data[ats.STATE_DB])
        assert ats.AUTO_TS in RedisHandle.data[ats.STATE_DB], "STATE_DB entry should've been created"
        assert ats.PREV_TS_COUNT in RedisHandle.data[ats.STATE_DB][ats.AUTO_TS], "num_techsupports field should've been created"
        assert int(RedisHandle.data[ats.STATE_DB][ats.AUTO_TS][ats.PREV_TS_COUNT]) == 1, "num_techsupports should be equal to 1"
        assert ats.LAST_TS in RedisHandle.data[ats.STATE_DB][ats.AUTO_TS], "last_techsupport_run field should've been created"
        assert not RedisHandle.data[ats.STATE_DB][ats.AUTO_TS][ats.LAST_TS], "last_techsupport_run should be NULL"
    
    def test_with_state_db_populated(self):
        """ Scenario: State Info is Already Populated, Verify if it is getting updated"""
        clear_redis()
        RedisHandle.data[ats.CFG_DB] = {ats.AUTO_TS : {ats.CFG_STATE : "enabled"}} # Enable the Feature
        print(RedisHandle.data[ats.CFG_DB])
        with Patcher() as patcher:
            patcher.fs.create_file("/var/dump/sonic_dump_random1.tar.gz")
            patcher.fs.create_file("/var/dump/sonic_dump_random2.tar.gz")
            creation_time = str(time.monotonic())
            RedisHandle.data[ats.STATE_DB] = {ats.AUTO_TS : {ats.PREV_TS_COUNT : "2", ats.LAST_TS : creation_time}}
            time.sleep(0.01)
            patcher.fs.create_file("/var/dump/sonic_dump_random3.tar.gz") # Event Trigger
            self.assert_clean_exit(ats.handle_techsupport_creation_event)
        print(RedisHandle.data[ats.STATE_DB])
        assert ats.AUTO_TS in RedisHandle.data[ats.STATE_DB], "STATE_DB entry should not be empty"
        assert ats.PREV_TS_COUNT in RedisHandle.data[ats.STATE_DB][ats.AUTO_TS], "num_techsupports field can't be NULL"
        assert int(RedisHandle.data[ats.STATE_DB][ats.AUTO_TS][ats.PREV_TS_COUNT]) == 3, "num_techsupports should be equal to 3"
        assert ats.LAST_TS in RedisHandle.data[ats.STATE_DB][ats.AUTO_TS], "last_techsupport_run field should've been created"
        assert RedisHandle.data[ats.STATE_DB][ats.AUTO_TS][ats.LAST_TS] != creation_time, "last_techsupport_run should've been updated"
        
    def test_cleanup_process(self):
        """ Scenario: Check TechSupport Cleanup is properly performed """
        clear_redis()
        RedisHandle.data[ats.CFG_DB] = {ats.AUTO_TS : {ats.CFG_STATE : "enabled", ats.CFG_MAX_TS : "2"}} 
        print(RedisHandle.data[ats.CFG_DB])
        with Patcher() as patcher:
            patcher.fs.create_file("/var/dump/sonic_dump_random1.tar.gz")
            patcher.fs.create_file("/var/dump/sonic_dump_random2.tar.gz")
            creation_time = str(time.monotonic())
            RedisHandle.data[ats.STATE_DB] = {ats.AUTO_TS : {ats.PREV_TS_COUNT : "2", ats.LAST_TS : creation_time}}
            time.sleep(0.01)
            patcher.fs.create_file("/var/dump/sonic_dump_random3.tar.gz") # Event Trigger
            self.assert_clean_exit(ats.handle_techsupport_creation_event)
            current_fs = os.listdir(ats.TS_DIR)
            print(current_fs)
            assert len(current_fs) == 2
            assert "sonic_dump_random2.tar.gz" in current_fs
            assert "sonic_dump_random3.tar.gz" in current_fs
            assert "sonic_dump_random1.tar.gz" not in current_fs
        print(RedisHandle.data[ats.STATE_DB])
        assert ats.AUTO_TS in RedisHandle.data[ats.STATE_DB], "STATE_DB entry should not be empty"
        assert ats.PREV_TS_COUNT in RedisHandle.data[ats.STATE_DB][ats.AUTO_TS], "num_techsupports field can't be NULL"
        assert int(RedisHandle.data[ats.STATE_DB][ats.AUTO_TS][ats.PREV_TS_COUNT]) == 2, "num_techsupports value should be updated after cleanup"
        assert ats.LAST_TS in RedisHandle.data[ats.STATE_DB][ats.AUTO_TS], "last_techsupport_run field should've been created"
        assert RedisHandle.data[ats.STATE_DB][ats.AUTO_TS][ats.LAST_TS] != creation_time, "last_techsupport_run should've been updated" 
                       
    def test_no_cleanup(self):
        """ Scenario: Check TechSupport Cleanup is properly performed """
        clear_redis()
        RedisHandle.data[ats.CFG_DB] = {ats.AUTO_TS : {ats.CFG_STATE : "enabled", ats.CFG_MAX_TS : "5"}} 
        print(RedisHandle.data[ats.CFG_DB])
        with Patcher() as patcher:
            patcher.fs.create_file("/var/dump/sonic_dump_random1.tar.gz")
            patcher.fs.create_file("/var/dump/sonic_dump_random2.tar.gz")
            creation_time = str(time.monotonic())
            RedisHandle.data[ats.STATE_DB] = {ats.AUTO_TS : {ats.PREV_TS_COUNT : "2", ats.LAST_TS : creation_time}}
            time.sleep(0.01)
            patcher.fs.create_file("/var/dump/sonic_dump_random3.tar.gz") # Event Trigger
            self.assert_clean_exit(ats.handle_techsupport_creation_event)
            current_fs = os.listdir(ats.TS_DIR)
            print(current_fs)
            assert len(current_fs) == 3
            assert "sonic_dump_random2.tar.gz" in current_fs
            assert "sonic_dump_random3.tar.gz" in current_fs
            assert "sonic_dump_random1.tar.gz" in current_fs
        print(RedisHandle.data[ats.STATE_DB])
        assert ats.AUTO_TS in RedisHandle.data[ats.STATE_DB], "STATE_DB entry should not be empty"
        assert ats.PREV_TS_COUNT in RedisHandle.data[ats.STATE_DB][ats.AUTO_TS], "num_techsupports field can't be NULL"
        assert int(RedisHandle.data[ats.STATE_DB][ats.AUTO_TS][ats.PREV_TS_COUNT]) == 3, "num_techsupports value should be updated"
        assert ats.LAST_TS in RedisHandle.data[ats.STATE_DB][ats.AUTO_TS], "last_techsupport_run field should've been created"
        assert RedisHandle.data[ats.STATE_DB][ats.AUTO_TS][ats.LAST_TS] != creation_time, "last_techsupport_run should've been updated" 