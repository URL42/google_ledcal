SSID = "YOUR SSID HERE"
PASSWORD = "YOUR PASSWORD HERE"
CALENDAR = "YOUR CALENDAR GMAIL ADDRESS HERE"
APIKEY = "GOOGLE CALENDAR API"
#OAUTH_TOKEN = ""
TIMEZONE = "America/Los_Angeles" #update your own timezone
# Lighting
PIXELS = 144
GPIOPIN = 0
BARCOL = (0,100,0)
EVENTCOL =[(255, 255, 0),(0,128,255)] # list of tuples used as meeting colours (255,255,0)
FLIP = False                # Flip display (set to True if the strip runs from right to left)
GOOGLECALBOOL = True        # Boolean for whether to check google calendar page
IGNORE_HARDCODED = False    # Set to True if you want Clock in at the start of first meeting and Clockout at end of last meeting
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
