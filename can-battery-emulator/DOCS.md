# Home Assistant Add-on: CAN Battery Emulator

## How to use

Provides an MQTT to CAN bus bridge between non-standard solar batteries and inverters
that support CAN bus battery protocols. The current list of supported hardware is very
limited, but could be expanded relatively easily.

The following is a list of battery stats that must be published on MQTT with default topic names:

- Voltage (victron/soc/total_voltage)
- Current (victron/soc/current)
- SOC: (victron/soc/soc_percent)
- Power: (victron/soc/power)

The default set of topics is compatible with the Victron interface suppor in the [batmon-ha addon](https://github.com/fl4p/batmon-ha), but are fairly standard and could come from many sources. Combining mulitple batteries is not currently supported.

The only supported battery protocol supported is Plontech protocol, which was derived thanks to the [ESPHome JK BMS CAN github project](https://github.com/Uksa007/esphome-jk-bms-can).

The current code is mimimally tested with a [Deye/Sunsynk 16k inverter](https://www.deyeinverter.com/product/hybrid-inverter-1/sun12-14-16ksg01lp1-1216kw-single-phase-3-mppt-hybrid-inverter.html), so use at your own risk.

Note: The [Enable Can Addon](https://github.com/dries007/HA_EnableCAN) is recommended for configuring the CAN bus interface on Home Assistant.
