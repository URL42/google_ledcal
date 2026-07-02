import machine
import time
import gc
import network
import config
import urequests
import neopixel
import ntptime

# Configuration from config.py
calendar = config.CALENDAR
api_key = config.APIKEY
n = config.PIXELS
p = config.GPIOPIN
barcolor = config.BARCOL
eventcollist = config.EVENTCOL
schedule = config.SCHEDULE
flip = config.FLIP
googlecalbool = config.GOOGLECALBOOL
utc_offset_std = config.UTC_OFFSET_STD

# On-board LED for status
led = machine.Pin("LED", machine.Pin.OUT)

def connect_to_wifi(ssid, password, max_attempts=10):
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    if not sta_if.isconnected():
        print('Connecting to network...')
        sta_if.connect(ssid, password)
        for i in range(max_attempts):
            if sta_if.isconnected():
                print('Network config:', sta_if.ifconfig())
                return True
            time.sleep(1)
    else:
        return True
    return False

def machine_reset():
    print("Resetting in 5 seconds...")
    time.sleep(5)
    machine.reset()

def sync_time_ntp():
    ntp_servers = ["time.google.com", "time.cloudflare.com", "pool.ntp.org"]
    for server in ntp_servers:
        try:
            print(f"Syncing time via {server}...")
            ntptime.host = server
            ntptime.settime()
            print("Time synced successfully!")
            return True
        except Exception as e:
            print(f"{server} failed: {e}")
            time.sleep(1)
    return False

def nth_sunday(year, month, nth):
    """Day-of-month of the nth Sunday of the given month."""
    # mktime takes an 8-tuple; the weekday/yearday fields are ignored on input
    t = time.mktime((year, month, 1, 0, 0, 0, 0, 0))
    wd = time.gmtime(t)[6]  # weekday of the 1st: 0=Monday .. 6=Sunday
    first_sunday = 1 + (6 - wd) % 7
    return first_sunday + 7 * (nth - 1)

def local_offset_hours():
    """Current UTC offset in hours, applying US DST rules
    (DST runs from the 2nd Sunday of March to the 1st Sunday of November)."""
    t = time.gmtime(time.time() + utc_offset_std * 3600)  # local standard time
    year, month, day, hour = t[0], t[1], t[2], t[3]
    if month < 3 or month > 11:
        dst = False
    elif 3 < month < 11:
        dst = True
    elif month == 3:
        # DST starts at 2:00 standard time
        start = nth_sunday(year, 3, 2)
        dst = day > start or (day == start and hour >= 2)
    else:
        # DST ends at 2:00 daylight time, i.e. 1:00 standard time
        end = nth_sunday(year, 11, 1)
        dst = day < end or (day == end and hour < 1)
    return utc_offset_std + 1 if dst else utc_offset_std

def offset_iso(offset_h):
    """Hour offset as an RFC3339 suffix, URL-safe: -7 -> '-07:00'."""
    sign = "-" if offset_h < 0 else "%2B"  # '+' must be percent-encoded in URLs
    return "{}{:02d}:00".format(sign, abs(offset_h))

def get_today_appointment_times(calendar_id, api_key, tz, offset_h):
    # NTP sets the RTC to UTC; shift by the local offset to get the local date
    local_t = time.gmtime(time.time() + offset_h * 3600)
    date_str = "{:04d}-{:02d}-{:02d}".format(local_t[0], local_t[1], local_t[2])
    off = offset_iso(offset_h)

    # Explicit offset makes a valid RFC3339 timestamp so Google searches the
    # full LOCAL day, capturing evening events that are 'tomorrow' in UTC.
    # fields= trims the response to what we use — the Pico's heap is small.
    url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
    url += f"?timeMin={date_str}T00:00:00{off}&timeMax={date_str}T23:59:59{off}"
    url += f"&singleEvents=true&timeZone={tz}&fields=items(status,start,end)&key={api_key}"

    try:
        response = urequests.get(url, timeout=10)
        if response.status_code != 200:
            print("Google API Error:", response.status_code)
            response.close()
            return []

        data = response.json()
        response.close()

        events = []
        items = data.get("items", [])
        for item in items:
            if item.get("status") == "cancelled":
                continue
            s = item["start"].get("dateTime", item["start"].get("date"))
            e = item["end"].get("dateTime", item["end"].get("date"))
            events.append((s, e))

        # Sort strictly by start time
        events.sort()

        # Flatten to [s1, e1, s2, e2...]
        flattened = []
        for s, e in events:
            flattened.append(s)
            flattened.append(e)

        print(f"Sync Complete: Found {len(items)} events for {date_str}.")
        return flattened
    except Exception as e:
        print("Request failed:", e)
        return []

def whatday(weekday):
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    return days[weekday]

def timetohour(iso_str, offset_h):
    """Converts ISO strings to local decimal hour (0.0 - 24.0)."""
    if 'T' not in iso_str: return 0.0
    try:
        t_part = iso_str.split("T")[1]
        is_utc = "Z" in iso_str or "+00:00" in iso_str
        clean_t = t_part.replace('Z', '').split('-')[0].split('+')[0]
        parts = clean_t.split(':')
        hh = int(parts[0])
        mm = int(parts[1])
        if is_utc:
            hh = (hh + offset_h) % 24
        return hh + (mm/60)
    except:
        return 0.0

