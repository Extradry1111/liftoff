# Liftoff routines

Routines are what bring users back every day, and coming back is what Creator Rewards counts. A skill is the playbook and a routine is the schedule that runs it.

| Routine | When | Runs | Sends |
|---|---|---|---|
| Morning brief | Daily, 08:00 user time | `/launch-desk` (next 72h) | Upcoming launches, times, one-line "why it matters" |
| T-minus alert | 60 min before any launch the user follows | `/launch-desk` + `/launch-post` (pre) | Final time check, stream link, ready-to-post draft |
| Post-flight | 30 min after T-0 | `/starship-explainer` + `/launch-post` (post) | What happened, confirmed vs. unconfirmed, recap draft |
| Weekly wrap | Sunday 18:00 user time | `/launch-desk` (last 7d + next 7d) | Week in launches, count, records, next week's highlight |

## Copy-paste routine prompts

**Morning brief**
```
Run /launch-desk for the next 72 hours. Send me a brief: max 5 launches, each with vehicle, mission, time in my timezone + UTC, and one line on why it matters. If nothing launches, say so in one line and tell me the next launch date.
```

**T-minus alert**
```
A launch I follow is ~60 minutes out. Recheck the time with live search. Send: confirmed time, official stream link, weather/scrub risk if reported, and a /launch-post pre-launch draft in my voice.
```

**Post-flight**
```
Check what happened on the launch that just flew. Separate confirmed (SpaceX/official) from unconfirmed. Then run /launch-post in recap mode.
```

**Weekly wrap**
```
Run /launch-desk for the past 7 days and next 7 days. Send a weekly wrap: number of SpaceX launches, notable firsts or records (confirmed only), and the one launch to watch next week.
```

## Tips

- Keep alerts opt-in per vehicle. A user who only cares about Starship shouldn't get 12 Starlink pings a week, because people who get spammed turn the bot off.
- If nothing is happening, send less. Silence is better than filler.
