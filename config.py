SSID = "YOUR SSID HERE"
PASSWORD = "YOUR PASSWORD HERE"
CALENDAR = "YOUR CALENDAR GMAIL ADDRESS HERE"
APIKEY = "GOOGLE CALENDAR API"
#OAUTH_TOKEN = ""
TIMEZONE = "America/Los_Angeles" #update your own timezone
UTC_OFFSET_STD = -8         # Standard-time UTC offset in hours; must match TIMEZONE.
                            # DST (US rules) is applied automatically on top of this.
# Lighting
PIXELS = 144
GPIOPIN = 15 
BARCOL = (0,100,0)
EVENTCOL =[(255, 255, 0),(0,128,255)] # list of tuples used as meeting colours (255,255,0)
FLIP = False                # Flip display (set to True if the strip runs from right to left)
GOOGLECALBOOL = True        # Boolean for whether to check google calendar page
SCHEDULE = {
    "monday": [
      {
        "clockin": "8",
        "clockout": "17"
      }
    ],
    "tuesday": [
      {
        "clockin": "8",
        "clockout": "17"
      }
    ],
    "wednesday": [
      {
        "clockin": "8",
        "clockout": "17"
      }
    ],
    "thursday": [
      {
        "clockin": "8",
        "clockout": "17"
      }
    ],
    "friday": [
      {
        "clockin": "8",
        "clockout": "17"
      }
    ],
"saturday": [
      {
        "clockin": "0",
        "clockout": "0"
      }
    ],
    "sunday": [
      {
        "clockin": "0",
        "clockout": "0"
      }
    ]
}
