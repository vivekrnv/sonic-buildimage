#
# Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES.
# Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

SDK_BASE_PATH = $(PLATFORM_PATH)/sdk-src/sonic-bluefield-packages/bin

# Place here URL where SDK sources exist
SDK_SOURCE_BASE_URL =
SDK_VERSION = 24.1-RC3

SDK_COLLECTX_URL = https://linux.mellanox.com/public/repo/doca/1.5.2/debian12/aarch64/

SDK_GH_BASE_URL = https://github.com/Mellanox/sonic-bluefield-packages/releases/download/dpu-sdk-$(SDK_VERSION)-$(BLDENV)/

define make_url_sdk
	$(1)_URL="$(SDK_GH_BASE_URL)/$(1)"

endef

define get_sdk_version_file_gh
	$(shell wget --quiet $(1) -O $(2))

endef

ifneq ($(SDK_SOURCE_BASE_URL), )
SDK_FROM_SRC = y
SDK_SOURCE_URL = $(SDK_SOURCE_BASE_URL)/$(subst -,/,$(SDK_VERSION))
SDK_VERSIONS_FILE = $(PLATFORM_PATH)/sdk-src/VERSIONS
$(eval $(call get_sdk_version_file_gh, "$(SDK_SOURCE_URL)/VERSIONS_FOR_SONIC_BUILD", $(SDK_VERSIONS_FILE)))
else
SDK_FROM_SRC = n
SDK_VERSIONS_FILE = $(PLATFORM_PATH)/sdk-src/VERSIONS
$(eval $(call get_sdk_version_file_gh, "$(SDK_GH_BASE_URL)/VERSIONS_FOR_SONIC_BUILD", $(SDK_VERSIONS_FILE)))
endif

export SDK_VERSION SDK_SOURCE_URL

define get_sdk_package_version_short
$(shell $(PLATFORM_PATH)/recipes/get_sdk_package_version.sh -s $(SDK_VERSIONS_FILE) $(1))
endef

define get_sdk_package_version_full
$(shell $(PLATFORM_PATH)/recipes/get_sdk_package_version.sh $(SDK_VERSIONS_FILE) $(1))
endef

SDK_DEBS =
SDK_SRC_TARGETS =
SDK_ONLINE_TARGETS =

# OFED and derived packages

OFED_VER_SHORT = $(call get_sdk_package_version_short,"ofed")
OFED_VER_FULL = $(call get_sdk_package_version_full,"ofed")
OFED_KERNEL_VER_SHORT = $(call get_sdk_package_version_short,"mlnx-ofed-kernel")
OFED_KERNEL_VER_FULL = $(call get_sdk_package_version_full,"mlnx-ofed-kernel")
MLNX_TOOLS_VER = $(call get_sdk_package_version_full,"mlnx-tools")

MLNX_TOOLS = mlnx-tools_$(MLNX_TOOLS_VER)_arm64.deb
$(MLNX_TOOLS)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/ofed

OFED_KERNEL_UTILS = mlnx-ofed-kernel-utils_$(OFED_KERNEL_VER_FULL)-1_arm64.deb

$(eval $(call add_derived_package,$(MLNX_TOOLS),$(OFED_KERNEL_UTILS)))

OFED_KERNEL_DKMS = mlnx-ofed-kernel-dkms_$(OFED_KERNEL_VER_SHORT)-1_all.deb
$(OFED_KERNEL_DKMS)_DEPENDS = $(OFED_KERNEL_UTILS)

$(eval $(call add_derived_package,$(MLNX_TOOLS),$(OFED_KERNEL_DKMS)))

OFED_KERNEL = mlnx-ofed-kernel-modules-$(KVERSION)_$(OFED_KERNEL_VER_SHORT)_$(BUILD_ARCH).deb
$(OFED_KERNEL)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/ofed
$(OFED_KERNEL)_DEPENDS = $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)

ifeq ($(SDK_FROM_SRC), y)
$(OFED_KERNEL)_DEPENDS += $(OFED_KERNEL_DKMS)
endif

export OFED_VER_SHORT OFED_VER_FULL OFED_KERNEL OFED_KERNEL_UTILS OFED_KERNEL_VER_FULL MLNX_TOOLS OFED_KERNEL_DKMS

SDK_DEBS += $(OFED_KERNEL) $(MLNX_TOOLS) $(OFED_KERNEL_UTILS)
SDK_SRC_TARGETS += $(OFED_KERNEL) $(MLNX_TOOLS)

# MLNX iproute2
MLNX_IPROUTE2_VER = $(call get_sdk_package_version_full,"mlnx-iproute2")

