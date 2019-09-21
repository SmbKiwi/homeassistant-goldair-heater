"""
Platform to control Goldair WiFi-connected heaters and panels.
"""
from homeassistant.components.climate import ClimateDevice

from homeassistant.components.climate.const import (
    ATTR_PRESET_MODE, HVAC_MODE_OFF, HVAC_MODE_HEAT, CURRENT_HVAC_HEAT, CURRENT_HVAC_IDLE, CURRENT_HVAC_OFF, CURRENT_HVAC_DRY,
    SUPPORT_TARGET_TEMPERATURE, SUPPORT_PRESET_MODE, SUPPORT_SWING_MODE
)
from homeassistant.const import (STATE_UNAVAILABLE, ATTR_TEMPERATURE)
import custom_components.goldair_heater as goldair_heater

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE | SUPPORT_SWING_MODE

ATTR_ON = 'on'
STATE_ANTI_FREEZE = 'Anti-freeze'

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Goldair WiFi heater."""
    device = hass.data[goldair_heater.DOMAIN][discovery_info['host']]
    add_devices([
        GoldairHeater(device)
    ])


class GoldairHeater(ClimateDevice):
    """Representation of a Goldair WiFi heater."""

    def __init__(self, device):
        """Initialize the heater.
        Args:
            name (str): The device's name.
            device (GoldairHeaterDevice): The device API instance."""
        self._device = device

        self._support_flags = SUPPORT_FLAGS

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return self._support_flags

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    @property
    def name(self):
        """Return the name of the climate device."""
        return self._device.name

    @property
    def state(self):
        """Return the state of the climate device."""
        if self._device._get_cached_state()[ATTR_ON] is None:
            return STATE_UNAVAILABLE
        if self._device._get_cached_state()[ATTR_ON] is True:
            return HVAC_MODE_HEAT
        return HVAC_MODE_OFF    

    @property     
    def hvac_mode(self):
        """Return current hvac mode (heating or off)."""
        return self._device.hvac_mode

    @property  
    def hvac_modes(self):
        """Return hvac modes (heating or off)."""
        return self._device.hvac_modes
    
    def set_hvac_mode(self, hvac_mode):
        return self._device.set_hvac_mode(hvac_mode)
    
    @property
    def hvac_action(self):
        """Return the current running hvac operation."""
        if self._device.hvac_mode == HVAC_MODE_HEAT:  
             return CURRENT_HVAC_HEAT    
        if self._device.preset_mode == STATE_ANTI_FREEZE:
            return CURRENT_HVAC_DRY
        if self._device.target_temperature is not None:
            if self._device.target_temperature < self._device.current_temperature:
                return CURRENT_HVAC_IDLE
        return CURRENT_HVAC_OFF

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return self._device.temperature_unit

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._device.target_temperature

    @property
    def target_temperature_step(self):
        """Return the supported step of target temperature."""
        return self._device.target_temperature_step

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return self._device.min_target_teperature

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return self._device.max_target_temperature

    def set_temperature(self, **kwargs):
        """Set new target temperatures."""
        if kwargs.get(ATTR_TEMPERATURE) is not None:
            self._device.set_target_temperature(kwargs.get(ATTR_TEMPERATURE))
        if kwargs.get(ATTR_PRESET_MODE) is not None:
            self._device.set_preset_mode(kwargs.get(ATTR_PRESET_MODE))

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._device.current_temperature

    @property
    def preset_mode(self):
        """Return current device operation, ie Comfort, Eco, Anti-freeze."""
        return self._device.preset_mode

    @property
    def preset_modes(self):
        """Return the list of available device operation modes."""
        return self._device.preset_modes

    def set_preset_mode(self, preset_mode):
        """Set new device operation mode."""
        self._device.set_preset_mode(preset_mode)

    @property
    def swing_mode(self):
        """Return the power level setting."""
        return self._device.power_level

    @property
    def swing_modes(self):
        """List of available power level modes."""
        return self._device.power_level_list

    def set_swing_mode(self, swing_mode):
        """Set new target temperature."""
        self._device.set_power_level(swing_mode)

    def update(self):
        self._device.refresh()
