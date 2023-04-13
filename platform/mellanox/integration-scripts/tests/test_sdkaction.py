import sys
from unittest import mock, TestCase
from pyfakefs.fake_filesystem_unittest import Patcher
sys.path.append('../')
from sdk_kernel_patches import *

MOCK_SLK_SERIES = """\
# Trtnetlink-catch-EOPNOTSUPP-errors.patch

# Mellanox patches for 5.10
###-> mellanox_sdk-start
###-> mellanox_sdk-end

###-> mellanox_hw_mgmt-start
0001-i2c-mlxcpld-Update-module-license.patch
###-> mellanox_hw_mgmt-end
"""

MOCK_SLK_SERIES_1 = """\
# Trtnetlink-catch-EOPNOTSUPP-errors.patch

# Mellanox patches for 5.10
###-> mellanox_sdk-start
0001-psample-Encapsulate-packet-metadata-in-a-struct.patch
###-> mellanox_sdk-end

###-> mellanox_hw_mgmt-start
0001-i2c-mlxcpld-Update-module-license.patch
###-> mellanox_hw_mgmt-end
"""

MOCK_FINAL_SLK_SERIES = """\
# Trtnetlink-catch-EOPNOTSUPP-errors.patch

# Mellanox patches for 5.10
###-> mellanox_sdk-start
0001-psample-Encapsulate-packet-metadata-in-a-struct.patch
0002-psample-new-attr-tc-tc-occ-latency.patch
###-> mellanox_sdk-end

###-> mellanox_hw_mgmt-start
0001-i2c-mlxcpld-Update-module-license.patch
###-> mellanox_hw_mgmt-end
"""

MOCK_SLK_VER = "5.10.104"

def mock_sdk_args():
    with mock.patch("sys.argv", ["sdk_kernel_patches.py",
                                "--sonic_kernel_ver", MOCK_SLK_VER,
                                "--patches", "/tmp",
                                "--build_root", "/sonic"]):
        parser = create_parser()
        return parser.parse_args()


def check_lists(exp, rec):
    print(" ------- Expected ----------- ")
    print("".join(exp))
    print(" ------- Recieved ----------- ")
    print("".join(rec))
    if len(exp) != len(rec):
        return False
    for i in range(0, len(exp)):
        if exp[i] != rec[i]:
            return False
    return True

class TestSDKAction(TestCase):
    def setUp(self):
        self.action = SDKAction(mock_sdk_args())
        self.action.check()

    def tearDown(self):
        Data.new_series = list()
        Data.new_patches = list()
        Data.old_series = list()
        Data.old_patches = list()
        Data.k_dir = ""
        Data.i_sdk_start = -1
        Data.i_sdk_end = -1

    def test_get_kernel_dir(self):
        with Patcher() as patcher:
            dir_ = os.path.join(KERNEL_BACKPORTS, MOCK_SLK_VER)
            patcher.fs.create_file(os.path.join("/tmp", dir_))
            self.action.get_kernel_dir()
            assert dir_ == Data.k_dir
            assert "/tmp/kernel_backports/5.10.0" != Data.k_dir
        
        with Patcher() as patcher:
            dir_ = os.path.join(KERNEL_BACKPORTS, "5.10.0")
            patcher.fs.create_file(os.path.join("/tmp", dir_))
            self.action.get_kernel_dir()
            assert dir_ == Data.k_dir
            assert "/tmp/kernel_backports/5.10.140" != Data.k_dir
        
    def test_find_sdk_patches(self):
        Data.old_series = MOCK_SLK_SERIES.splitlines(True)
        self.action.find_sdk_patches()
        assert "mellanox_sdk-start" in Data.old_series[Data.i_sdk_start]
        assert "mellanox_sdk-end" in Data.old_series[Data.i_sdk_end]
        assert not Data.old_patches

        Data.old_series = MOCK_SLK_SERIES_1.splitlines(True)
        self.action.find_sdk_patches()
        assert "mellanox_sdk-start" in Data.old_series[Data.i_sdk_start]
        assert "mellanox_sdk-end" in Data.old_series[Data.i_sdk_end]
        assert len(Data.old_patches) == 1
        assert Data.old_patches[-1] == "0001-psample-Encapsulate-packet-metadata-in-a-struct.patch"

    def test_get_new_patches(self):
        with Patcher() as patcher:
            root_dir = "/tmp/kernel_backports/5.10.0/"
            patcher.fs.create_file(os.path.join(root_dir, "0001-psample-Encapsulate-packet-metadata-in-a-struct.patch"))
            patcher.fs.create_file(os.path.join(root_dir, "0002-psample-new-attr-tc-tc-occ-latency.patch"))
            self.action.get_kernel_dir()
            self.action.get_new_patches()
            assert len(Data.new_patches) == 2
            assert Data.new_patches[0] == "0001-psample-Encapsulate-packet-metadata-in-a-struct.patch"
            assert Data.new_patches[1] == "0002-psample-new-attr-tc-tc-occ-latency.patch"
    
    def test_process_patches_1(self):
        Data.old_series = MOCK_SLK_SERIES.splitlines(True)
        with Patcher() as patcher:
            root_dir = "/tmp/kernel_backports/5.10.0/"
            patcher.fs.create_file(os.path.join(root_dir, "0001-psample-Encapsulate-packet-metadata-in-a-struct.patch"))
            patcher.fs.create_file(os.path.join(root_dir, "0002-psample-new-attr-tc-tc-occ-latency.patch"))
            self.action.find_sdk_patches()
            self.action.get_kernel_dir()
            self.action.get_new_patches()
            assert not Data.old_patches
            (update_required, patches_add, patches_del) = self.action.process_patches()
            assert update_required == True
            assert len(patches_add) == 2
            assert patches_add[0] == "0001-psample-Encapsulate-packet-metadata-in-a-struct.patch"
            assert patches_add[1] == "0002-psample-new-attr-tc-tc-occ-latency.patch"
            assert check_lists(MOCK_FINAL_SLK_SERIES.splitlines(True), Data.new_series)
            assert len(patches_del) == 0
    
    def test_process_patches_2(self):
        Data.old_series = MOCK_SLK_SERIES_1.splitlines(True)
        with Patcher() as patcher:
            root_dir = "/tmp/kernel_backports/5.10.0/"
            patcher.fs.create_file(os.path.join(root_dir, "0001-psample-Encapsulate-packet-metadata-in-a-struct.patch"))
            patcher.fs.create_file(os.path.join(root_dir, "0002-psample-new-attr-tc-tc-occ-latency.patch"))
            self.action.find_sdk_patches()
            self.action.get_kernel_dir()
            self.action.get_new_patches()
            (update_required, patches_add, patches_del) = self.action.process_patches()
            assert update_required == True
            assert len(patches_add) == 2
            assert patches_add[0] == "0001-psample-Encapsulate-packet-metadata-in-a-struct.patch"
            assert patches_add[1] == "0002-psample-new-attr-tc-tc-occ-latency.patch"
            assert check_lists(MOCK_FINAL_SLK_SERIES.splitlines(True), Data.new_series)
            assert len(patches_del) == 1
            assert patches_del[0] == "0001-psample-Encapsulate-packet-metadata-in-a-struct.patch"
