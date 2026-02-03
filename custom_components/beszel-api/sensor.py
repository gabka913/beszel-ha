from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, LOGGER

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []

    try:
        # Get systems and stats from coordinator data
        systems = coordinator.data['systems']
        stats_data = coordinator.data.get('stats', {})

        for system in systems:
            try:
                # Get stats for this system
                system_stats = stats_data.get(system.id, {})

                entities.append(BeszelCPUSensor(coordinator, system))
                entities.append(BeszelRAMSensor(coordinator, system))
                entities.append(BeszelRAMUsageSensor(coordinator, system))
                entities.append(BeszelRAMTotalSensor(coordinator, system))
                entities.append(BeszelDiskSensor(coordinator, system))
                entities.append(BeszelDiskUsageSensor(coordinator, system))
                entities.append(BeszelDiskTotalSensor(coordinator, system))
                entities.append(BeszelBandwidthSensor(coordinator, system))
                entities.append(BeszelTemperatureSensor(coordinator, system))
                entities.append(BeszelUptimeSensor(coordinator, system))

                # Create EFS sensors if EFS data is available
                if system_stats and 'efs' in system_stats and isinstance(system_stats['efs'], dict):
                    for disk_name in system_stats['efs'].keys():
                        entities.append(BeszelEFSDiskSensor(coordinator, system, disk_name))
                        entities.append(BeszelEFSDiskUsageSensor(coordinator, system, disk_name))
                        entities.append(BeszelEFSDiskTotalSensor(coordinator, system, disk_name))
                        LOGGER.info(f"Created EFS sensor for {system.name} - {disk_name}")

            except Exception as e:
                LOGGER.error(f"Failed to create sensors for system {system.name if hasattr(system, 'name') else 'unknown'}: {e}")
                continue

        LOGGER.info(f"Created {len(entities)} sensors total")
        async_add_entities(entities)
    except Exception as e:
        LOGGER.error(f"Failed to setup sensors: {e}")
        raise

class BeszelBaseSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, system):
        super().__init__(coordinator)
        self._system_id = system.id

    @property
    def system(self):
        systems = self.coordinator.data['systems']
        for s in systems:
            if s.id == self._system_id:
                return s
        return None

    @property
    def system_stats(self):
        return self.coordinator.data['stats'][self._system_id]

    @property
    def device_info(self):
        sys = self.system
        if sys is None:
            return None
        info = getattr(sys, "info", {})
        return {
            "identifiers": {(DOMAIN, sys.id)},
            "name": sys.name,
            "manufacturer": "Beszel",
            "model": info.get("m"),
            "sw_version": info.get("v"),
            "hw_version": info.get("k"),
        }

class BeszelCPUSensor(BeszelBaseSensor):
    @property
    def unique_id(self):
        return f"beszel_{self._system_id}_cpu"

    @property
    def name(self):
        return f"{self.system.name} CPU" if self.system else None

    @property
    def icon(self):
        return "mdi:memory"

    @property
    def native_value(self):
        return self.system.info.get("cpu") if self.system else None

    @property
    def native_unit_of_measurement(self):
        return "%"

class BeszelRAMSensor(BeszelBaseSensor):
    @property
    def unique_id(self):
        return f"beszel_{self._system_id}_ram"

    @property
    def name(self):
        return f"{self.system.name} RAM" if self.system else None

    @property
    def icon(self):
        return "mdi:chip"

    @property
    def native_value(self):
        return self.system.info.get("mp") if self.system else None

    @property
    def native_unit_of_measurement(self):
        return "%"

class BeszelRAMUsageSensor(BeszelBaseSensor):
    @property
    def unique_id(self):
        return f"beszel_{self._system_id}_used_ram"

    @property
    def name(self):
        return f"{self.system.name} Used RAM" if self.system else None

    @property
    def icon(self):
        return "mdi:chip"

    @property
    def native_value(self):
        return self.system_stats.get("mu") if self.system_stats else None

    @property
    def native_unit_of_measurement(self):
        return "GB"

    @property
    def device_class(self):
        return SensorDeviceClass.DATA_SIZE

class BeszelRAMTotalSensor(BeszelBaseSensor):
    @property
    def unique_id(self):
        return f"beszel_{self._system_id}_total_ram"

    @property
    def name(self):
        return f"{self.system.name} Total RAM" if self.system else None

    @property
    def icon(self):
        return "mdi:chip"

    @property
    def native_value(self):
        return self.system_stats.get("m") if self.system_stats else None

    @property
    def native_unit_of_measurement(self):
        return "GB"

    @property
    def device_class(self):
        return SensorDeviceClass.DATA_SIZE

class BeszelDiskSensor(BeszelBaseSensor):

    @property
    def unique_id(self):
        return f"beszel_{self._system_id}_disk"

    @property
    def name(self):
        return f"{self.system.name} Disk" if self.system else None

    @property
    def icon(self):
        return "mdi:harddisk"

    @property
    def native_value(self):
        return self.system.info.get("dp") if self.system else None

    @property
    def native_unit_of_measurement(self):
        return "%"

class BeszelDiskUsageSensor(BeszelBaseSensor):

    @property
    def unique_id(self):
        return f"beszel_{self._system_id}_used_disk"

    @property
    def name(self):
        return f"{self.system.name} Used Disk" if self.system else None

    @property
    def icon(self):
        return "mdi:harddisk"

    @property
    def native_value(self):
        return self.system_stats.get("du") if self.system_stats else None

    @property
    def native_unit_of_measurement(self):
        return "GB"

    @property
    def device_class(self):
        return SensorDeviceClass.DATA_SIZE