def hourtoindex(hoursin, clockin, clockout):
    if clockout <= clockin: return -1
    ratio = (hoursin - clockin) / (clockout - clockin)
    return int(n * ratio) if ratio >= 0 else -1

def get_alert_trigger(hoursin, appointment_times, offset_h):
    for t_str in appointment_times:
        h = timetohour(t_str, offset_h)
        # 30 second window for the alert trigger
        if abs(h - hoursin) < (0.5/60):
            return h
    return None

def rainbow_cycle(np, cycles=1):
    for j in range(255 * cycles):
        for i in range(n):
            pos = ((i * 256 // n) + j) & 255
            if pos < 85: col = (pos * 3, 255 - pos * 3, 0)
            elif pos < 170:
                pos -= 85
                col = (255 - pos * 3, 0, pos * 3)
            else:
                pos -= 170
                col = (0, pos * 3, 255 - pos * 3)
            np[i] = col
        np.write()
        time.sleep(0.001)

def full_system_pulse(np, color=(255, 255, 0)):
    print("ALARM: Meeting pulse triggered!")
    for _ in range(5): # 5 dramatic pulses
        for i in range(0, 101, 10):
            br = i / 100
            c = tuple(int(x * br) for x in color)
            for j in range(n): np[j] = c
            np.write()
            time.sleep(0.01)
        for i in range(100, -1, -10):
            br = i / 100
            c = tuple(int(x * br) for x in color)
            for j in range(n): np[j] = c
            np.write()
            time.sleep(0.01)

def application_mode():
    np = neopixel.NeoPixel(machine.Pin(p), n)
    rainbow_cycle(np)
    for i in range(n): np[i] = (0,0,0)
    np.write()

    if not sync_time_ntp():
        machine_reset()

    googleindex = 0
    appointment_times = []
    last_alert_h = -1.0
    check_interval = 300
    last_ntp = time.time()
    consecutive_errors = 0

    print("Starting Main Loop...")
    while True:
        try:
            off_h = local_offset_hours()

            if googlecalbool and googleindex == 0:
                led.on()
                appointment_times = get_today_appointment_times(calendar, api_key, config.TIMEZONE, off_h)
                led.off()
                gc.collect()

            # The RTC drifts over days; re-sync once a day (non-fatal if NTP is down)
            if time.time() - last_ntp > 86400:
                sync_time_ntp()
                last_ntp = time.time()

            # 1. Local Time Calculation
            lt = time.gmtime(time.time() + off_h * 3600)
            h_local = lt[3]
            hoursin = h_local + lt[4]/60 + lt[5]/3600
            dayname = whatday(lt[6])

            cin = float(schedule[dayname][0]['clockin'])
            cout = float(schedule[dayname][0]['clockout'])

            # 2. Frame Buffer
            frame = [(0, 0, 0)] * n

            if cin <= hoursin < cout:
                # 3. PAINT ALL UPCOMING EVENTS (Background)
                # We iterate through all event pairs to ensure none are missing
                for i in range(0, len(appointment_times)-1, 2):
                    h_start = timetohour(appointment_times[i], off_h)
                    h_end = timetohour(appointment_times[i+1], off_h)

                    p_start = hourtoindex(h_start, cin, cout)
                    p_end = hourtoindex(h_end, cin, cout)

                    if googleindex == 1:
                        print(f"Event {i//2} mapped to pixels {p_start} to {p_end}")

                    d_start = max(0, p_start)
                    d_end = min(n, p_end)

                    if d_start < d_end:
                        # Color alternation logic
                        col = eventcollist[(i//2) % len(eventcollist)]
                        for px in range(d_start, d_end):
                            frame[px] = col

                # 4. PAINT PROGRESS BAR ON TOP (The 'Eating' Layer)
                # Drawing this second overwrites events in the past with green
                bar_end = hourtoindex(hoursin, cin, cout)
                for i in range(min(bar_end, n)):
                    frame[i] = barcolor

                # 5. Meeting Alert Logic
                trigger_h = get_alert_trigger(hoursin, appointment_times, off_h)
                if trigger_h is not None and abs(trigger_h - last_alert_h) > (1/60):
                    full_system_pulse(np)
                    last_alert_h = trigger_h

                # 6. Blink Tip (White)
                if 0 <= bar_end < n and int(time.time()) % 2 == 0:
                    frame[bar_end] = (255, 255, 255)

            # 7. Push Frame to LEDs — every cycle, so the strip goes dark
            # outside work hours instead of holding the last frame
            if flip:
                frame.reverse()
            for i in range(n):
                np[i] = frame[i]
            np.write()

            # Maintenance & Heartbeat
            googleindex = (googleindex + 1) % check_interval
            if googleindex % 10 == 0:
                print(f"Time: {h_local:02d}:{lt[4]:02d} | Progress: {hoursin:.2f}/{cout}")

            consecutive_errors = 0
            time.sleep(1)

        except Exception as e:
            # Transient errors (Wi-Fi blips, memory pressure) get retries;
            # only a persistent failure reboots the board
            consecutive_errors += 1
            print(f"Loop Error ({consecutive_errors} in a row):", e)
            if consecutive_errors >= 5:
                machine_reset()
            time.sleep(5)

try:
    if connect_to_wifi(config.SSID, config.PASSWORD):
        application_mode()
    else:
        machine_reset()
except Exception as e:
    print("Global Error:", e)
    machine_reset()
