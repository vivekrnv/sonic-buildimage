#
# psuutil.py
# Platform-specific PSU status interface for SONiC
#
import logging
from sonic_py_common.general import getstatusoutput_noshell, getstatusoutput_noshell_pipe

Z9332F_MAX_PSUS = 2
FRU_PSUL = 11
FRU_PSUR = 12


try:
    from sonic_psu.psu_base import PsuBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


class PsuUtil(PsuBase):
    """Platform-specific PSUutil class"""
    IPMI_PSU1_DATA = ["ipmitool", "raw", "0x04", "0x2d", "0x2f"]
    IPMI_PSU2_DATA = ["ipmitool", "raw", "0x04", "0x2d", "0x39"]
    IPMI_PSU_VOUT = ["ipmitool", "sdr", "get", ""]
    IPMI_PSU_POUT = ["ipmitool", "sdr", "get", ""]
    IPMI_PSU_COUT = ["ipmitool", "sdr", "get", ""]
    IPMI_PSU_FAN_SPEED = ["ipmitool", "sdr", "get", ""]
    IPMI_FRU = ["ipmitool", "fru"]
    IPMI_FRU_DATA = ["ipmitool", "fru", "print", ""]
    awk_cmd = ['awk', '{print substr($0,9,1)}']

    def __init__(self):
        PsuBase.__init__(self)

    def isDockerEnv(self):
        num_docker = open('/proc/self/cgroup', 'r').read().count(":/docker")
        if num_docker > 0:
            return True
        else:
            return False

    def get_psu_vout(self,index):
        try:
            self.IPMI_PSU_VOUT[3] = 'PSU' + str(index) + '_VOut'
            ret_status, ipmi_cmd_ret = getstatusoutput_noshell(self.IPMI_PSU_VOUT)
            if ret_status == 0:
                rdata = ipmi_cmd_ret.splitlines()[3].split(':')[1].split(' ')[1]
                return rdata

        except Exception:
            logging.error('Failed to execute : %s'%(' '.join(self.IPMI_PSU_VOUT)))
    
    def get_psu_cout(self,index):
        try:
            self.IPMI_PSU_COUT[3] = 'PSU' + str(index) + 'POut'
            ret_status, ipmi_cmd_ret = getstatusoutput_noshell(self.IPMI_PSU_COUT)
            if ret_status == 0:
                rdata = ipmi_cmd_ret.splitlines()[3].split(':')[1].split(' ')[1]
                return rdata

        except Exception:
            logging.error('Failed to execute : %s'%(' '.join(self.IPMI_PSU_COUT)))

    def get_psu_pout(self,index):
        try:
            self.IPMI_PSU_POUT[3] = 'PSU' + str(index) + '_COut'
            ret_status, ipmi_cmd_ret = getstatusoutput_noshell(self.IPMI_PSU_POUT)
            if ret_status == 0:
                rdata = ipmi_cmd_ret.splitlines()[3].split(':')[1].split(' ')[1]
                return rdata

        except Exception:
            logging.error('Failed to execute : %s'%(' '.join(self.IPMI_PSU_POUT)))

    def get_psu_fan_speed(self,index):
        try:
            self.IPMI_PSU_FAN_SPEED[3] = 'PSU' + str(index) + '_Fan'
            ret_status, ipmi_cmd_ret = getstatusoutput_noshell(self.IPMI_PSU_FAN_SPEED)
            if ret_status == 0:
                rdata = ipmi_cmd_ret.splitlines()[3].split(':')[1].split(' ')[1]
                return rdata

        except Exception:
            logging.error('Failed to execute : %s'%(' '.join(self.IPMI_PSU_FAN_SPEED)))


    #Fetch FRU Data for given fruid
    def get_psu_airflow(self, index):
        if index == 1:
            fru_id = 'FRU_PSUL'
        else:
            fru_id = 'FRU_PSUR'

        ret_status, ipmi_cmd_ret = getstatusoutput_noshell(self.IPMI_FRU)
        if ret_status:
            logging.error('Failed to execute ipmitool: '+ self.IPMI_FRU)

        found_fru = False
        for line in ipmi_cmd_ret.splitlines():
            if line.startswith('FRU Device Description') and fru_id in line.split(':')[1] :
                found_fru = True
            if found_fru and line.startswith(' Board Product '):
                return ' B2F' if 'PS/IO' in line else ' F2B'
        return ''

    # Read FRU info
    def get_fru_info(self,fru_id,reg_name):
        output = None
        Found = False
        try:
            self.IPMI_FRU_DATA[3] = str(fru_id)
            status, ipmi_fru_list = getstatusoutput_noshell(self.IPMI_FRU_DATA)
            if status == 0:
                for item in ipmi_fru_list.split("\n"):
                    if reg_name == item.split(':')[0].strip(' '):
                        output = item.strip()
                        output = output.split(':')[1]
                        Found = True
                        break;

                if not Found:
                    logging.error('\nFailed to fetch: ' +  reg_name + ' sensor ')

                return output
        except Exception:
            logging.error('Failed to execute:' + ipmi_fru_list)

    def get_num_psus(self):
        """
        Retrieves the number of PSUs available on the device
        :return: An integer, the number of PSUs available on the device
         """
        Z9332F_MAX_PSUS = 2
        return Z9332F_MAX_PSUS

    def get_psu_status(self, index):
        """
        Retrieves the oprational status of power supply unit (PSU) defined
                by index <index>
        :param index: An integer, index of the PSU of which to query status
        :return: Boolean, True if PSU is operating properly, False if PSU is\
        faulty
        """
        psu_status = '0'
        ipmi_cmd = ''
        if index == 1:
            ipmi_cmd = self.IPMI_PSU1_DATA
        elif index == 2:
            ipmi_cmd = self.IPMI_PSU2_DATA
        else:
            logging.error("Invalid PSU number:" + index)

        if ipmi_cmd != '':
            cmd_status, psu_status = getstatusoutput_noshell_pipe(ipmi_cmd, self.awk_cmd)
        if cmd_status:
            logging.error('Failed to execute ipmitool')
        return (not int(psu_status, 16) > 1)

    def get_psu_presence(self, index):
        """
        Retrieves the presence status of power supply unit (PSU) defined
                by index <index>
        :param index: An integer, index of the PSU of which to query status
        :return: Boolean, True if PSU is plugged, False if not
        """
        
        psu_status = '0'
        ipmi_cmd = ''
        if index == 1:
            ipmi_cmd = self.IPMI_PSU1_DATA
        elif index == 2:
            ipmi_cmd = self.IPMI_PSU2_DATA
        else:
            logging.error("Invalid PSU number:" + index)

        if ipmi_cmd != '':
            cmd_status, psu_status = getstatusoutput_noshell_pipe(ipmi_cmd, self.awk_cmd)
        if cmd_status:
            logging.error('Failed to execute ipmitool')

        return (int(psu_status, 16) & 1)

    def get_output_voltage(self, index):
        if index is None:
            return 0.0
        psuvoltage=self.get_psu_vout(index)
        return float(psuvoltage.strip())

    def get_output_current(self, index):
        if index is None:
            return 0.0
        psucurrent=self.get_psu_cout(index)
        return float(psucurrent.strip())

    def get_output_power(self, index):
        if index is None:
            return 0.0
        psupower=self.get_psu_pout(index)
        return float(psupower.strip())

    def get_fan_rpm(self, index, fan_idx):
        if index is None:
            return 0
        fanrpm=self.get_psu_fan_speed(index)
        return int(fanrpm.strip())

    def get_serial(self, index):
        if index is None:
            return None
        if index == 1:
            fru_id = FRU_PSUL
        else:
            fru_id = FRU_PSUR

        return self.get_fru_info(fru_id,'Board Serial')

    def get_model(self, index):
        if index is None:
            return None
        if index == 1:
            fru_id = FRU_PSUL
        else:
            fru_id = FRU_PSUR

        return self.get_fru_info(fru_id,'Board Part Number')

    def get_mfr_id(self, index):
        if index is None:
            return None
        if index == 1:
            fru_id = FRU_PSUL
        else:
            fru_id = FRU_PSUR

        return self.get_fru_info(fru_id,'Board Mfg')
        
    def get_direction(self, index):
        if index is None:
            return None

        direction=self.get_psu_airflow(index).strip()
        if direction == 'B2F':
            return "INTAKE"
        elif direction == 'F2B':
            return "EXHAUST"
        else:
            return None
