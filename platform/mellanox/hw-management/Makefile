.ONESHELL:
SHELL = /bin/bash

BASE_LINUX = 5.10.43

MAIN_TARGET = hw-management_1.mlnx.$(MLNX_HW_MANAGEMENT_VERSION)_$(CONFIGURED_ARCH).deb
MOD_TARGET = hwmgmt-modules-$(KVERSION)_$(MLNX_HW_MANAGEMENT_VERSION)_$(CONFIGURED_ARCH).deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :

	pushd hw-mgmt
	git stash
	git apply -3 ../*.patch || exit 1
	chmod +x ./debian/rules
	KVERSION=$(KVERSION) dpkg-buildpackage -us -uc -b -rfakeroot -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
	popd

	pushd platform_modules	
	sudo python3 build_modules.py $(BASE_LINUX) $(MLNX_HW_MANAGEMENT_VERSION) $(CONFIGURED_ARCH) $(KVERSION)
	mv /var/lib/dkms/hwmgmt/$(MLNX_HW_MANAGEMENT_VERSION)/bmdeb/$(MOD_TARGET) ../
	popd

	mv $(MAIN_TARGET) $(MOD_TARGET) $(DEST)/
