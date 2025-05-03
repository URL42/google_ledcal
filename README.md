# Workday Progress Bar with Google Calendar Integration (Pico W)

A Wi-Fi-connected LED progress bar built using a Raspberry Pi Pico W and an addressable LED strip. It visualizes how far you are into your workday and highlights scheduled events pulled from your Google Calendar.

This project was inspired by [veebch/hometime](https://github.com/veebch/hometime), but restructured and rewritten for my own purposes, with updated logic, simplified setup, and U.S. timezone defaults.

## 💡 What It Does

- Connects to Wi-Fi and syncs the current time via API
- Uses Google Calendar API to show your scheduled events
- Displays a progress bar indicating how far you are into your workday
- Shows different colors for scheduled events
- Celebrates the end of your day with a rainbow animation

## 🔧 Hardware Required

- Raspberry Pi Pico W
- WS2812B-compatible LED strip (e.g. 144 LEDs, 5V) - I also used an aluminum stip + diffuser
- 5V power source (VBUS on Pico W if USB powered)
- Basic wiring (3 pins: GND, VCC, Data)

### Pin Connections

| Pico GPIO | LED Strip |
|-----------|-----------|
| VBUS      | VCC       |
| GND       | GND       |
| GP0       | DATA      |

## 🛠️ Installation

1. Flash your Pico W with [MicroPython](https://micropython.org/download/rp2-pico-w/).
2. Clone or download this repo.
3. Update `config.py` with your:
   - Wi-Fi credentials
   - Google Calendar API key
   - Public Google Calendar ID
   - Timezone and work schedule
4. Upload files to your Pico W using [ampy](https://pypi.org/project/adafruit-ampy/), `rshell`, or Thonny:

```bash
ampy -p /dev/ttyACM0 put main.py
ampy -p /dev/ttyACM0 put config.py
```
5. Reboot your Pico W — the script will autorun on startup.

### ⚙️ Configuration (`config.py`)

| Field             | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| `SSID` / `PASSWORD` | Your Wi-Fi credentials for connecting the Pico W                          |
| `CALENDAR`        | Your public Google Calendar ID (e.g., `abc123@group.calendar.google.com`)   |
| `APIKEY`          | Your Google API key with Calendar API access                                |
| `TIMEZONE`        | IANA timezone string (e.g., `America/Los_Angeles`)                          |
| `PIXELS`          | Number of LEDs in the strip                                                 |
| `GPIOPIN`         | GPIO pin number connected to the LED strip (e.g., `0`)                      |
| `BARCOL`          | RGB tuple for normal progress bar color                                     |
| `EVENTCOL`        | List of RGB tuples for event (meeting) display colors                       |
| `FLIP`            | Set `True` to reverse LED order (right to left display)                     |
| `GOOGLECALBOOL`   | `True` to use Google Calendar, `False` to use the static schedule           |
| `SCHEDULE`        | Fallback daily schedule used if calendar is disabled                        |

---

### 🌐 Time Sync & Calendar Integration

- Time is fetched from [timeapi.io](https://timeapi.io) based on your configured timezone.
- If `GOOGLECALBOOL = True`, the system pulls the current day’s events from your public Google Calendar.
- If `False`, it uses the `SCHEDULE` dictionary in `config.py`.

---

### 🔑 Getting a Google Calendar API Key and Calendar ID

To use your public Google Calendar for event-based LED visualization, follow these steps to get an API key and calendar ID:

#### 1. Enable the Google Calendar API
- Go to the [Google Cloud Console](https://console.cloud.google.com/apis/library/calendar-json.googleapis.com)
- Select or create a project.
- Click **"Enable"** to activate the Google Calendar API for that project.

#### 2. Create an API Key
- In the [Credentials section](https://console.cloud.google.com/apis/credentials), click **"Create Credentials"** > **"API key"**.
- Copy this key and paste it into your `config.py` under `APIKEY`.

#### 3. Make Your Calendar Public
- Go to [Google Calendar](https://calendar.google.com)
- Find the calendar you want to use under **"My Calendars"** on the left.
- Click the 3-dot menu > **"Settings and sharing"**
- Under **"Access permissions for events"**, check **"Make available to public"**
- Scroll to **"Integrate calendar"** and copy the **Calendar ID** (it ends in `@group.calendar.google.com`).
- Paste that into `config.py` under `CALENDAR`.

> 📌 Your calendar must be public or shared with `default` visibility for the Pico W to read it without OAuth authentication.

---

### 🎨 LED Behavior

- The strip lights up progressively from clock-in to clock-out.
- During scheduled calendar events, LEDs show event colors instead of the default bar color.
- If a meeting is currently ongoing, a "breathing" animation occurs.
- A rainbow animation plays at the end of the workday.
- Outside of working hours, all LEDs are turned off.

---

### 🔍 Debugging

- Output is printed via serial USB (visible in Thonny, PuTTY, or screen).
- If the Pico W cannot connect to Wi-Fi or a web service, it will retry or reset.
- Watch for messages like:
  - `Connecting to network...`
  - `Grab time: ...`
  - `Scheduling issues`

---


### 📜 License

This project is licensed under the **GNU GPL v3**. You are free to use, modify, and share it as long as you keep it open.

---

### 🙏 Acknowledgements

This project was inspired by the original [hometime](https://github.com/veebch/hometime) project by [@veebch](https://www.instagram.com/v_e_e_b/), but was significantly modified to simplify logic and better fit my needs.
