/**
 * Dashboard WebSocket Client
 * Manages WebSocket connection to dashboard and displays real-time data
 */

class DashboardWebSocket {
	constructor() {
		this.socket = null;
		this.reconnectInterval = null;
		this.reconnectAttempts = 0;
		this.maxReconnectAttempts = 5;
		this.isConnected = false;

		// DOM elements
		this.statusIndicator = document.getElementById("connection-status");
		this.devicesContainer = document.getElementById("devices-container");
		this.latestReadingsContainer = document.getElementById("latest-readings");

		this.init();
	}

	init() {
		this.connect();
		this.setupEventListeners();
	}

	connect() {
		try {
			// Replace with your server URL
			const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
			const wsUrl = `${protocol}//${window.location.host}/ws/dashboard/`;

			this.socket = new WebSocket(wsUrl);
			this.setupSocketEvents();
		} catch (error) {
			console.error("Error creating WebSocket connection:", error);
			this.handleConnectionError();
		}
	}

	setupSocketEvents() {
		this.socket.onopen = (event) => {
			this.isConnected = true;
			this.reconnectAttempts = 0;
			this.updateConnectionStatus("connected");

			// Request initial data
			this.requestOnlineDevices();
		};

		this.socket.onmessage = (event) => {
			try {
				const data = JSON.parse(event.data);
				this.handleMessage(data);
			} catch (error) {
				console.error("Error parsing WebSocket message:", error);
			}
		};

		this.socket.onclose = (event) => {
			this.isConnected = false;
			this.updateConnectionStatus("disconnected");

			// Attempt to reconnect if not manually closed
			if (event.code !== 1000) {
				this.attemptReconnect();
			}
		};

		this.socket.onerror = (error) => {
			console.error("Dashboard WebSocket error:", error);
			this.handleConnectionError();
		};
	}

	handleMessage(data) {
		switch (data.type) {
			case "connection_established":
				this.showNotification("Terhubung ke dashboard", "success");
				break;

			case "online_devices":
				this.updateOnlineDevices(data.devices);
				break;

			case "sensor_update":
				this.handleSensorUpdate(data);
				break;

			case "latest_readings":
				this.updateLatestReadings(data.device_uuid, data.readings);
				break;

			case "error":
				this.showNotification(data.message, "error");
				break;

			default:
		}
	}

	handleSensorUpdate(data) {
		// Update device data in real-time
		this.updateDeviceCard(data.device_uuid, data);

		// Add to latest readings if viewing specific device
		this.addToLatestReadings(data);

		// Show notification for new data
		this.showNotification(`Data baru dari ${data.device_name}`, "info", 3000);

		// Update charts if function exists
		if (typeof updateCharts === "function") {
			updateCharts(data);
		}
	}

	updateDeviceCard(deviceUuid, data) {
		const deviceCard = document.querySelector(`[data-device-uuid="${deviceUuid}"]`);
		if (!deviceCard) return;

		// Update timestamp
		const timestampElement = deviceCard.querySelector(".last-update");
		if (timestampElement) {
			const timestamp = new Date(data.timestamp).toLocaleString("id-ID");
			timestampElement.textContent = `Terakhir update: ${timestamp}`;
		}

		// Update sensor values
		const sensorData = data.data;
		Object.keys(sensorData).forEach((key) => {
			const element = deviceCard.querySelector(`[data-sensor="${key}"]`);
			if (element && sensorData[key] !== null) {
				element.textContent = this.formatSensorValue(key, sensorData[key]);

				// Add animation class
				element.classList.add("updated");
				setTimeout(() => element.classList.remove("updated"), 1000);
			}
		});

		// Update device status indicator
		const statusIndicator = deviceCard.querySelector(".device-status");
		if (statusIndicator) {
			statusIndicator.classList.remove("offline");
			statusIndicator.classList.add("online");
		}
	}

	updateOnlineDevices(devices) {
		if (!this.devicesContainer) return;

		devices.forEach((device) => {
			let deviceCard = document.querySelector(`[data-device-uuid="${device.device_uuid}"]`);

			if (!deviceCard) {
				deviceCard = this.createDeviceCard(device);
				this.devicesContainer.appendChild(deviceCard);
			} else {
				this.updateDeviceStatus(deviceCard, device);
			}
		});
	}

	createDeviceCard(device) {
		const card = document.createElement("div");
		card.className = "device-card";
		card.setAttribute("data-device-uuid", device.device_uuid);

		card.innerHTML = `
            <div class="device-header">
                <h3>${device.name}</h3>
                <span class="device-status ${device.status}">${device.status}</span>
            </div>
            <div class="device-info">
                <p>UUID: ${device.device_uuid}</p>
                ${device.battery_level !== null ? `<p>Battery: ${device.battery_level}%</p>` : ""}
            </div>
            <div class="sensor-data">
                <div class="sensor-grid">
                    <div class="sensor-item">
                        <label>Temperature</label>
                        <span data-sensor="air_temperature">-</span>°C
                    </div>
                    <div class="sensor-item">
                        <label>Humidity</label>
                        <span data-sensor="air_humidity">-</span>%
                    </div>
                    <div class="sensor-item">
                        <label>Soil Moisture</label>
                        <span data-sensor="soil_moisture">-</span>%
                    </div>
                    <div class="sensor-item">
                        <label>Soil pH</label>
                        <span data-sensor="soil_ph">-</span>
                    </div>
                    <div class="sensor-item">
                        <label>Wind Speed</label>
                        <span data-sensor="wind_speed">-</span> km/h
                    </div>
                    <div class="sensor-item">
                        <label>Wind Direction</label>
                        <span data-sensor="wind_direction">-</span>
                    </div>
                </div>
            </div>
            <div class="last-update">Belum ada data</div>
            <button class="btn-view-details" onclick="dashboardWS.viewDeviceDetails('${device.device_uuid}')">
                Lihat Detail
            </button>
        `;

		return card;
	}

