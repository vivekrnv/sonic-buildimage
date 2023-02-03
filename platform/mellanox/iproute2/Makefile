SHELL = /bin/bash
.ONESHELL:
.SHELLFLAGS += -e

MAIN_TARGET = iproute2_mlnx_$(IPROUTE2_MLNX_VERSION)_$(CONFIGURED_ARCH).deb

$(addprefix $(DEST)/, $(MAIN_TARGET)): $(DEST)/% :
	# Remove any stale files
	rm -rf iproute2-$(IPROUTE2_MLNX_VERSION)

	wget -O iproute2_$(IPROUTE2_MLNX_VERSION).orig.tar.xz http://deb.debian.org/debian/pool/main/i/iproute2/iproute2_$(IPROUTE2_MLNX_VERSION).orig.tar.xz
	wget -O iproute2_$(IPROUTE2_MLNX_VERSION_FULL).dsc http://deb.debian.org/debian/pool/main/i/iproute2/iproute2_$(IPROUTE2_MLNX_VERSION_FULL).dsc
	wget -O iproute2_$(IPROUTE2_MLNX_VERSION_FULL).debian.tar.xz http://deb.debian.org/debian/pool/main/i/iproute2/iproute2_$(IPROUTE2_MLNX_VERSION_FULL).debian.tar.xz
	dpkg-source -x iproute2_$(IPROUTE2_MLNX_VERSION_FULL).dsc

	pushd iproute2-$(IPROUTE2_MLNX_VERSION)

	# Create a git repository here for stg to apply patches
	git init
	git add -f *
	git commit -qm "initial commit"

	# Apply Patches
	stg init
	stg import -s ../patch/series

	dpkg-buildpackage -us -uc -b -j$(SONIC_CONFIG_MAKE_JOBS) --admindir $(SONIC_DPKG_ADMINDIR)

	popd

	mv $* $(DEST)/