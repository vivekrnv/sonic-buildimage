# docker image for GNMI agent

DOCKER_GNMI_STEM = docker-sonic-gnmi
DOCKER_GNMI = $(DOCKER_GNMI_STEM).gz
DOCKER_GNMI_DBG = $(DOCKER_GNMI_STEM)-$(DBG_IMAGE_MARK).gz

$(DOCKER_GNMI)_PATH = $(DOCKERS_PATH)/$(DOCKER_GNMI_STEM)

$(DOCKER_GNMI)_DEPENDS += $(SONIC_MGMT_COMMON)
$(DOCKER_GNMI)_DEPENDS += $(SONIC_TELEMETRY)
$(DOCKER_GNMI)_DBG_DEPENDS = $($(DOCKER_CONFIG_ENGINE_BULLSEYE)_DBG_DEPENDS)

$(DOCKER_GNMI)_LOAD_DOCKERS += $(DOCKER_CONFIG_ENGINE_BULLSEYE)

$(DOCKER_GNMI)_VERSION = 1.0.0
$(DOCKER_GNMI)_PACKAGE_NAME = gnmi

$(DOCKER_GNMI)_DBG_IMAGE_PACKAGES = $($(DOCKER_CONFIG_ENGINE_BULLSEYE)_DBG_IMAGE_PACKAGES)

SONIC_DOCKER_IMAGES += $(DOCKER_GNMI)
SONIC_BULLSEYE_DOCKERS += $(DOCKER_GNMI)
ifeq ($(INCLUDE_SYSTEM_GNMI), y)
SONIC_INSTALL_DOCKER_IMAGES += $(DOCKER_GNMI)
endif

SONIC_DOCKER_DBG_IMAGES += $(DOCKER_GNMI_DBG)
SONIC_BULLSEYE_DBG_DOCKERS += $(DOCKER_GNMI_DBG)
ifeq ($(INCLUDE_SYSTEM_GNMI), y)
SONIC_INSTALL_DOCKER_DBG_IMAGES += $(DOCKER_GNMI_DBG)
endif

$(DOCKER_GNMI)_CONTAINER_NAME = gnmi
$(DOCKER_GNMI)_RUN_OPT += -t
$(DOCKER_GNMI)_RUN_OPT += -v /etc/sonic:/etc/sonic:ro
$(DOCKER_GNMI)_RUN_OPT += -v /etc/timezone:/etc/timezone:ro
$(DOCKER_GNMI)_RUN_OPT += -v /var/run/dbus:/var/run/dbus:rw

$(DOCKER_GNMI)_FILES += $(SUPERVISOR_PROC_EXIT_LISTENER_SCRIPT)
$(DOCKER_GNMI)_BASE_IMAGE_FILES += monit_gnmi:/etc/monit/conf.d
