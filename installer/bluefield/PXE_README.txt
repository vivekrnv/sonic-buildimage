""" Setup PXE Network Installer for Bluefield """
1) vendor-class-identifier option of the DHCP request coming from a bluefield2 will be equal to BF2Client.
2) Add the corresponding line to DHCP conf
   if substring (option vendor-class-identifier, 0, 9) = "BF2Client" {
      filename "grubnetaa64.efi";
   }
3) Extract the tar file. Eg: tar -xvzf <tar_file> .
4) Please place the individual files in the expected locations. For Eg:
   a) The above DHCP configuration expects grub-efi binary to be in tftp-root
   b) grub.cfg is expected in grub/ directory
   c) Location of Image & initramfs can be somewhere in the tftp-root directory, but update the grub.cfg appropriately 
5) Doesn't support Secure Boot
