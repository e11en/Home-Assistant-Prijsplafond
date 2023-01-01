#!/usr/bin/env python3
"""
Sensor component for Prijsplafond
Author: Richard Brink
"""

import voluptuous as vol
from datetime import datetime

from .const.const import (
    _LOGGER,
    CONF_SOURCE_TOTAL_GAS,
    CONF_SOURCES_TOTAL_POWER,
    DOMAIN,
    ATTR_FRIENDLY_NAME,
    ATTR_THIS_MONTH_CAP,
    ATTR_THIS_MONTH_COSTS,
    ATTR_UNIT_OF_MEASUREMENT,
    GAS_PRICE,
    NAME,
    POWER_PRICE,
    PRICE_CAP_GAS_MONTH,
    PRICE_CAP_POWER_MONTH,
    UNIT_OF_MEASUREMENT_GAS,
    UNIT_OF_MEASUREMENT_POWER,
    UPDATE_MIN_TIME,
    ATTR_PREVIOUS_TOTAL_USAGE
)

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_RESOURCES
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SOURCES_TOTAL_POWER, default=[]): cv.entity_ids,
        vol.Required(CONF_SOURCE_TOTAL_GAS, default=""): cv.entity_id
    }
)

def setup_platform(hass: HomeAssistant, config, add_entities, discovery_info=None):
    _LOGGER.debug(f"Setup {NAME} sensor")

    add_entities(
        [
            PrijsplafondSensor(
                hass,
                "stroom",
                config.get(CONF_SOURCES_TOTAL_POWER),
                config.get(CONF_SOURCE_TOTAL_GAS)
            ),

            PrijsplafondSensor(
                hass,
                "gas",
                config.get(CONF_SOURCES_TOTAL_POWER),
                config.get(CONF_SOURCE_TOTAL_GAS)
            )
        ]
    )

    return True

class PrijsplafondSensor(Entity):
    def __init__(
        self,
        hass: HomeAssistant,
        type,
        total_power_entities,
        total_gas_entity
    ):
        self.entity_id = f"sensor.{DOMAIN}_{type}"
        self.friendly_name = f"{type.capitalize()}gebruik deze maand"
        self._state = 0
        self._previous_total_usage = 0

        self._current_month = datetime.now().month

        if type == 'gas':
            self.this_month_cap = PRICE_CAP_GAS_MONTH[self._current_month]
            self.this_month_costs = 0
            self._unit_of_measurement = UNIT_OF_MEASUREMENT_GAS

            self._price = GAS_PRICE
            self._sources = [total_gas_entity]
        else:
            self.this_month_cap = PRICE_CAP_POWER_MONTH[self._current_month]
            self.this_month_costs = 0
            self._unit_of_measurement = UNIT_OF_MEASUREMENT_POWER

            self._price = POWER_PRICE
            self._sources = total_power_entities

    @property
    def name(self):
        return self.friendly_name

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement

    @property
    def extra_state_attributes(self):
        return {
            ATTR_FRIENDLY_NAME: self.friendly_name,
            ATTR_THIS_MONTH_CAP: self.this_month_cap,
            ATTR_THIS_MONTH_COSTS: self.this_month_costs,
            ATTR_UNIT_OF_MEASUREMENT: self._unit_of_measurement,
            ATTR_PREVIOUS_TOTAL_USAGE: self._previous_total_usage
        }

    @Throttle(UPDATE_MIN_TIME)
    def update(self):
        # Fetching the old state in order to calculate new values.
        old_state = self.hass.states.get(self.entity_id)

        # Calculating total usage based on given sensors.
        total_usage = -1
        for entity_id in self._sources:
            state = self.hass.states.get(entity_id)

            if state is None:
                _LOGGER.error('Unable to find entity "%s"', entity_id)
                continue

            # As we need a sum of the sources to calculate the usage.
            total_usage += float(state.state)

        if total_usage == -1:
            _LOGGER.error('Error while updating sensor "%s"', self.entity_id)
            return

    	# If no previous state has been found it means the usage state is 0.
        if old_state is None:
            self._state = 0
        else:
            previous = old_state.attributes.get(ATTR_PREVIOUS_TOTAL_USAGE, 0) 
            if previous > 0:
                self._state += (total_usage - previous)
            
        self._previous_total_usage = total_usage
        self.this_month_costs = self._state * self._price
