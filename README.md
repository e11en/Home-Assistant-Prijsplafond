## Home Assistant sensor component/integration for the Dutch nutservice pricecap (prijsplafond) in the Netherlands

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

- - -

If you like my work, please buy me a coffee. This will keep me awake :)

<a href="https://www.buymeacoffee.com/devsnow" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png"></a>

- - -

### Installation

~~[HACS](https://hacs.xyz/) > Integrations > Plus (+) > **Prijsplafond**~~
(HACS way is still work in progress, the PR has been made.. #waiting)

Or manually copy `prijsplafond` folder from [latest release](https://github.com/rbrink/Home-Assistant-Prijsplafond/releases/latest) to `custom_components` folder in your config folder.

## Configuration

Configuration > [Integrations](https://my.home-assistant.io/redirect/integrations/) > Add Integration > [Prijsplafond](https://my.home-assistant.io/redirect/config_flow_start/?domain=prijsplafond)

*If the integration is not in the list or is missing labels during configuration, you need to clear the browser cache.*

## Known design flaws
- As some might have noticed, one of the entities provided by this integration ends with power instead of energy. The answer yes.. I know.. Didn't really think that through. Can I change it? Yes I can but then the persons using the integration already will lose their history. So Sorry folks, I will keep it that way. Can you change it for yourself? Yes you can! As the entitites generated by this integration are given an unique id you can override the entity_id to anything you like. Feel free to change it to energy.
Problem solved!

### Useful template examples:
```yaml
template:
  - sensor:
      # Template sensor to display the current monthly cap.
      - name: Prijsplafond monthly gas cap
        unit_of_measurement:  "m³"
        state: "{{ state_attr('sensor.prijsplafond_gas', 'this_month_cap') }}"
        
      # Template sensor to display what this month total costs are.
      - name: Prijsplafond this month costs
        unit_of_measurement: "EUR"
        state: "{{ (state_attr('sensor.prijsplafond_gas', 'this_month_costs') | float) +
                   (state_attr('sensor.prijsplafond_power', 'this_month_costs') | float) }}"
        icon: mdi:currency-eur

      # With thanks to @pluim300 a sensor to show the remaining gas to be used for this month.
      - name: 'Prijsplafond remaining gas'
        unit_of_measurement: "m³"
        state: "{{ (state_attr('sensor.prijsplafond_gas', 'this_month_cap') | float | round(2) ) -
                   (states('sensor.prijsplafond_gas') | float | round(2) ) }}"
        icon: mdi:gas-cylinder

      # With thanks to @pluim300 a sensor to show the remaining energy to be used for this month.
      - name: 'Prijsplafond remaining energy'
        unit_of_measurement: "kWh"
        state: "{{ (state_attr('sensor.prijsplafond_power', 'this_month_cap') | float | round(2) ) -
                   (states('sensor.prijsplafond_power') | float | round(2) ) }}"
        icon: mdi:flash
```
