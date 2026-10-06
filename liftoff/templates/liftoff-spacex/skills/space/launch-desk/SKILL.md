---
name: launch-desk
description: Find upcoming and recent SpaceX launches (Starship, Falcon 9, Falcon Heavy, Starlink, Dragon) with verified times, sites and stream links. Use when the user asks what's launching, when the next launch is, where to watch, or whether a launch scrubbed.
when-to-use: "what's launching", "next starship", "is the launch still on", "did it scrub", "where can I watch"
---

# Launch desk

## Steps

1. **Work out the window.** The default is the next 72 hours. "This week" means 7 days and "next Starship" means the next one, whatever the date.
2. **Search live.** Use web search and X search. Prefer these sources in this order:
   1. SpaceX's official site and @SpaceX on X
   2. NASA (for crew and cargo missions) and the FAA (for Starship licenses and airspace notices)
   3. Established launch trackers and space reporters on X. Name the account.
3. **Cross-check every time.** If two sources disagree, show both and say which is newer.
4. **Convert times** to the user's timezone and UTC.
5. **Answer in this format:**

```
🚀 [Vehicle] · [Mission]
🕒 [Day, time user TZ] ([time UTC])
📍 [Pad / site]
📺 [Official stream link]
💡 [One line: why it matters]
✅ last checked [time] via [source]
```

## Rules

- If it scrubbed or slipped, say so at the top. Don't bury it.
- Never fill a gap with a guess. If the time is "NET" (no earlier than), write "NET".
- Starlink batches can be grouped into one line ("3 Starlink launches: Tue, Wed, Fri").
- For the weekly wrap, count only launches that actually lifted off.
