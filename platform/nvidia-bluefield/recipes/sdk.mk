#
# Copyright (c) 2022 NVIDIA CORPORATION & AFFILIATES.
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
SDK_VERSION = 0.1-RC19

ifneq ($(SDK_SOURCE_BASE_URL), )
SDK_FROM_SRC = y
SDK_SOURCE_URL = $(SDK_SOURCE_BASE_URL)/$(subst -,/,$(SDK_VERSION))
else
SDK_FROM_SRC = n
endif

export SDK_VERSION SDK_SOURCE_URL

SDK_DEBS =

# OFED and derived packages

OFED_VER_SHORT = 5.6
OFED_VER_FULL = $(OFED_VER_SHORT)-1.0.3.1

OFED_KERNEL = mlnx-ofed-kernel-modules-$(KVERSION)_$(OFED_VER_SHORT)_$(BUILD_ARCH).deb
$(OFED_KERNEL)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/ofed
$(OFED_KERNEL)_DEPENDS = $(LINUX_HEADERS) $(LINUX_HEADERS_COMMON)

export OFED_VER_SHORT OFED_VER_FULL OFED_KERNEL

OFED_DERIVED_DEBS =

export OFED_DERIVED_DEBS

SDK_DEBS += $(OFED_KERNEL) $(OFED_DERIVED_DEBS)

# RDMA and derived packages

RDMA_CORE_VER=56mlnx40-1

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
IB_VERBS_DBGSYM = libibverbs1-dbg_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb

IB_UMAD = libibumad3_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
IB_UMAD_DEV = libibumad-dev_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
IB_UMAD_DBGSYM = libibumad3-dbg_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb

$(eval $(call add_derived_package,$(RDMA_CORE),$(IB_VERBS_PROV)))
$(eval $(call add_derived_package,$(RDMA_CORE),$(IB_VERBS)))
$(eval $(call add_derived_package,$(RDMA_CORE),$(IB_VERBS_DEV)))
$(eval $(call add_derived_package,$(RDMA_CORE),$(IB_UMAD)))
$(eval $(call add_derived_package,$(RDMA_CORE),$(IB_UMAD_DEV)))

ifeq ($(SDK_FROM_SRC),y)
$(eval $(call add_derived_package,$(RDMA_CORE),$(RDMA_CORE_DBGSYM)))
$(eval $(call add_derived_package,$(RDMA_CORE),$(IB_VERBS_PROV_DBGSYM)))
$(eval $(call add_derived_package,$(RDMA_CORE),$(IB_VERBS_DBGSYM)))
$(eval $(call add_derived_package,$(RDMA_CORE),$(IB_UMAD_DBGSYM)))
endif

export RDMA_CORE RDMA_CORE_DBGSYM
export IB_VERBS IB_VERBS_DEV IB_VERBS_DBGSYM
export IB_VERBS_PROV IB_VERBS_PROV_DBGSYM
export IB_UMAD IB_UMAD_DEV IB_UMAD_DBGSYM

RDMA_CORE_DERIVED_DEBS = $(RDMA_CORE_DBGSYM) \
		$(IB_VERBS) \
		$(IB_VERBS_DEV) \
		$(IB_VERBS_DBGSYM) \
		$(IB_VERBS_PROV) \
		$(IB_VERBS_PROV_DBGSYM) \
		$(IB_UMAD) \
		$(IB_UMAD_DEV) \
		$(IB_UMAD_DBGSYM)

export RDMA_CORE_DERIVED_DEBS

SDK_DEBS += $(RDMA_CORE) $(RDMA_CORE_DERIVED_DEBS)

# DPDK and derived packages

DPDK_VER=20.11.0-4.1.9

DPDK = mlnx-dpdk_${DPDK_VER}_${CONFIGURED_ARCH}.deb
$(DPDK)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/dpdk
$(DPDK)_RDEPENDS = $(IB_VERBS_PROV) $(IB_VERBS)

DPDK_DEV = mlnx-dpdk-dev_${DPDK_VER}_${CONFIGURED_ARCH}.deb
$(DPDK)_DEPENDS = $(RDMA_CORE) $(IB_VERBS_PROV) $(IB_VERBS) $(IB_VERBS_DEV)
$(DPDK_DEV)_RDEPENDS = $(DPDK)

$(eval $(call add_derived_package,$(DPDK),$(DPDK_DEV)))

export DPDK DPDK_DEV

DPDK_DERIVED_DEBS = $(DPDK_DEV)
export DPDK_DERIVED_DEBS

SDK_DEBS += $(DPDK) $(DPDK_DERIVED_DEBS)

# Collectx

COLLECTX_CLXAPI = collectx-1.9.1-5158675.aarch64_debian-11.2-clxapi.deb
$(COLLECTX_CLXAPI)_RDEPENDS = $(IB_UMAD)

SDK_DEBS += $(COLLECTX_CLXAPI)

# RXP compiler and derived packages

RXPCOMPILER_VER = 22.05.1

RXPCOMPILER = rxp-compiler_$(RXPCOMPILER_VER)_arm64.deb
$(RXPCOMPILER)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/rxp-compiler
LIBRXPCOMPILER_DEV = librxpcompiler-dev_$(RXPCOMPILER_VER)_arm64.deb

$(eval $(call add_derived_package,$(RXPCOMPILER),$(LIBRXPCOMPILER_DEV)))

export RXPCOMPILER LIBRXPCOMPILER_DEV

