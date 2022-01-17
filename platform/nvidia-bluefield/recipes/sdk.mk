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

DOCA_SDK_BASE_PATH = $(PLATFORM_PATH)/sdk-src/sonic-bluefield-packages/bin

# Place here URL where SDK sources exist
DOCA_SDK_SOURCE_BASE_URL =

ifneq ($(DOCA_SDK_SOURCE_BASE_URL), )
SDK_FROM_SRC = y
else
SDK_FROM_SRC = n
endif

### RDMA
RDMA_CORE_VER=33.1-1

RDMA_CORE = rdma-core_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
$(RDMA_CORE)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/rdma
$(RDMA_CORE)_DEPENDS = $(LIBNL3_DEV) $(LIBNL_ROUTE3_DEV)
$(RDMA_CORE)_RDEPENDS = $(LIBNL3) $(ETHTOOL)
RDMA_CORE_DBGSYM = rdma-core-dbgsym_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
ifeq ($(SDK_FROM_SRC),y)
$(eval $(call add_extra_package,$(RDMA_CORE),$(RDMA_CORE_DBGSYM)))
endif

# Derived debs from rdma-core
IB_VERBS_PROV = ibverbs-providers_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
IB_VERBS_PROV_DBGSYM = ibverbs-providers-dbgsym_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
$(IB_VERBS_PROV)_DEPENDS = $(IB_VERBS)
$(IB_VERBS_PROV)_RDEPENDS = $(IB_VERBS)
$(IB_VERBS_PROV_DBGSYM)_DEPENDS = $(IB_VERBS_DBGSYM)
$(IB_VERBS_PROV_DBGSYM)_RDEPENDS = $(IB_VERBS_DBGSYM)
ifeq ($(SDK_FROM_SRC),y)
$(eval $(call add_extra_package,$(RDMA_CORE),$(IB_VERBS_PROV)))
$(eval $(call add_extra_package,$(RDMA_CORE),$(IB_VERBS_PROV_DBGSYM)))
endif

IB_VERBS = libibverbs1_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
IB_VERBS_DBGSYM = libibverbs1-dbgsym_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
IB_VERBS_DEV = libibverbs-dev_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
$(IB_VERBS)_DEPENDS = $(LIBNL3_DEV) $(LIBNL_ROUTE3_DEV)
$(IB_VERBS_DBGSYM)_DEPENDS = $(LIBNL3_DEV) $(LIBNL_ROUTE3_DEV)
$(IB_VERBS_DEV)_DEPENDS = $(IB_VERBS_PROV)
ifeq ($(SDK_FROM_SRC),y)
$(eval $(call add_extra_package,$(RDMA_CORE),$(IB_VERBS)))
$(eval $(call add_extra_package,$(RDMA_CORE),$(IB_VERBS_DBGSYM)))
$(eval $(call add_extra_package,$(RDMA_CORE),$(IB_VERBS_DEV)))
endif

IB_UMAD = libibumad3_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
IB_UMAD_DBGSYM = libibumad3-dbgsym_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
IB_UMAD_DEV = libibumad-dev_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
ifeq ($(SDK_FROM_SRC),y)
$(eval $(call add_extra_package,$(RDMA_CORE),$(IB_UMAD)))
$(eval $(call add_extra_package,$(RDMA_CORE),$(IB_UMAD_DBGSYM)))
$(eval $(call add_extra_package,$(RDMA_CORE),$(IB_UMAD_DEV)))
endif

RDMA_CM = librdmacm1_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
RDMA_CM_DBGSYM = librdmacm1-dbgsym_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
RDMA_CM_DEV = librdmacm-dev_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
ifeq ($(SDK_FROM_SRC),y)
$(eval $(call add_extra_package,$(RDMA_CORE),$(RDMA_CM)))
$(eval $(call add_extra_package,$(RDMA_CORE),$(RDMA_CM_DBGSYM)))
$(eval $(call add_extra_package,$(RDMA_CORE),$(RDMA_CM_DEV)))
endif

IB_MAD = libibmad5_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
$(IB_MAD)_DEPENDS = $(IB_UMAD)
$(IB_MAD)_RDEPENDS = $(IB_UMAD)
IB_MAD_DBGSYM = libibmad5-dbgsym_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
$(IB_MAD_DBGSYM)_DEPENDS = $(IB_UMAD_DBGSYM)
$(IB_MAD_DBGSYM)_RDEPENDS = $(IB_UMAD_DBGSYM)
IB_MAD_DEV = libibmad-dev_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
ifeq ($(SDK_FROM_SRC),y)
$(eval $(call add_extra_package,$(RDMA_CORE),$(IB_MAD)))
$(eval $(call add_extra_package,$(RDMA_CORE),$(IB_MAD_DBGSYM)))
$(eval $(call add_extra_package,$(RDMA_CORE),$(IB_MAD_DEV)))
endif

IB_NET_DISC = libibnetdisc5_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
IB_NET_DISC_DBGSYM = libibnetdisc5-dbgsym_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
IB_NET_DISC_DEV = libibnetdisc-dev_${RDMA_CORE_VER}_${CONFIGURED_ARCH}.deb
ifeq ($(SDK_FROM_SRC),y)
$(eval $(call add_extra_package,$(RDMA_CORE),$(IB_NET_DISC)))
$(eval $(call add_extra_package,$(RDMA_CORE),$(IB_NET_DISC_DBGSYM)))
$(eval $(call add_extra_package,$(RDMA_CORE),$(IB_NET_DISC_DEV)))
endif

