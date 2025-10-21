#!/usr/bin/env python


try:
    from sonic_platform_pddf_base.pddf_psu import PddfPsu
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")


class Psu(PddfPsu):
    """PDDF Platform-Specific PSU class"""

    PLATFORM_PSU_CAPACITY = 450

    def __init__(self, index, pddf_data=None, pddf_plugin_data=None):
        PddfPsu.__init__(self, index, pddf_data, pddf_plugin_data)

    # Provide the functions/variables below for which implementation is to be overwritten
    def get_maximum_supplied_power(self):
        """
        Retrieves the maximum supplied power by PSU (or PSU capacity)
        Returns:
            A float number, the maximum power output in Watts.
            e.g. 1200.1
        """
        return float(self.PLATFORM_PSU_CAPACITY)

    def get_power(self):
        """
        Retrieves current energy supplied by PSU

        Returns:
            A float number, the power in watts,
            e.g. 302.6
        """

        # power is returned in micro watts
        return round(float(self.get_voltage()*self.get_current()), 2)

    def get_capacity(self):
        """
        Retrieves the maximum supplied power by PSU (or PSU capacity)
        Returns:
            A float number, the maximum power output in Watts.
            e.g. 1200.1
        """
        return self.get_maximum_supplied_power()

    def get_type(self):
        """
        Gets the type of the PSU

        Returns:
            A string, the type of PSU (AC/DC)
        """
        mfr = self.get_mfr_id()
        model = self.get_model()
        ptype = self.plugin_data['PSU']['valmap']['DEFAULT_TYPE']

        if mfr and model :
            for dev in self.plugin_data['PSU']['psu_support_list']:
                if dev['Manufacturer'] == mfr and dev['Name'] == model:
                    ptype = dev['Type']
                    break


        return ptype