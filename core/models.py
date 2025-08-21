from django.db import models

class Device(models.Model):
    """
    Represents a single, physical IoT device deployed in the field.

    This model stores metadata about the device itself, such as its unique
    identifier, user-assigned name, and operational status. This information
    is relatively static compared to the constant stream of sensor data.
    """
    device_uuid = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique hardware identifier, e.g., MAC address or a custom UUID."
    )
    name = models.CharField(
        max_length=255,
        help_text="A user-friendly name for easy identification, e.g., 'West Field Sensor'."
    )
    status = models.CharField(
        max_length=50,
        default='offline',
        help_text="The last reported status of the device, e.g., 'online', 'offline'."
    )
    battery_level = models.IntegerField(
        null=True,
        blank=True,
        help_text="The last reported battery level percentage (0-100)."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the device was first registered in the system."
    )

    def __str__(self) -> str:
        """String representation of the Device model."""
        return f"{self.name} ({self.device_uuid})"

class SensorReading(models.Model):
    """
    Stores a single, time-series data point collected from a device.

    This table is expected to be the largest in the database, as it will
    receive frequent updates from every active device.
    """
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='readings',
        help_text="The device that this reading originated from."
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the data was received by the server."
    )

    # Sensor Data Fields
    air_temperature = models.FloatField(null=True, blank=True, help_text="Air temperature in Celsius.")
    air_humidity = models.FloatField(null=True, blank=True, help_text="Relative air humidity as a percentage.")
    soil_moisture = models.FloatField(null=True, blank=True, help_text="Soil moisture as a percentage.")
    soil_ph = models.FloatField(null=True, blank=True, help_text="Soil pH level (0-14).")
    wind_speed = models.FloatField(null=True, blank=True, help_text="Wind speed in km/h.")
    wind_direction = models.CharField(max_length=50, null=True, blank=True, help_text="e.g., N, NE, SW.")
    nitrogen = models.FloatField(null=True, blank=True, help_text="Soil Nitrogen (N) level.")
    phosphorus = models.FloatField(null=True, blank=True, help_text="Soil Phosphorus (P) level.")
    potassium = models.FloatField(null=True, blank=True, help_text="Soil Potassium (K) level.")
    rainfall = models.FloatField(null=True, blank=True, help_text="Rainfall in mm since the last reading.")

    class Meta:
        """Metadata options for the SensorReading model."""
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', 'timestamp']),
        ]

    def __str__(self) -> str:
        """String representation of the SensorReading model."""
        return f"Reading for {self.device.name} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"