MLNX_IPROUTE2 = mlnx-iproute2_$(MLNX_IPROUTE2_VER)_arm64.deb
$(MLNX_IPROUTE2)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/mlnx-iproute2

export MLNX_IPROUTE2_VER MLNX_IPROUTE2

MLNX_IPROUTE2_DERIVED_DEBS = 

export MLNX_IPROUTE2_DERIVED_DEBS

SDK_DEBS += $(MLNX_IPROUTE2) $(MLNX_IPROUTE2_DERIVED_DEBS)
SDK_SRC_TARGETS += $(MLNX_IPROUTE2)

# RDMA and derived packages

RDMA_CORE_VER = $(call get_sdk_package_version_full,"rdma-core")
RDMA_CORE = rdma-core_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
$(RDMA_CORE)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/rdma
$(RDMA_CORE)_RDEPENDS = $(LIBNL3)
$(RDMA_CORE)_DEPENDS = $(LIBNL3_DEV) $(LIBNL_ROUTE3_DEV)
RDMA_CORE_DBGSYM = rdma-core-dbgsym_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb

IB_VERBS_PROV = ibverbs-providers_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
$(IB_VERBS_PROV)_DEPENDS = $(LIBNL3_DEV) $(LIBNL_ROUTE3_DEV)
IB_VERBS_PROV_DBGSYM = ibverbs-providers-dbgsym_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb

IB_VERBS = libibverbs1_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
$(IB_VERBS)_DEPENDS = $(LIBNL3_DEV) $(LIBNL_ROUTE3_DEV)
IB_VERBS_DEV = libibverbs-dev_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
$(IB_VERBS_DEV)_DEPENDS = $(IB_VERBS) $(IB_VERBS_PROV)
IB_VERBS_DBGSYM = libibverbs1-dbg_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb

IB_UMAD = libibumad3_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
IB_UMAD_DEV = libibumad-dev_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
IB_UMAD_DBGSYM = libibumad3-dbg_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb

RDMACM = librdmacm1_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
RDMACM_DEV = librdmacm-dev_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
$(RDMACM_DEV)_DEPENDS = $(RDMACM) $(IB_VERBS_DEV)
RDMACM_DBGSYM = librdmacm1-dbg_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb

$(eval $(call add_derived_package,$(RDMA_CORE),$(IB_VERBS_PROV)))
$(eval $(call add_derived_package,$(RDMA_CORE),$(IB_VERBS)))
$(eval $(call add_derived_package,$(RDMA_CORE),$(IB_VERBS_DEV)))
$(eval $(call add_derived_package,$(RDMA_CORE),$(IB_UMAD)))
$(eval $(call add_derived_package,$(RDMA_CORE),$(IB_UMAD_DEV)))
$(eval $(call add_derived_package,$(RDMA_CORE),$(RDMACM)))
$(eval $(call add_derived_package,$(RDMA_CORE),$(RDMACM_DEV)))

ifeq ($(SDK_FROM_SRC),y)
$(eval $(call add_derived_package,$(RDMA_CORE),$(RDMA_CORE_DBGSYM)))
$(eval $(call add_derived_package,$(RDMA_CORE),$(IB_VERBS_PROV_DBGSYM)))
$(eval $(call add_derived_package,$(RDMA_CORE),$(IB_VERBS_DBGSYM)))
$(eval $(call add_derived_package,$(RDMA_CORE),$(IB_UMAD_DBGSYM)))
$(eval $(call add_derived_package,$(RDMA_CORE),$(RDMACM_DBGSYM)))
endif

export RDMA_CORE RDMA_CORE_DBGSYM
export IB_VERBS IB_VERBS_DEV IB_VERBS_DBGSYM
export IB_VERBS_PROV IB_VERBS_PROV_DBGSYM
export IB_UMAD IB_UMAD_DEV IB_UMAD_DBGSYM
export RDMACM RDMACM_DEV RDMACM_DBGSYM

RDMA_CORE_DERIVED_DEBS = $(RDMA_CORE_DBGSYM) \
		$(IB_VERBS) \
		$(IB_VERBS_DEV) \
		$(IB_VERBS_DBGSYM) \
		$(IB_VERBS_PROV) \
		$(IB_VERBS_PROV_DBGSYM) \
		$(IB_UMAD) \
		$(IB_UMAD_DEV) \
		$(IB_UMAD_DBGSYM) \
		$(RDMACM) \
		$(RDMACM_DEV) \
		$(RDMACM_DBGSYM)

export RDMA_CORE_DERIVED_DEBS

SDK_DEBS += $(RDMA_CORE) $(RDMA_CORE_DERIVED_DEBS)
SDK_SRC_TARGETS += $(RDMA_CORE)

# FlexIO