	updateDeviceStatus(deviceCard, device) {
		const statusElement = deviceCard.querySelector(".device-status");
		if (statusElement) {
			statusElement.textContent = device.status;
			statusElement.className = `device-status ${device.status}`;
		}

		const batteryElement = deviceCard.querySelector(".battery-level");
		if (batteryElement && device.battery_level !== null) {
			batteryElement.textContent = `${device.battery_level}%`;
		}
	}

	addToLatestReadings(data) {
		if (!this.latestReadingsContainer) return;

		const readingItem = document.createElement("div");
		readingItem.className = "reading-item";

		const timestamp = new Date(data.timestamp).toLocaleString("id-ID");
		readingItem.innerHTML = `
            <div class="reading-header">
                <strong>${data.device_name}</strong>
                <span class="timestamp">${timestamp}</span>
            </div>
            <div class="reading-data">
                ${Object.entries(data.data)
					.filter(([key, value]) => value !== null)
					.map(
						([key, value]) => `
                        <span class="data-point">
                            ${this.getSensorLabel(key)}: ${this.formatSensorValue(key, value)}
                        </span>
                    `
					)
					.join("")}
            </div>
        `;

		// Insert at the beginning
		this.latestReadingsContainer.insertBefore(readingItem, this.latestReadingsContainer.firstChild);

		// Keep only last 20 readings
		const readings = this.latestReadingsContainer.children;
		while (readings.length > 20) {
			this.latestReadingsContainer.removeChild(readings[readings.length - 1]);
		}
	}

	viewDeviceDetails(deviceUuid) {
		this.sendMessage({
			type: "get_latest_readings",
			device_uuid: deviceUuid,
		});
	}

	updateLatestReadings(deviceUuid, readings) {
		// Create modal or update specific section with detailed readings
		// You can implement a modal or dedicated section here
		// For now, just log the data
	}

	formatSensorValue(sensorType, value) {
		if (value === null || value === undefined) return "-";

		switch (sensorType) {
			case "air_temperature":
			case "soil_ph":
				return Number(value).toFixed(1);
			case "air_humidity":
			case "soil_moisture":
				return Number(value).toFixed(0);
			case "wind_speed":
				return Number(value).toFixed(1);
			case "nitrogen":
			case "phosphorus":
			case "potassium":
				return Number(value).toFixed(0);
			case "rainfall":
				return Number(value).toFixed(2);
			default:
				return value;
		}
	}

	getSensorLabel(sensorType) {
		const labels = {
			air_temperature: "Temp Udara",
			air_humidity: "Kelembaban",
			soil_moisture: "Kelembaban Tanah",
			soil_ph: "pH Tanah",
			wind_speed: "Kec. Angin",
			wind_direction: "Arah Angin",
			nitrogen: "Nitrogen",
			phosphorus: "Fosfor",
			potassium: "Kalium",
			rainfall: "Curah Hujan",
		};
		return labels[sensorType] || sensorType;
	}

	updateConnectionStatus(status) {
		if (!this.statusIndicator) return;

		this.statusIndicator.className = `connection-status ${status}`;
		this.statusIndicator.textContent = status === "connected" ? "Terhubung" : "Terputus";
	}

	showNotification(message, type = "info", duration = 5000) {
		// Create notification element
		const notification = document.createElement("div");
		notification.className = `notification ${type}`;
		notification.innerHTML = `
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.remove()">×</button>
        `;

		// Add to notifications container or body
		const container = document.getElementById("notifications") || document.body;
		container.appendChild(notification);

		// Auto remove after duration
		if (duration > 0) {
			setTimeout(() => {
				if (notification.parentElement) {
					notification.remove();
				}
			}, duration);
		}
	}

	requestOnlineDevices() {
		this.sendMessage({ type: "get_devices" });
	}

	sendMessage(message) {
		if (this.socket && this.socket.readyState === WebSocket.OPEN) {
			this.socket.send(JSON.stringify(message));
		} else {
			console.warn("WebSocket not connected. Message not sent:", message);
		}
	}

	handleConnectionError() {
		this.updateConnectionStatus("error");
		this.showNotification("Koneksi WebSocket error", "error");
	}

	attemptReconnect() {
		if (this.reconnectAttempts >= this.maxReconnectAttempts) {
			this.showNotification("Gagal terhubung kembali. Silakan refresh halaman.", "error", 0);
			return;
		}

		this.reconnectAttempts++;
		const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);

		this.showNotification(`Mencoba terhubung kembali... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`, "warning", delay);

		this.reconnectInterval = setTimeout(() => {
			this.connect();
		}, delay);
	}

	setupEventListeners() {
		// Setup any additional event listeners here
		window.addEventListener("beforeunload", () => {
			if (this.socket) {
				this.socket.close(1000);
			}
		});

		// Reconnect button if exists
		const reconnectBtn = document.getElementById("reconnect-btn");
		if (reconnectBtn) {
			reconnectBtn.addEventListener("click", () => {
				this.reconnectAttempts = 0;
				this.connect();
			});
		}
	}

	disconnect() {
		if (this.reconnectInterval) {
			clearTimeout(this.reconnectInterval);
		}

		if (this.socket) {
			this.socket.close(1000);
		}
	}
}

// Initialize WebSocket when DOM is loaded
let dashboardWS;
document.addEventListener("DOMContentLoaded", function () {
	dashboardWS = new DashboardWebSocket();
});

// Cleanup on page unload
window.addEventListener("beforeunload", function () {
	if (dashboardWS) {
		dashboardWS.disconnect();
	}
});
