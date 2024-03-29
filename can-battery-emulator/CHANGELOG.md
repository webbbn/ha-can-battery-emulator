<!-- https://developers.home-assistant.io/docs/add-ons/presentation#keeping-a-changelog -->

## 1.0.0

- Initial release

## 1.1.0

- Switched from using paho MQTT to gmqtt
- Now using asyncio for improved efficiency and reliability
- Implemented expire_value_after, which adds tracking of the last update time of each value and removes a value if a timeout occurs. This helps prevent the code from writing old, and likely incorrect values to the inverter
- Tested for proper re-connection to MQTT server that goes offline
- Implemented clean shutdown
- Improved logging to reduce log clutter in normal operation

## 1.1.1

- Fixed namespace issue the prevented timeouts

## 1.1.2

- Updated documentation and configuration

# 1.1.3

- Fixed github CI/CD builds

# 1.2.0

- Added force charge/discharge switches

# 1.3.0

- Added controls for controling charging externally via the following controls:
  - Charge switch - enable/disable charging
  - Discharge switch - enable/disable discharging
  - Force charge 1 - Force charging of the battery mode 1
  - Force charge 1 - Force charging of the battery mode 2
  - Charge current - Force the charging current

  