#FLEXIO_VER = $(call get_sdk_package_version_full,"flexio")
#
#FLEXIO = flexio_$(FLEXIO_VER)_arm64.deb
#$(FLEXIO)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/flexio
#$(FLEXIO)_DEPENDS = $(IB_VERBS_PROV) $(IB_VERBS) $(IB_VERBS_DEV)
#$(FLEXIO)_RDEPENDS = $(IB_VERBS_PROV) $(IB_VERBS) $(IB_VERBS_DEV)
#
#export FLEXIO_VER FLEXIO

SDK_DEBS += $(FLEXIO)
SDK_SRC_TARGETS += $(FLEXIO)

# DPDK and derived packages

DPDK_VER = $(call get_sdk_package_version_full,"dpdk")

DPDK = mlnx-dpdk_${DPDK_VER}_${CONFIGURED_ARCH}.deb
$(DPDK)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/dpdk
$(DPDK)_DEPENDS = $(FLEXIO)
$(DPDK)_RDEPENDS = $(FLEXIO) $(IB_VERBS_PROV) $(IB_VERBS) $(IB_VERBS_DEV)

DPDK_DEV = mlnx-dpdk-dev_${DPDK_VER}_${CONFIGURED_ARCH}.deb
$(DPDK)_DEPENDS = $(RDMA_CORE) $(IB_VERBS_PROV) $(IB_VERBS) $(IB_VERBS_DEV) $(FLEXIO)
$(DPDK_DEV)_RDEPENDS = $(DPDK) $(FLEXIO)

$(eval $(call add_derived_package,$(DPDK),$(DPDK_DEV)))

export DPDK DPDK_DEV

DPDK_DERIVED_DEBS = $(DPDK_DEV)
export DPDK_DERIVED_DEBS

SDK_DEBS += $(DPDK) $(DPDK_DERIVED_DEBS)
SDK_SRC_TARGETS += $(DPDK)

# Collectx

COLLECTX_CLXAPI = collectx_1.14.3-9642347-debian12.1-aarch64-clxapi.deb
$(COLLECTX_CLXAPI)_URL = $(SDK_COLLECTX_URL)/collectx_1.14.3-9642347-debian12.1-aarch64-clxapi.deb
$(COLLECTX_CLXAPI)_RDEPENDS = $(IB_UMAD)

COLLECTX_CLXAPI_DEV = collectx_1.14.3-9642347-debian12.1-aarch64-clxapidev.deb
$(COLLECTX_CLXAPI_DEV)_URL = $(SDK_COLLECTX_URL)/collectx_1.14.3-9642347-debian12.1-aarch64-clxapidev.deb
$(COLLECTX_CLXAPI_DEV)_DEPENDS = $(COLLECTX_CLXAPI)
$(COLLECTX_CLXAPI_DEV)_RDEPENDS = $(IB_UMAD)

SDK_DEBS += $(COLLECTX_CLXAPI) $(COLLECTX_CLXAPI_DEV)
SDK_ONLINE_TARGETS += $(COLLECTX_CLXAPI) $(COLLECTX_CLXAPI_DEV)

# RXP compiler and derived packages

RXPCOMPILER_VER = $(call get_sdk_package_version_full,"rxp-tools")

RXPCOMPILER = rxp-compiler_$(RXPCOMPILER_VER)_arm64.deb
$(RXPCOMPILER)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/rxp-compiler
LIBRXPCOMPILER_DEV = librxpcompiler-dev_$(RXPCOMPILER_VER)_arm64.deb

$(eval $(call add_derived_package,$(RXPCOMPILER),$(LIBRXPCOMPILER_DEV)))

export RXPCOMPILER LIBRXPCOMPILER_DEV

RXPCOMPILER_DERIVED_DEBS = $(LIBRXPCOMPILER_DEV)
export RXPCOMPILER_DERIVED_DEBS

SDK_DEBS += $(RXPCOMPILER) $(RXPCOMPILER_DERIVED_DEBS)
SDK_SRC_TARGETS += $(RXPCOMPILER)

# UCX and derived packages

UCX_VER = $(call get_sdk_package_version_full,"ucx")

UCX = ucx_$(UCX_VER)_arm64.deb
$(UCX)_DEPENDS = $(IB_VERBS_PROV) $(IB_VERBS) $(IB_VERBS_DEV) $(RDMACM) $(RDMACM_DEV)
$(UCX)_RDEPENDS = $(IB_VERBS_PROV) $(IB_VERBS)
$(UCX)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/ucx

export UCX_VER UCX

SDK_DEBS += $(UCX)
SDK_SRC_TARGETS += $(UCX)

# GRPC and derived packages

LIBGRPC_VER = $(call get_sdk_package_version_full,"grpc")

