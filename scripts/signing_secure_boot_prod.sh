#!/bin/bash
# This script is signing boot components: shim, mmx, grub, kernel and kernel modules in production env.
## Enable debug output for script & exit code when failing occurs
set -x -e
print_usage() {
    cat <<EOF
$0: Usage
$0 -a <CONFIGURED_ARCH> -r <FS_ROOT> -l <LINUX_KERNEL_VERSION> -o <OUTPUT_SEC_BOOT_DIR> -m <SECURE_MODE> -c <VAULT_ROLE_CREDS>
EOF
}
clean_file() {
    if [ -f $1 ]; then
        echo "clean old file named: $1"
        echo "sudo rm -f $1"
        sudo sudo rm -f $1
    fi
}
while getopts 'a:r:l:o:m:c:hv' flag; do
  case "${flag}" in
    a) CONFIGURED_ARCH="${OPTARG}" ;;
    r) FS_ROOT="${OPTARG}" ;;
    l) LINUX_KERNEL_VERSION="${OPTARG}" ;;
    o) OUTPUT_SEC_BOOT_DIR="${OPTARG}" ;;
    m) SECURE_MODE="${OPTARG}" ;;
    c) VAULT_ROLE_CREDS="${OPTARG}" ;;
    v) VERBOSE='true' ;;
    h) print_usage
       exit 1 ;;
  esac
done
if [ $OPTIND -eq 1 ]; then echo "no options were pass"; print_usage; exit 1 ;fi
if [ -z ${CONFIGURED_ARCH} ]; then
    echo "ERROR: CONFIGURED_ARCH=${CONFIGURED_ARCH} is empty"
    print_usage
    exit 1
fi
if [[ $SECURE_MODE != "prod" ]]; then
    echo "ERROR: SECURE_MODE=${SECURE_MODE} is incorrect, should be prod"
    print_usage
    exit 1
fi
: "${SECURE_MODE_FLAG:=prod}"
if [[ $SECURE_MODE_FLAG != "staging" && $SECURE_MODE_FLAG != "prod" ]]; then
    echo "ERROR: SECURE_MODE_FLAG=${SECURE_MODE_FLAG} is incorrect, should be prod or staging"
    print_usage
    exit 1
fi
if [[ $SECURE_MODE == "prod" ]]; then
    SIGN_FLAG="--prod"
fi
if [ -z ${FS_ROOT} ]; then
    echo "ERROR: FS_ROOT=${FS_ROOT} is empty"
    print_usage
    exit 1
fi
if [ -z ${LINUX_KERNEL_VERSION} ]; then
    echo "ERROR: LINUX_KERNEL_VERSION=${LINUX_KERNEL_VERSION} is empty"
    print_usage
    exit 1
fi
if [ ! -d "$OUTPUT_SEC_BOOT_DIR" ]; then
    echo "ERROR: OUTPUT_SEC_BOOT_DIR=$OUTPUT_SEC_BOOT_DIR folder does not exist"
    print_usage
    exit 1
fi
if [ -z ${VAULT_ROLE_CREDS} ]; then
    echo "ERROR: VAULT_ROLE_CREDS=${VAULT_ROLE_CREDS} is empty"
    print_usage
    exit 1
fi
echo "$0 Production signing EFI files and Kernel Modules start ..."
# export creds for remote sign server connection
export VAULT_ROLE_CREDS=$VAULT_ROLE_CREDS
# ######################################
# Signing EFI files: mm, shim, grub
# #####################################
SERVER_SIGN_SCRIPT=/opt/nvidia/sonic_sign.sh
HOST_PATH=$(docker container inspect $(hostname) | jq -c -r .[].HostConfig.Binds | jq -r '.[]' | grep -e ":/sonic$" | cut -d ":" -f1)
echo "HOST_PATH is ${HOST_PATH}"
echo "signing mm, shim and grub step"
efi_file_list=$(sudo find ${FS_ROOT} -name "*.efi")
for efi in $efi_file_list
do
    # grep filename from full path
    efi_filename=$(echo $efi | grep -o '[^/]*$')
    if echo $efi_filename | grep -e "shim" -e "grub" -e "mm"; then
        clean_file ${efi}-signed
        echo "signing efi file - full path: ${efi} filename: ${efi_filename}"
        # signing with prod server
        ${SERVER_SIGN_SCRIPT} --sandbox $(dirname "${HOST_PATH}/${efi}") \
                            --file ${efi} \
                            --type EFI $SIGN_FLAG\
                            --description 'Signing linux kernel file ${efi}' \
                            --out-file ${efi}-signed || exit $? ;
        # cp shim & mmx signed files to boot directory in the fs.
        sudo cp ${efi}-signed $OUTPUT_SEC_BOOT_DIR/${efi_filename}
    fi
done
echo "signing mm, shim and grub step DONE"
######################
## vmlinuz signing
######################
echo "signing vmlinuz step"
CURR_VMLINUZ=$FS_ROOT/boot/vmlinuz-${LINUX_KERNEL_VERSION}-${CONFIGURED_ARCH}
# clean old files
clean_file ${CURR_VMLINUZ}-signed
echo "signing ${CURR_VMLINUZ} from prod server.."
${SERVER_SIGN_SCRIPT} --sandbox "${HOST_PATH}/${FS_ROOT}/boot/" \
                    --file ${CURR_VMLINUZ} \
                    --type EFI $SIGN_FLAG\
                    --description 'Signing linux kernel file ${efi}' \
                    --out-file ${CURR_VMLINUZ}-signed || exit $? ;
# rename signed vmlinuz with the name vmlinuz without signed suffix
sudo mv ${CURR_VMLINUZ}-signed ${CURR_VMLINUZ}
echo "signing vmlinuz step DONE"
#########################
# Kernel Modules signing
#########################
echo "signing all the kernel modules step"
# Create tar file for sending to signing server
tar -cvf kernel_modules.tar.gz $(find ${FS_ROOT} -name "*.ko") ;
${SERVER_SIGN_SCRIPT} --sandbox "${HOST_PATH}" \
                      --file kernel_modules.tar.gz --type KERNEL $SIGN_FLAG \
                      --description 'Signing kernel modules' \
                      --out-file kernel_modules_signed.tar.gz \
                      || exit $?
tar -xvf kernel_modules_signed.tar.gz --directory ./
echo "echo rm kernel_modules.tar.gz"
rm kernel_modules.tar.gz
echo "echo rm kernel_modules_signed.tar.gz"
rm kernel_modules_signed.tar.gz
echo "signing all the kernel modules step DONE"
echo "$0 signing EFI files and Kernel Modules from prod server DONE"