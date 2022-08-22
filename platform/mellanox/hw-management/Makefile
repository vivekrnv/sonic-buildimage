.ONESHELL:
SHELL = /bin/bash

BASE_LINUX = 5.10.103

MAIN_TARGET = hw-management_1.mlnx.$(MLNX_HW_MANAGEMENT_VERSION)_$(CONFIGURED_ARCH).deb
MOD_TARGET = hwmgmt-modules-$(KVERSION)_$(MLNX_HW_MANAGEMENT_VERSION)_$(CONFIGURED_ARCH).deb
HW_MGMT_PCH_LOC = hw-mgmt/recipes-kernel/linux/linux-5.10

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :

	pushd hw-mgmt
	git stash
	git apply -3 ../*.patch || exit 1
	chmod +x ./debian/rules
	KVERSION=$(KVERSION) dpkg-buildpackage -us -uc -b -rfakeroot -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)
	popd

	mv $(MAIN_TARGET) $(DEST)/


$(addprefix $(DEST)/, $(MOD_TARGET)): $(DEST)/% :

#   Create Applicable patch set
	find $(HW_MGMT_PCH_LOC) -regex ".*patch" -printf "%P\n" | sort > /tmp/series
	grep -xvf platform_modules/exclude-patches /tmp/series > /tmp/non_excluded_series
	grep -xvf platform_modules/upstream-patches /tmp/non_excluded_series > $(HW_MGMT_PCH_LOC)/series
	echo "Patches Applicable: "
	cat $(HW_MGMT_PCH_LOC)/series
	
#   Cleanup
	pushd platform_modules
	sudo rm -rf linux-$(BASE_LINUX) /usr/src/hwmgmt-$(MLNX_HW_MANAGEMENT_VERSION)
	sudo rm -rf /var/lib/dkms/hwmgmt/$(MLNX_HW_MANAGEMENT_VERSION)

#   Get Linux Source and apply patch set
#   TODO: Use the linux-source-deb-package built during sonic-linux-kernel
#	wget -nc https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/linux-$(BASE_LINUX).tar.gz
	tar xf linux-$(BASE_LINUX).tar.gz
	pushd linux-$(BASE_LINUX)
	git init
	git add -A
	git commit -m "init"
	stg init
	stg import -s ../../$(HW_MGMT_PCH_LOC)/series
	popd

#   Validate and construct dkms
	sudo python3 build_dkms.py $(BASE_LINUX) $(MLNX_HW_MANAGEMENT_VERSION) $(CONFIGURED_ARCH) $(KVERSION)

# 	Build the package
	sudo dkms add hwmgmt/$(MLNX_HW_MANAGEMENT_VERSION) 
	sudo dkms build hwmgmt/$(MLNX_HW_MANAGEMENT_VERSION) -k $(KVERSION) -a $(CONFIGURED_ARCH) --verbose
	sudo dkms mkbmdeb hwmgmt/$(MLNX_HW_MANAGEMENT_VERSION) -k $(KVERSION) -a $(CONFIGURED_ARCH)

	sudo mv /var/lib/dkms/hwmgmt/$(MLNX_HW_MANAGEMENT_VERSION)/bmdeb/$(MOD_TARGET) $(DEST)/

	popd