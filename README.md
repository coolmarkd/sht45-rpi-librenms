# SHT42 Data Into LibreNMS

as seen on [my website](https://www.marktoso.com)

Use these files to get your SHT45 sensor data into LibreNMS.

This makes use of LibreNMS's [Rasberry Pi GPIO monitor](https://docs.librenms.org/Extensions/Applications/Raspberry%20Pi%20GPIO%20Monitor/) to bring the data in, which is cool as I have this connected to my Pi and want to continue to use the GPIO.

```shell
sudo cp /etc/snmp/snmpd.conf /etc/snmp/snmpd.conf.bak-sht

sudo apt install php-cli python3-serial snmpd
python3 sht45-trinkey.py raw    # should print temperature/humidity lines

sudo install -m 755 sht45-trinkey.py /usr/local/bin/sht45-trinkey.py
sudo ln -s /usr/local/bin/sht45-trinkey.py /usr/local/bin/sht45-temperature
sudo ln -s /usr/local/bin/sht45-trinkey.py /usr/local/bin/sht45-humidity

# read the Trinkey's serial port
sudo usermod -aG dialout Debian-snmp


sudo wget https://raw.githubusercontent.com/librenms/librenms-agent/master/snmp/rpigpiomonitor.php -O /etc/snmp/rpigpiomonitor.php


sudo install -m 644 rpigpiomonitor.ini /etc/snmp/rpigpiomonitor.ini
sudo install -m 755 rpigpiomonitor-wrapper.sh /etc/snmp/rpigpiomonitor-wrapper.sh


sudo -u Debian-snmp /etc/snmp/rpigpiomonitor-wrapper.sh -validate

echo "extend rpigpiomonitor /etc/snmp/rpigpiomonitor-wrapper.sh" | sudo tee -a /etc/snmp/snmpd.conf

sudo systemctl restart snmpd
```

on Proxmox (normal hw)

```shell

```