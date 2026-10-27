DOMAIN = "shl_scoreboard"

API_BASE = "https://www.thesportsdb.com/api/v1/json"
DEFAULT_API_KEY = "123"  # TheSportsDB public free key
LEAGUE_ID = "4419"  # Swedish Hockey League
LEAGUE_NAME = "SHL"

CONF_API_KEY = "api_key"
CONF_NAME = "name"
CONF_TEAMS = "teams"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_SHOW_UPCOMING = "show_upcoming"

# The free key allows ~30 requests/minute; each poll uses 1-3 requests.
DEFAULT_SCAN_INTERVAL = 120
MIN_SCAN_INTERVAL = 60
MAX_SCAN_INTERVAL = 3600

# TheSportsDB strStatus codes
LIVE_STATUSES = {"1P", "2P", "3P", "OT", "PT", "BT", "P", "LIVE", "INT", "HT"}
FINAL_STATUSES = {"FT", "AOT", "AP", "AET", "PEN", "AW", "Match Finished"}
POSTPONED_STATUSES = {"PST", "CANC", "ABD", "SUSP", "INTR", "Postponed", "Cancelled"}

STATUS_TEXT = {
    "1P": "1st",
    "2P": "2nd",
    "3P": "3rd",
    "OT": "OT",
    "PT": "Shootout",
    "BT": "Break",
    "P": "Shootout",
    "INT": "Intermission",
    "HT": "Intermission",
    "LIVE": "Live",
    "FT": "Final",
    "Match Finished": "Final",
    "AOT": "Final/OT",
    "AET": "Final/OT",
    "AP": "Final/SO",
    "PEN": "Final/SO",
    "AW": "Final",
    "PST": "Postponed",
    "Postponed": "Postponed",
    "CANC": "Cancelled",
    "Cancelled": "Cancelled",
    "ABD": "Abandoned",
    "SUSP": "Suspended",
    "INTR": "Interrupted",
}

# Team names as TheSportsDB spells them -> common SHL abbreviations
TEAM_ABBREVIATIONS = {
    "Brynäs IF": "BIF",
    "Djurgårdens IF": "DIF",
    "Färjestad BK": "FBK",
    "Frölunda HC": "FHC",
    "HV71": "HV71",
    "IK Oskarshamn": "IKO",
    "Leksands IF": "LIF",
    "Linköpings HC": "LHC",
    "Luleå HF": "LHF",
    "Malmö Redhawks": "MIF",
    "MoDo Hockey": "MODO",
    "Modo Hockey": "MODO",
    "Örebro HK": "ÖHK",
    "Rögle BK": "RBK",
    "Skellefteå AIK": "SAIK",
    "Timrå IK": "TIK",
    "Växjö Lakers": "VLH",
    "AIK": "AIK",
    "BIK Karlskoga": "BIK",
    "Södertälje SK": "SSK",
    "Björklöven": "IFB",
    "IF Björklöven": "IFB",
    "Västerås IK": "VIK",
}
