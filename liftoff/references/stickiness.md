# Stickiness: what makes people come back

Creator Rewards looks at how many people use a template and **how consistently they keep using it**. Getting people to copy it isn't the hard part. Getting them to come back on day 2, day 9 and day 30 is.

## Score the idea (before building)

Score each one from 1 to 5. Under 18/30, sharpen the idea first.

| Test | Question | 1 | 5 |
|---|---|---|---|
| Recurring job | How often does the user need this? | once | daily |
| Routine-able | Can a schedule run it with nobody typing? | no | yes, fully |
| Live data | Does today's output differ from yesterday's? | never | always |
| Personal memory | Does it improve the more it knows the user? | no | a lot |
| 30-second win | Is the first reply useful on its own? | needs setup | instantly |
| Shareable | Would someone post the output on X? | never | often |

**The rescue move:** most one-shot ideas become sticky when you add a routine that brings in live data. For example:
- "Logo generator" becomes "daily brand radar + logo critic".
- "Resume rewriter" becomes "daily job radar + tailored first line".
- "Trip planner" becomes "trip planner + daily price watch".

## What the script measures (Stickiness Score, 100 points)

| Check | Points | What earns it |
|---|---|---|
| Comes back on its own | 25 | `ROUTINES.md` with a schedule (15) that runs daily or more often (+10) |
| Fresh every day | 15 | Live web/X data, news, prices, "today" (2+ cues = 15, 1 = 8) |
| Remembers the user | 15 | `BOT.md` tells the bot what to remember and reuse |
| 30-second first win | 15 | A `## First message` section (10) that asks a question and gives a prompt to try (+5) |
| Does one job well | 10 | 1-3 skills (4-5 = 5) |
| Skills trigger reliably | 10 | Each skill's `description` is 40+ chars and says when to use it |
| Easy to turn down | 5 | Users can mute alerts or ask for less |
| Short instructions | 5 | `BOT.md` up to 500 words (up to 800 = 2) |
| Won't travel | −10 each, max −20 | Depends on logins, custom code, private MCP servers, localhost or "my computer" |

80+ means **Built to stick**, 60-79 means **Close: fix the misses**, and under 60 means **One-and-done risk**.

It's a heuristic built on the factors X has named publicly. It isn't X's payout formula.

## Anti-patterns

- **One-shot generators.** Used once, then forgotten.
- **Alert spam.** Twelve pings a week, and the user mutes the bot forever. Make alerts opt-in per topic.
- **Ten skills.** If nobody can say what it's for, nobody comes back.
- **Hidden dependencies.** It works for you but breaks for everyone who copies it.
