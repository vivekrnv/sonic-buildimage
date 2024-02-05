#!/bin/bash
set -e
UNSIGNED_IMG=$1
OUT_CMS_SIGNATURE=$2
echo "secure upgrade remote signing START"
echo "sign_image_prod params: UNSIGNED_IMG=$UNSIGNED_IMG, OUT_CMS_SIGNATURE=$OUT_CMS_SIGNATURE, SECURE_MODE_FLAG=$SECURE_MODE_FLAG"
if [ ! -f "${UNSIGNED_IMG}" ]; then
    echo "ERROR: UNSIGNED_IMG=${UNSIGNED_IMG} file does not exist"
    exit 1
fi
if [ -z ${OUT_CMS_SIGNATURE} ]; then
    echo "ERROR: OUT_CMS_SIGNATURE=${OUT_CMS_SIGNATURE} is empty"
    exit 1
fi
: "${SECURE_MODE_FLAG:=prod}"
if [[ $SECURE_MODE_FLAG != "staging" && $SECURE_MODE_FLAG != "prod" ]]; then
    echo "ERROR: SECURE_MODE_FLAG=${SECURE_MODE_FLAG} is incorrect, should be prod or staging"
    print_usage
    exit 1
fi
if [[ "${SECURE_MODE_FLAG}" == "prod" ]]; then
    SIGN_FLAG="--prod"
fi
echo "XXX999 this is dev"
echo "INFO: SECURE_MODE_FLAG=${SECURE_MODE_FLAG} & SIGN_FLAG=${SIGN_FLAG} "
echo "XXX0 hostname is: $(hostname)"
DOCKER_INSPECT=$(docker container inspect $(hostname))
echo "XXX1 docker inspect: $DOCKER_INSPECT"
#HOST_BINDS=$($(DOCKER_INSPECT) | jq -c -r .[].HostConfig.Binds)
#echo "XXX2 host binds: $HOST_BINDS"
#A_HOST_BINDS=$($(HOST_BINDS) | jq -r '.[]' )
#echo "XXX3 host binds 2: $A_HOST_BINDS"
#HOST_BIND_GREP=$( $(A_HOST_BINDS) | grep -e ":/sonic_dpu$")
#echo "XXX4 host binds grep : $HOST_BIND_GREP"
HOST_PATH=$(docker container inspect $(hostname) | jq -c -r .[].HostConfig.Binds | jq -r '.[]' | grep -e ":/sonic_dpu$" | cut -d ":" -f1)
echo "XXX5 host path: $HOST_PATH"
SERVER_SIGN_SCRIPT=/opt/nvidia/sonic_sign.sh
# signing with prod server
#${SERVER_SIGN_SCRIPT} --file ${UNSIGNED_IMG} \
#                    --type CMS ${SIGN_FLAG} \
#                    --description 'CMS Signing SONiC bluefield IMG' \
#                    --out-file ${OUT_CMS_SIGNATURE} || exit $? ;
${SERVER_SIGN_SCRIPT} --sandbox ${HOST_PATH}/$(dirname "${UNSIGNED_IMG}") \
                    --file ${UNSIGNED_IMG} \
                    --type CMS --prod \
                    --description 'CMS Signing SONiC bluefield IMG' \
                    --out-file ${OUT_CMS_SIGNATURE} || exit $? ;
echo "secure upgrade remote signing DONE"