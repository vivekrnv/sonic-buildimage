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

	rm -rf /tmp/dkms_patches
	mkdir /tmp/dkms_patches

# Create Applicable patch set
# Get all Hw-mgmt patches
	find $(HW_MGMT_PCH_LOC) -regex ".*patch" -printf "%P\n" | sort > /tmp/series
# Remove Patches that are not applicable
	grep -xvf platform_modules/exclude-patches /tmp/series > /tmp/non_excluded_series
# Remove hw-mgmt Patches that have been modified to suit sonic
	grep -xvf platform_modules/modified-patches /tmp/non_excluded_series > /tmp/non_modified_series
# Remove upstream patches that are already there in sonic-linux version
	grep -xvf platform_modules/upstream-patches /tmp/non_modified_series > /tmp/final_hwmgmt_series
# Apply Modified patches
	find platform_modules/sonic-patches/ -regex ".*patch" -printf "%P\n" | sort > /tmp/mod_series
	cat /tmp/final_hwmgmt_series /tmp/mod_series | sort > /tmp/dkms_patches/final_series

	cp $(HW_MGMT_PCH_LOC)/*.patch /tmp/dkms_patches/
	cp platform_modules/sonic-patches/*.patch /tmp/dkms_patches/

	echo "Patches Applicable: "
	cat /tmp/dkms_patches/final_series

# Sanity Check
	patches=`ls /tmp/dkms_patches/*.patch`
	for s_patch in $(patches)
	do 
		p_name=`basename $(s_patch)`
		if grep -Fxq "$(p_name)" /tmp/dkms_patches/final_series
		then
			echo "$(patch) will be applied"
		else
			echo "ERROR: $(patch) will not be applied"
		fi
	done
	
# Cleanup
	pushd platform_modules
	sudo rm -rf linux-$(BASE_LINUX) /usr/src/hwmgmt-$(MLNX_HW_MANAGEMENT_VERSION)
	sudo rm -rf /var/lib/dkms/hwmgmt/$(MLNX_HW_MANAGEMENT_VERSION)

# Get Linux Source and apply patch set
# TODO: Use the linux-source-deb-package built during sonic-linux-kernel
# wget -nc https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/linux-$(BASE_LINUX).tar.gz
	tar xf linux-$(BASE_LINUX).tar.gz
	pushd linux-$(BASE_LINUX)
	git init
	git add -A
	git commit -m "init"
	stg init
	stg import -s /tmp/dkms_patches/final_series
	popd

#   Validate and construct dkms
	sudo python3 build_dkms.py $(BASE_LINUX) $(MLNX_HW_MANAGEMENT_VERSION) $(CONFIGURED_ARCH) $(KVERSION)

# 	Build the package
	sudo dkms add hwmgmt/$(MLNX_HW_MANAGEMENT_VERSION) 
	sudo dkms build hwmgmt/$(MLNX_HW_MANAGEMENT_VERSION) -k $(KVERSION) -a $(CONFIGURED_ARCH) --verbose
	sudo dkms mkbmdeb hwmgmt/$(MLNX_HW_MANAGEMENT_VERSION) -k $(KVERSION) -a $(CONFIGURED_ARCH)

	sudo mv /var/lib/dkms/hwmgmt/$(MLNX_HW_MANAGEMENT_VERSION)/bmdeb/$(MOD_TARGET) $(DEST)/

	popd