class BeszelDiskTotalSensor(BeszelBaseSensor):

    @property
    def unique_id(self):
        return f"beszel_{self._system_id}_total_disk"

    @property
    def name(self):
        return f"{self.system.name} Total Disk" if self.system else None

    @property
    def icon(self):
        return "mdi:harddisk"

    @property
    def native_value(self):
        return self.system_stats.get("d") if self.system_stats else None

    @property
    def native_unit_of_measurement(self):
        return "GB"

    @property
    def device_class(self):
        return SensorDeviceClass.DATA_SIZE

class BeszelBandwidthSensor(BeszelBaseSensor):
    @property
    def unique_id(self):
        return f"beszel_{self._system_id}_bandwidth"

    @property
    def name(self):
        return f"{self.system.name} Bandwidth" if self.system else None

    @property
    def icon(self):
        return "mdi:router-network"

    @property
    def native_value(self):
        return self.system.info.get("b") if self.system else None

    @property
    def native_unit_of_measurement(self):
        return "MB/s"

class BeszelTemperatureSensor(BeszelBaseSensor):
    @property
    def unique_id(self):
        return f"beszel_{self._system_id}_temperature"

    @property
    def name(self):
        return f"{self.system.name} temperature" if self.system else None

    @property
    def native_value(self):
        return self.system.info.get("dt") if self.system else None

    @property
    def device_class(self):
        return "temperature"

    @property
    def native_unit_of_measurement(self):
        return "°C"

class BeszelUptimeSensor(BeszelBaseSensor):
    @property
    def unique_id(self):
        return f"beszel_{self._system_id}_uptime"

    @property
    def name(self):
        return f"{self.system.name} uptime" if self.system else None

    @property
    def icon(self):
        return "mdi:sort-clock-descending"

    @property
    def native_value(self):
        return self.system.info.get("u") / 60 if self.system else None

    @property
    def suggested_display_precision(self):
        return 2

    @property
    def state_class(self):
        return "total_increasing"

    @property
    def native_unit_of_measurement(self):
        return "minutes"

class BeszelEFSDiskSensor(BeszelBaseSensor):
    def __init__(self, coordinator, system, disk_name):
        super().__init__(coordinator, system)
        self._disk_name = disk_name

    @property
    def unique_id(self):
        return f"beszel_{self._system_id}_efs_{self._disk_name}"

    @property
    def name(self):
        return f"{self.system.name} EFS {self._disk_name}" if self.system else None

    @property
    def icon(self):
        return "mdi:harddisk"

    @property
    def native_value(self):
        if not self.system_stats:
            return None

        efs_data = self.system_stats.get('efs', {})
        disk_data = efs_data.get(self._disk_name, {})

        total_space = disk_data.get('d')
        used_space = disk_data.get('du')

        # Calculate disk usage percentage
        if total_space and used_space and total_space > 0:
            return round((used_space / total_space) * 100, 2)
        return None

    @property
    def native_unit_of_measurement(self):
        return "%"

    @property
    def extra_state_attributes(self):
        """Return additional state attributes for the EFS disk."""
        if not self.system_stats:
            return {}

        efs_data = self.system_stats.get('efs', {})
        disk_data = efs_data.get(self._disk_name, {})

        return {
            "total_disk_space_gb": disk_data.get('d'),
            "disk_used_gb": disk_data.get('du'),
            "read_mb_s": disk_data.get('r'),
            "write_mb_s": disk_data.get('w'),
        }

class BeszelEFSDiskUsageSensor(BeszelBaseSensor):
    def __init__(self, coordinator, system, disk_name):
        super().__init__(coordinator, system)
        self._disk_name = disk_name

    @property
    def unique_id(self):
        return f"beszel_{self._system_id}_efs_{self._disk_name}_used"

    @property
    def name(self):
        return f"{self.system.name} EFS {self._disk_name} Used" if self.system else None

    @property
    def icon(self):
        return "mdi:harddisk"

    @property
    def native_value(self):
        if not self.system_stats:
            return None

        efs_data = self.system_stats.get('efs', {})
        disk_data = efs_data.get(self._disk_name, {})

        return disk_data.get('du')

    @property
    def native_unit_of_measurement(self):
        return "GB"

    @property
    def device_class(self):
        return SensorDeviceClass.DATA_SIZE

class BeszelEFSDiskTotalSensor(BeszelBaseSensor):
    def __init__(self, coordinator, system, disk_name):
        super().__init__(coordinator, system)
        self._disk_name = disk_name

    @property
    def unique_id(self):
        return f"beszel_{self._system_id}_efs_{self._disk_name}_total"

    @property
    def name(self):
        return f"{self.system.name} EFS {self._disk_name} Total" if self.system else None

    @property
    def icon(self):
        return "mdi:harddisk"

    @property
    def native_value(self):
        if not self.system_stats:
            return None

        efs_data = self.system_stats.get('efs', {})
        disk_data = efs_data.get(self._disk_name, {})

        return disk_data.get('d')

    @property
    def native_unit_of_measurement(self):
        return "GB"

    @property
    def device_class(self):
        return SensorDeviceClass.DATA_SIZE