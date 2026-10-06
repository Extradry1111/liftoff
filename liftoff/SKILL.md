---
name: liftoff
description: Build, score, scrub and launch Grok Bot templates that people keep using, which is what Grok Bot Creator Rewards pays for. Use when the user wants to make a Grok Bot or Grok Bot template, turn an idea into a bot, check whether a bot is ready to share, find leaked keys or personal data before sharing, write the X post that launches a template, log Creator Rewards payouts, or set up the SpaceX launch-desk bot.
when-to-use: "grok bot", "grok bot template", "creator rewards", "make money with grok", "is my bot ready to share", "launch my template", "spacex bot"
---

# liftoff

Grok Bot Creator Rewards pays creators every two weeks based on **how many people use their templates and how consistently they keep using them**. One-shot bots get copied and forgotten. liftoff helps the user build the other kind and ship it without leaking anything.

You have a script that measures everything. **Run it. Don't guess.**

```
python3 scripts/liftoff.py new "NAME" -o DIR      scaffold a template
python3 scripts/liftoff.py score DIR              Stickiness Score 0-100 + fixes
python3 scripts/liftoff.py scan DIR               Leak Scan (exit 1 = don't share)
python3 scripts/liftoff.py post FILE              Launch Check for the X post
python3 scripts/liftoff.py check DIR --post FILE  all three
python3 scripts/liftoff.py pack DIR               TEMPLATE_CARD.md: paste-ready blocks, in order
```

Paths are relative to this skill's folder. If you can't run code, apply the same checks by hand from `references/stickiness.md` and `references/leaks.md`, and say that you checked by hand.

## Pick the mode

| The user says | Mode |
|---|---|
| an idea, "make me a bot", "what should I build" | **BUILD** |
| pastes a bot, "is this ready", "why does nobody use my bot" | **AUDIT** |
| "write the post", has a share link | **LAUNCH** |
| "got paid", "rewards update" | **LOG** |
| "spacex", "launch bot", "show me an example" | **LIFTOFF** |

## BUILD: idea → template that sticks

1. **Score the idea before writing anything.** If the user has no idea yet, offer picks from `references/template-ideas.md`. Use the six questions in `references/stickiness.md` (recurring job, routine-able, live data, memory, 30-second win, shareable). Show the table. If it scores under 18/30, propose a sharper version first. Most one-shot ideas can be rescued with a daily routine ("logo generator" becomes "daily brand radar + logo critic").
2. **Scaffold** with `new`, then fill every `[FILL: …]` blank (the score is capped at 40 until they are gone):
   - `BOT.md`: who it serves, what it does, rules, `## First message`. Under 500 words.
   - `ROUTINES.md`: at least one daily routine, written as a copy-paste prompt in a code block under a **bold name**.
   - 1-3 skills at `skills/<category>/<slug>/SKILL.md`, each with a `description` that says **when to use it**.
3. **Run `score`.** Fix every ✗ and ! line and rerun. **Don't stop below 80.**
4. **Run `scan`.** It must say SAFE TO SHARE.
5. **Run `pack`** and give the user `TEMPLATE_CARD.md`, which has everything to paste into Grok Bot in order.
6. Show the final score and scan result in your answer, as proof.

## AUDIT: existing bot → fixes

1. Ask the user to paste the bot's instructions, every skill and every routine. Write them into a folder in the template layout above.
2. Run `check`. Report the score, every leak (masked, never repeat a full secret) and the top 3 fixes ranked by points.
3. Offer to apply the fixes, then rerun and show before → after.

## LAUNCH: the X post

Rules come from the program terms, so they're not optional: the template goes in a **public X post with its share link**, and the post uses X's **paid partnership label**.

1. Ask for the share link and a real output, like a screenshot or pasted text. **Never invent a link, user counts, testimonials or earnings.**
2. Write the post using `references/launch-posts.md`, with 2 hook options.
3. Save it to a file and run `post`. Fix anything flagged until READY TO POST.
4. Remind the user to turn on **Paid partnership** before posting.
5. Write 3 follow-up quote-posts, each with a new angle and new proof.

## LOG: payouts

Follow `references/rewards-log.md`. Program facts and sources are in `references/rewards-program.md`. Keep a table of each period's payout per template next to what changed. Suggest **one** experiment per template for the next period. Never invent numbers.

## LIFTOFF: the SpaceX launch desk

`templates/liftoff-spacex/` is a complete template that scores 100/100: a daily SpaceX launch brief, T-60 alerts with stream links, post-flight recaps that keep confirmed and unconfirmed apart, and X post drafts. Run `pack` on it and hand over the card. Suggest the user give it their own angle, such as Starship only, Starlink coverage or a Starbase local feed, before sharing it as their own template.

## Always

- Be straight about the money. The rewards pilot is **invite-only** (US, 18+, Grok Bot account, X account in good standing, eligible Premium). Payouts are **discretionary**, not a revenue share and not guaranteed. The Stickiness Score is built on the factors X has named publicly, not on X's actual formula. Say so if the user asks "how much will I make".
- Templates copy the bot's description, skills, routines, relevant memories and first-party plugins. **Secrets aren't removed automatically.** Logins, custom code, private MCP servers and the author's computer don't travel, so a bot that needs them breaks for everyone who copies it.
- No em dashes in anything you write for X.
