# SHT42 Data Into LibreNMS

as seen on [my website](https://www.marktoso.com)

Use these files to get your SHT45 sensor data into LibreNMS.

This makes use of LibreNMS's [Rasberry Pi GPIO monitor](https://docs.librenms.org/Extensions/Applications/Raspberry%20Pi%20GPIO%20Monitor/) to bring the data in, which is cool as I have this connected to my Pi and want to continue to use the GPIO.

```shell
sudo cp /etc/snmp/snmpd.conf /etc/snmp/snmpd.conf.bak-sht
sudo raspi-config nonint do_i2c 0

sudo apt install php-cli python3-smbus2 snmpd i2c-tools
i2cdetect -y 1            # should show 44


sudo install -m 755 sht45.py /usr/local/bin/sht45.py
sudo ln -s /usr/local/bin/sht45.py /usr/local/bin/sht45-temperature
sudo ln -s /usr/local/bin/sht45.py /usr/local/bin/sht45-humidity

# read i2c
sudo usermod -aG i2c Debian-snmp


sudo wget https://raw.githubusercontent.com/librenms/librenms-agent/master/snmp/rpigpiomonitor.php -O /etc/snmp/rpigpiomonitor.php


sudo install -m 644 rpigpiomonitor.ini /etc/snmp/rpigpiomonitor.ini
sudo install -m 755 rpigpiomonitor-wrapper.sh /etc/snmp/rpigpiomonitor-wrapper.sh


sudo -u Debian-snmp /etc/snmp/rpigpiomonitor-wrapper.sh -validate

sudo echo "extend rpigpiomonitor /etc/snmp/rpigpiomonitor-wrapper.sh" >> /etc/snmp/snmpd.conf

sudo systemctl restart snmpd
```
