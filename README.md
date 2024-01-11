# Battery emulator for inverter control over CAN bus

This repository contains an addon for enabling communications with an inverer CAN bus that emulates a standard battery, including Pylontech and other batteries that use a similar protocol.

This addon is still work in progress, so use at your own risk. Reporting incorrect battery settings can be very detrimental to your batteries, or worse.

Currently, battery current, voltage, and SOC are reported using user-configurable MQTT topics. I use a [Victron SmartShunt](https://www.amazon.com/Victron-SmartShunt-500AMP-Bluetooth-Battery/dp/B0856PHNLX) with the [batmon-ha](https://github.com/fl4p/batmon-ha) addon to get voltage, current and SOC. SOH, along with a few other paramters are just defaulted currently. Charging parameters are all configurable, and you should make sure that they are correct for your battery/batteries.

This addon will also add some entities to HA for controlling the charge message, which contains a pair of switches for charge/discharge, a pair of switches to control forced charging, and a numerical charge current selector. My Deye inverter will initiate charging at the specified current if force_charge_1 is enabled, but YMMV, and you could damage your battery/hardware with improper settings.

Add-on documentation: <https://developers.home-assistant.io/docs/add-ons>

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fwebbbn%2Fha-can-battery-emulator)

## Add-ons

This repository contains the following add-ons

### [Can Battery Emulator add-on](./can-battery-emulator)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

_Home Assistant addon for emulating a CAN battery to inverter interface._

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