RDMA_CORE_DEBS += $(IB_VERBS_PROV) $(IB_VERBS) $(RDMA_CM) \
				  $(IB_UMAD) $(IB_MAD) $(IB_NET_DISC)

RDMA_CORE_DBGSYM_DEBS += $(RDMA_CORE_DBGSYM) $(IB_VERBS_PROV_DBGSYM) \
				 $(IB_VERBS_DBGSYM) $(IB_UMAD_DBGSYM) $(RDMA_CM_DBGSYM) \
				 $(IB_MAD_DBGSYM) $(IB_NET_DISC_DBGSYM)

RDMA_CORE_DEV_DEBS += $(IB_VERBS_DEV) $(IB_UMAD_DEV) $(RDMA_CM_DEV) $(IB_MAD_DEV) $(IB_NET_DISC_DEV)

export RDMA_CORE RDMA_CORE_DEBS RDMA_CORE_DBGSYM_DEBS RDMA_CORE_DEV_DEBS

### DPDK with Hardware Steering

DPDK_VER=21.02-1mlnx1

DPDK_HWS = dpdk.hws_${DPDK_VER}_${CONFIGURED_ARCH}.deb
$(DPDK_HWS)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/dpdk
$(DPDK_HWS)_DEPENDS = $(IB_VERBS_PROV) $(IB_VERBS_DEV) $(RDMA_CORE) $(IB_MAD) $(IB_NET_DISC) $(RDMA_CM)
$(DPDK_HWS)_RDEPENDS = $(IB_VERBS_PROV) $(IB_VERBS) $(RDMA_CORE) $(IB_MAD) $(IB_NET_DISC) $(RDMA_CM)

DPDK_HWS_DEV = dpdk.hws-dev_${DPDK_VER}_${CONFIGURED_ARCH}.deb
$(DPDK_HWS_DEV)_DEPENDS = $(IB_VERBS_PROV) $(IB_VERBS_DEV) $(RDMA_CORE) $(IB_MAD) $(IB_NET_DISC) $(RDMA_CM)
$(DPDK_HWS_DEV)_RDEPENDS = $(IB_VERBS_PROV) $(IB_VERBS) $(RDMA_CORE) $(IB_MAD) $(IB_NET_DISC) $(RDMA_CM)
ifeq ($(SDK_FROM_SRC),y)
$(eval $(call add_extra_package,$(DPDK_HWS),$(DPDK_HWS_DEV)))
endif

export DPDK_HWS DPDK_HWS_DEV

## DOCA_DPDK

DOCA_DPDK_VER=1.5-1mlnx1

DOCA_DPDK = doca-dpdk_${DOCA_DPDK_VER}_${CONFIGURED_ARCH}.deb
$(DOCA_DPDK)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/doca-dpdk
$(DOCA_DPDK)_DEPENDS = $(DPDK_HWS_DEV)
$(DOCA_DPDK)_RDEPENDS = $(DPDK_HWS)

DOCA_DPDK_DEV = doca-dpdk-dev_${DOCA_DPDK_VER}_${CONFIGURED_ARCH}.deb
ifeq ($(SDK_FROM_SRC),y)
$(eval $(call add_derived_package,$(DOCA_DPDK),$(DOCA_DPDK_DEV)))
endif

export DOCA_DPDK DOCA_DPDK_DEV

## SDN Appliance 

SDN_APPL_VER=1.5-1mlnx1
SDN_APPL = sdn-appliance_${SDN_APPL_VER}_${CONFIGURED_ARCH}.deb
$(SDN_APPL)_SRC_PATH = $(PLATFORM_PATH)/sdk-src/sdn
$(SDN_APPL)_DEPENDS = $(DOCA_DPDK_DEV) 
$(SDN_APPL)_RDEPENDS = $(DOCA_DPDK)

SDN_APPL_DEV = sdn-appliance-dev_${DOCA_DPDK_VER}_${CONFIGURED_ARCH}.deb
ifeq ($(SDK_FROM_SRC),y)
$(eval $(call add_derived_package,$(SDN_APPL),$(SDN_APPL_DEV)))
endif

export SDN_APPL SDN_APPL_DEV

define make_path
	$(1)_PATH = $(DOCA_SDK_BASE_PATH)

endef

$(eval $(foreach deb,$(RDMA_CORE) $(RDMA_CORE_DEBS),$(call make_path,$(deb))))
$(eval $(foreach deb,$(DPDK_HWS) $(DOCA_DPDK) $(SDN_APPL),$(call make_path,$(deb))))

ifeq ($(SDK_FROM_SRC), y)
SONIC_MAKE_DEBS += $(RDMA_CORE) $(DPDK_HWS) $(DOCA_DPDK) $(SDN_APPL)
else
$(SDN_APPL)_DERIVED_DEBS += $(RDMA_CORE) $(RDMA_CORE_DEBS) $(DPDK_HWS) $(DOCA_DPDK)
SONIC_COPY_DEBS += $(RDMA_CORE) $(RDMA_CORE_DEBS) $(DPDK_HWS) $(DOCA_DPDK) $(SDN_APPL)
endif

doca-sdk-packages: $(addprefix $(DEBS_PATH)/, $(RDMA_CORE) $(DPDK_HWS) $(DOCA_DPDK) $(SDN_APPL))

SONIC_PHONY_TARGETS += doca-sdk-packages