LIBGRPC_DEV = libgrpc-dev_$(LIBGRPC_VER)_arm64.deb
$(LIBGRPC_DEV)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/grpc
LIBGRPC_DBG = libgrpc-dev-dbgsym_$(LIBGRPC_VER)_arm64.deb

$(eval $(call add_derived_package,$(LIBGRPC_DEV),$(LIBGRPC_DBG)))

export LIBGRPC_DEV LIBGRPC_DBG LIBGRPC_VER

LIBGRPC_DERIVED_DEBS = $(LIBGRPC_DBG)
export LIBGRPC_DERIVED_DEBS

SDK_DEBS += $(LIBGRPC_DEV) $(LIBGRPC_DERIVED_DEBS)
SDK_SRC_TARGETS += $(LIBGRPC_DEV)

# DOCA and derived packages

DOCA_VERSION = $(call get_sdk_package_version_full,"doca")
DOCA_DEB_VERSION = $(DOCA_VERSION)-1

DOCA_LIBS = doca-libs_${DOCA_DEB_VERSION}_${CONFIGURED_ARCH}.deb
$(DOCA_LIBS)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/doca
$(DOCA_LIBS)_RDEPENDS = $(DPDK) $(COLLECTX_CLXAPI) $(RXPCOMPILER) $(LIBRXPCOMPILER_DEV) $(UCX) $(LIBGRPC_DEV) $(FLEXIO)
$(DOCA_LIBS)_DEPENDS = $(COLLECTX_CLXAPI) $(COLLECTX_CLXAPI_DEV) $(RXPCOMPILER) $(LIBRXPCOMPILER_DEV) $(UCX) $(DPDK_DEV) $(LIBGRPC_DEV) $(FLEXIO)
DOCA_LIBS_DEV = libdoca-libs-dev_${DOCA_DEB_VERSION}_${CONFIGURED_ARCH}.deb
DOCA_LIBS_DBG = doca-libs-dbgsym_${DOCA_DEB_VERSION}_${CONFIGURED_ARCH}.deb

$(eval $(call add_derived_package,$(DOCA_LIBS),$(DOCA_LIBS_DEV)))
$(eval $(call add_derived_package,$(DOCA_LIBS),$(DOCA_LIBS_DBG)))

export DOCA_LIBS DOCA_LIBS_DEV DOCA_LIBS_DBG

DOCA_LIBS_DERIVED_DEBS = $(DOCA_LIBS_DEV) $(DOCA_LIBS_DBG)
export DOCA_LIBS_DERIVED_DEBS

SDK_DEBS += $(DOCA_LIBS) $(DOCA_LIBS_DERIVED_DEBS)
SDK_SRC_TARGETS += $(DOCA_LIBS)

# SDN Appliance

SDN_APPL_VER=$(call get_sdk_package_version_full,"nasa")
SDN_APPL = sdn-appliance_${SDN_APPL_VER}_${CONFIGURED_ARCH}.deb
$(SDN_APPL)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/sdn
$(SDN_APPL)_RDEPENDS = $(DOCA_LIBS) $(FLEXIO) $(MLNX_TOOLS) $(OFED_KERNEL_UTILS) $(MLNX_IPROUTE2)
$(SDN_APPL)_DEPENDS = $(DOCA_LIBS_DEV) $(DOCA_LIBS) $(DPDK_DEV) $(FLEXIO) $(MLNX_TOOLS) $(OFED_KERNEL_UTILS)

export SDN_APPL

SDN_APPL_DERIVED_DEBS =
export SDN_APPL_DERIVED_DEBS

SDK_DEBS += $(SDN_APPL) $(SDN_APPL_DERIVED_DEBS)
SDK_SRC_TARGETS += $(SDN_APPL)

ifeq ($(SDK_FROM_SRC), y)
SONIC_MAKE_DEBS += $(SDK_SRC_TARGETS)
SONIC_ONLINE_DEBS += $(SDK_ONLINE_TARGETS)
else
$(eval $(foreach deb,$(SDK_SRC_TARGETS) $(SDK_ONLINE_TARGETS) $(SDK_DEBS),$(call make_url_sdk,$(deb))))
SONIC_ONLINE_DEBS += $(SDK_SRC_TARGETS) $(SDK_ONLINE_TARGETS)
endif

SDK_PACKAGES = $(OFED_KERNEL) $(OFED_KERNEL_UTILS) $(MLNX_IPROUTE2) $(SDK_ONLINE_TARGETS) $(SDK_SRC_TARGETS)

sdk-packages: $(addprefix $(DEBS_PATH)/, $(SDK_PACKAGES))

SONIC_PHONY_TARGETS += sdk-packages
