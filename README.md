# Exhibitions calendar

Calendar feed of paid exhibitions, shown on weekends only (Sat and Sun, with opening hours) from the halfway point to closing at Tate Modern and Tate Britain, with
halfway and three-weeks-left alerts and Members Hours. Updated weekly.

**Subscribe on iPhone:** Settings → Calendar → Accounts → Add Account → Other →
Add Subscribed Calendar, paste the address below, and turn **Remove Alerts off**.

    https://raw.githubusercontent.com/mckenzei19/exhibitions/main/tate.ics

## Files

- `exhibitions.json`: Tate exhibitions and Members Hours sessions (the source of truth)
- `additions.json`: shows added by hand on the tracker page, copied in weekly
- `build_ics.py`: builds `tate.ics` from the two JSON files (`python3 build_ics.py`)

Tracker page: https://claude.ai/artifact/1M6m14DbDRCi3KJQqAMMer
