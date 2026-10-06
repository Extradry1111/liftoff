# liftoff: notes for Claude

## Brand and visuals

- **Grok Bot's image is `media/grok-bot.png`.** It's a white sphere with two slanted, pill-shaped black eye slots. When a post, banner or README needs "Grok Bot", use this image or the 3D version (`media/grok-bot-3d.jpg`). Don't invent a different mascot.
- `media/hero.jpg` is the 3D Grok Bot in brushed metal, framed by colorful 3D objects on black.
- `media/rocket.jpg` is the SpaceX launch-desk banner (stainless rocket, night launch).
- Demo GIFs/MP4s in `media/` are rendered from real `liftoff.py` runs. Don't fake terminal output.

## Writing for X

- English only, no em dashes, no hype words, no invented earnings or user counts.
- The Creator Rewards pilot is invite-only and payouts are discretionary. Always say so.

## Checks

```bash
python3 -m unittest discover tests
python3 liftoff/scripts/liftoff.py check liftoff/templates/liftoff-spacex
```
