## Mellanox non-upstream linux kernel patches ##

To include non-upstream patches into the sonic-linux image during build time, this folder must contain a patch archive.

### Structure of the patch archive

  1. The tarball should be gzip compressed i.e. of extension .tar.gz
  2. It should contain a file named series. series should provide an order of which the patches have to be applied
  3. All the patches should be present in the archive in the same folder where series resides.
  4. Developers should make sure patches apply cleanly over the existing patches present in the sonic-linux-kernel/ repo.

#### Example
```
admin@build-server:/sonic-buildimage/platform/mellanox/non-upstream-patches$ tar -tvf patches.tar.gz
drwxr-xr-x vkarri/dip        0 2022-10-07 00:20 ./
-rw-r--r-- vkarri/dip     4865 2022-10-06 22:50 ./mlx5-Implement-get_module_eeprom_by_page.patch
-rw-r--r-- vkarri/dip     1529 2022-10-06 22:48 ./mlx5-Add-support-for-DSFP-module-EEPROM-dumps.patch
-rw-r--r-- vkarri/dip      139 2022-10-07 00:20 ./series
-rw-r--r-- vkarri/dip     4827 2022-10-06 22:47 ./mlx5-Refactor-module-EEPROM-query.patch
```

### Include the archive while building sonic linux kernel

Set `INCLUDE_MLNX_PATCHES=y` using `SONIC_OVERRIDE_BUILD_VARS` to include these changes before building the kernel.
- Eg: `NOJESSIE=1 NOSTRETCH=1 NOBUSTER=1 make SONIC_OVERRIDE_BUILD_VARS=' INCLUDE_MLNX_PATCHES=y ' target/debs/bullseye/linux-headers-5.10.0-12-2-common_5.10.103-1_all.deb`
