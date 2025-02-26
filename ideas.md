# Clear storage card
# Firmware updates for Nanometrics equipment
# Firmware updates for Kinemetrics equipment
# In depth checks for device health, beyond what can be gotten from SNMP
    - memory card status

Useful commands:
"uptime" - prints uptime stats
"/usr/bin/nanometrics/cf_flag status" - prints CF card status
"snmpstatus" - needs at least one param
"df" - prints disk usage for all drives

For a script that needs to reboot and continue after reboot:
    Break into 2 scripts, pre-boot.sh and post-boot.sh. Use a while loop with a 5 sec delay to
    attempt reconnection, then run and delete or rename post-boot.sh.

Known bugs/improvements:
Alternative way to get IP info:
# wget -qO- https://rachel.ess.washington.edu/netbox/export_csv.php?model=titan-sma >> hostlist.txt
