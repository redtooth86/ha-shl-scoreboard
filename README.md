# SHL Scoreboard for Home Assistant

A Home Assistant custom integration that shows **Swedish Hockey League (SHL)** games using the
[TheSportsDB](https://www.thesportsdb.com/league/4419-swedish-hockey-league) v1 API.

The sensor uses the same attribute format as the
[MyScoreboard](https://github.com/viktoro/ha-myscoreboard) integration, so it works directly with
[MyScoreboard Card](https://github.com/viktoro/ha-myscoreboard-card).

## Installation

### HACS

1. HACS → ⋮ → **Custom repositories** → add `https://github.com/redtooth86/ha-shl-scoreboard`, category **Integration**
2. Install **SHL Scoreboard** and restart Home Assistant

### Manual

Copy `custom_components/shl_scoreboard` to your `config/custom_components/` folder and restart.

## Setup

**Settings → Devices & services → Add integration → SHL Scoreboard**

| Option | Default | Description |
|--------|---------|-------------|
| Sensor name | `SHL` | Name of the sensor (`sensor.shl`) |
| Only these teams | _(all)_ | Comma-separated team names or abbreviations, e.g. `FHC, Luleå` |
| Show last/next game | on | When no games are played today, show the most recent and the next SHL game |
| Poll interval | 120 s | 60–3600 seconds |
| API key | `123` | TheSportsDB free key. A premium key gives fresher data |

You can add the integration more than once with different names, for example one sensor for the
whole league and one for your own team. All options can be changed later via **Configure**.

## Display with MyScoreboard Card

Install [MyScoreboard Card](https://github.com/viktoro/ha-myscoreboard-card) and add:

```yaml
type: custom:myscoreboard-card
title: SHL
entities:
  - sensor.shl
```

## Sensor

State: number of games in the `games` attribute.

| Attribute | Description |
|-----------|-------------|
| `league` | `SHL` |
| `games` | List of games (see below) |
| `today_count` | Games played today (local time) |
| `live_count` / `final_count` / `pre_count` | Games by state |
| `next_game` / `last_game` | Filled when there are no games today and "show last/next game" is on |

Each game has `game_state` (0 = not started, 1 = live, 2 = final), `status`, `start_time` (UTC ISO 8601),
`start_time_local` (`19:00`, in Home Assistant's time zone), `home_team`, `home_abbr`, `home_logo`, `home_score`,
the same `away_*` fields, `venue`, `round` and `season`.

`status` is the start time for games that haven't started (`19:00` today, `Fri 30/10 19:00` on
another day), the period while live (`1st`, `2nd`, `3rd`, `OT`, `Shootout`), and `Final`, `Final/OT` or
`Final/SO` afterwards. MyScoreboard Card shows it in the right-hand column.

## Limitations of the free API key

- TheSportsDB's v1 API is not a true live-score feed; scores during a game may lag or only appear after the final whistle.
- The free key is limited to about 30 requests per minute. Each poll uses one request (three when there are no games today), so keep the poll interval at 60 s or more, especially with several sensors.
- With the free key, "next" and "last" return only one league game each.

## Development

```bash
pip install aiohttp pytest
pytest
```

Data provided by [TheSportsDB](https://www.thesportsdb.com).
