## Mellanox non-upstream linux kernel patches ##

To include non-upstream patches into the sonic-linux image during build time, the directory pointed by EXTERNAL_KERNEL_PATCH_LOC must follow the following structure 

### Directory Structure 

```
EXTERNAL_KERNEL_PATCH_LOC/
       ├──── patches/
             ├── 0001-mlx5-Refactor-module-EEPROM-query.patch.patch
             ├── 0002-mlx5-Implement-get_module_eeprom_by_page.patch.patch
             ├── 0005-mlx5-Add-support-for-DSFP-module-EEPROM-dumps.patch
             ├── .............
       ├──── series.patch
```

  1. It should contain a file named series.patch. This should contain a diff that is applied on the sonic-linux-kernel/patch/series file. The diff should include all the non-upstream patches.
  2. All the patches should be present in the patches folder
  3. Developers should make sure patches apply cleanly over the existing patches present in the src/sonic-linux-kernel .


### Include the non upstream patches while building sonic linux kernel

Set `INCLUDE_EXTERNAL_PATCHES=y` using `SONIC_OVERRIDE_BUILD_VARS` to include these changes before building the kernel.
- Eg: `NOJESSIE=1 NOSTRETCH=1 NOBUSTER=1 make SONIC_OVERRIDE_BUILD_VARS=' INCLUDE_EXTERNAL_PATCHES=y ' target/debs/bullseye/linux-headers-5.10.0-12-2-common_5.10.103-1_all.deb`

### Downloading the non upstream patch tar while building sonic linux kernel

To download a publicly accessible tar of the non-upstream patches with the directory structure explained above, use the `EXTERNAL_KERNEL_PATCH_TAR` variable.