RXPCOMPILER_DERIVED_DEBS = $(LIBRXPCOMPILER_DEV)
export RXPCOMPILER_DERIVED_DEBS

SDK_DEBS += $(RXPCOMPILER) $(RXPCOMPILER_DERIVED_DEBS)

# UCX and derived packages

UCX_VER = 1.13.0-1.56103

UCX = ucx_$(UCX_VER)_arm64.deb
$(UCX)_DEPENDS = $(IB_VERBS_PROV) $(IB_VERBS)
$(UCX)_RDEPENDS = $(IB_VERBS_PROV) $(IB_VERBS)
$(UCX)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/ucx

export UCX_VER UCX

SDK_DEBS += $(UCX)

# GRPC and derived packages

LIBGRPC_VER = 1.39.0-1

LIBGRPC_DEV = libgrpc-dev_$(LIBGRPC_VER)_arm64.deb
$(LIBGRPC_DEV)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/grpc
LIBGRPC_DBG = libgrpc-dev-dbgsym_$(LIBGRPC_VER)_arm64.deb

$(eval $(call add_derived_package,$(LIBGRPC_DEV),$(LIBGRPC_DBG)))

export LIBGRPC_DEV LIBGRPC_DBG LIBGRPC_VER

LIBGRPC_DERIVED_DEBS = $(LIBGRPC_DBG)
export LIBGRPC_DERIVED_DEBS

SDK_DEBS += $(LIBGRPC_DEV) $(LIBGRPC_DERIVED_DEBS)

# DOCA and derived packages

DOCA_VERSION = 1.4.0047
DOCA_DEB_VERSION = $(DOCA_VERSION)-1

DOCA_LIBS = doca-libs_${DOCA_DEB_VERSION}_${CONFIGURED_ARCH}.deb
$(DOCA_LIBS)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/doca
$(DOCA_LIBS)_RDEPENDS = $(DPDK) $(COLLECTX_CLXAPI) $(RXPCOMPILER) $(LIBRXPCOMPILER_DEV) $(UCX) $(LIBGRPC_DEV)
$(DOCA_LIBS)_DEPENDS = $(COLLECTX_CLXAPI) $(RXPCOMPILER) $(LIBRXPCOMPILER_DEV) $(UCX) $(DPDK_DEV) $(LIBGRPC_DEV)
DOCA_LIBS_DEV = libdoca-libs-dev_${DOCA_DEB_VERSION}_${CONFIGURED_ARCH}.deb
DOCA_LIBS_DBG = doca-libs-dbgsym_${DOCA_DEB_VERSION}_${CONFIGURED_ARCH}.deb

$(eval $(call add_derived_package,$(DOCA_LIBS),$(DOCA_LIBS_DEV)))
$(eval $(call add_derived_package,$(DOCA_LIBS),$(DOCA_LIBS_DBG)))

export DOCA_LIBS DOCA_LIBS_DEV DOCA_LIBS_DBG

DOCA_LIBS_DERIVED_DEBS = $(DOCA_LIBS_DEV) $(DOCA_LIBS_DBG)
export DOCA_LIBS_DERIVED_DEBS

SDK_DEBS += $(DOCA_LIBS) $(DOCA_LIBS_DERIVED_DEBS)

# SDN Appliance

SDN_APPL_VER=1.5-1mlnx1
SDN_APPL = sdn-appliance_${SDN_APPL_VER}_${CONFIGURED_ARCH}.deb
$(SDN_APPL)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/sdn
$(SDN_APPL)_RDEPENDS = $(DOCA_LIBS)
$(SDN_APPL)_DEPENDS = $(DOCA_LIBS_DEV) $(DOCA_LIBS) $(DPDK_DEV) 

$(eval $(call add_derived_package,$(SDN_APPL),$(SDN_APPL_DEV)))

SDN_APPL_DEV = sdn-appliance-dev_${SDN_APPL_VER}_${CONFIGURED_ARCH}.deb

export SDN_APPL SDN_APPL_DEV

SDN_APPL_DERIVED_DEBS = $(SDN_APPL_DEV)
export SDN_APPL_DERIVED_DEBS

SDK_DEBS += $(SDN_APPL) $(SDN_APPL_DERIVED_DEBS)

define make_path
	$(1)_PATH = $(SDK_BASE_PATH)

endef

$(eval $(foreach deb, $(SDK_DEBS),$(call make_path,$(deb))))

SONIC_COPY_DEBS += $(COLLECTX_CLXAPI)

ifeq ($(SDK_FROM_SRC), y)
SONIC_MAKE_DEBS += $(OFED_KERNEL) $(UCX) $(RXPCOMPILER) $(RDMA_CORE) $(DPDK) $(LIBGRPC_DEV) $(DOCA_LIBS) $(SDN_APPL) $(SDN_APPL_DEV)
else
SONIC_COPY_DEBS += $(OFED_KERNEL) $(UCX) $(RXPCOMPILER) $(RDMA_CORE) $(DPDK) $(LIBGRPC_DEV) $(DOCA_LIBS) $(SDN_APPL) $(SDN_APPL_DEV)
endif

sdk-packages: $(addprefix $(DEBS_PATH)/, $(OFED_KERNEL) $(UCX) $(RXPCOMPILER) $(COLLECTX_CLXAPI) $(RDMA_CORE) $(DPDK) $(LIBGRPC_DEV) $(DOCA_LIBS) $(SDN_APPL) $(SDN_APPL_DEV))

SONIC_PHONY_TARGETS += sdk-packages
