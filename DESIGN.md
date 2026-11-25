# Find the Winning Lottery — Roblox Design Brief

> **Superseded (2026-11-25):** the v6 prompt pack in `GamePrompts/Game_Prompts_With_References_v6_FINAL_Indoor_Stockroom/` is now the build spec. Where this brief disagrees with it (scratch prizes, days/playtime boards, per-player piles, saved tickets), follow v6. Kept for history.

One metallic gold ticket is buried in a pile of colorful lottery tickets. The fun is in spotting the first sliver of gold, clearing enough space to grab it, and finding out how many winners you can collect.

Creative reference: Jayify's TikTok. Lottery tickets replace the money shown in the reference. (Map: not yet specified.)

## How a hunt plays
- **Start.** v1: each player gets their own pile. Tickets overlap so several corners/edges are visible. First hunt shows "Find the gold ticket!"; player picks where to start.
- **Search.** Tap/click an exposed ticket to lift it out; whatever was directly underneath is revealed (e.g. a blue ticket clears to show two pink stubs and a gold corner). Once the gold corner is visible, tapping it claims the win.

## Look
- **Regular tickets:** ~20 colors. Each has a torn stub, printed number, perforated edge; must read as a lottery ticket on a phone. Yellow can be bright but stays matte.
- **Gold ticket:** metallic foil, star stamp, moving glint — reserved for the winner. Only the exposed part shimmers. On claim: ticket lifts above the pile, gold sparkle burst, "Winning ticket found!" with updated total.

## Scratch it or sell it
Every uncovered ticket goes into the player's stack. Player decides when to cash in. Gold counts toward the wins leaderboard immediately, and can still be scratched or sold afterward.
- **Scratch:** select a ticket, drag finger/mouse across the covered panel; coating comes off to reveal the prize. Ordinary ticket may pay nothing or beat the machine's offer. Gold always reveals a cash prize.
- **Sell:** bring an unscratched ticket to the machine, see its guaranteed offer, confirm to get cash immediately. Starting a scratch commits the ticket to its revealed payout. Each ticket pays out once.

## Tools (10)
Tools change which part of the pile you can clear. Player stats carry over between tools.
1. **Ticket Grabber** — one exposed ticket at a time; learn controls / precise clears.
2. **Dustpan Scoop** — lift a small cluster by aiming at the edge of an overlapping stack.
3. **Hand Rake** — drag toward yourself to comb a narrow strip of the top layer.
4. **Push Broom** — sweep a wide, shallow path; good for checking a fresh pile for a glint.
5. **Shovel** — lift several layers from one small spot; dig down.
6. **Handheld Vacuum** — hold to pull loose tickets into your stack; steer nozzle around a promising corner.
7. **Leaf Blower** — push the top layer aside in a cone; exposes buried tickets fast, but you must still collect them.
8. **Shop Vac** — long hose, work from farther away; hold over one spot to pull successive layers.
9. **Rotary Sweeper** — walk forward as twin brushes collect tickets in a wide lane; coverage depends on steering.
10. **Ride-on Ticket Vacuum** — drive through the pile with a wide intake collecting ordinary tickets; spot gold, stop, claim it yourself.

## Player upgrades (permanent)
- **Movement Speed** — run faster between pile, sell machine, shop; helps rotary sweeper coverage.
- **Dig Speed** — shorter delay between scoops/rakes/shovel strikes; on held tools, shorter time between pickups.
- **Reach** — interact with tickets farther from the character (aim distance); tool determines pass width.
- **Carry Capacity** — hold more unscratched tickets before bag is full; when full, scratch or sell to free space.
- **Scratch Speed** — reveal a wider strip per stroke; scratching stays manual.

Upgrade buttons show **current and next value**. Regular tickets collected by a tool go to the stack. An exposed gold ticket stays visible until the player claims it.

**Persistence:** purchased upgrades, unspent cash, and unused tickets persist between hunts and across sessions.

## Repeat play & leaderboards
Win counts the moment gold is claimed. During the celebration a fresh pile is prepared with the winner buried somewhere different; player can dig again in the same session. Saved totals / leaderboards:
- **Most Winning Lotteries Found** — total, updated after each run.
- **Playtime** — cumulative across sessions (40m + 30m = "1h 10m").
- **Most Days** — most days survived in a single run (decided 2026-11-25). **Conflict:** the brief has no survival/day mechanic and says cash, upgrades and tickets persist — so what ends a run? See open question 15.

---

## Open questions / gaps found on inspection
1. **"Most Days" is undefined.** Days in a run? Consecutive login days? Distinct days played? Also "run" is never defined (one hunt? a lifetime?). Needs a decision before data schema.
2. **Map unspecified.** Brief ends at "Map will be" — incomplete sentence. Need setting (shop, sell machine, pile location).
3. **Pile is per-player, but the world is shared?** Needs per-player pile visibility (client-side rendered piles vs. server-owned physical parts). Big perf/architecture impact.
4. **Ticket count / physics.** Hundreds of overlapping tickets with layered "what's underneath" logic → recommend a data-driven layered pile (server state + client render), not physics parts.
5. **Anti-exploit:** gold location must never be sent to the client; claim must be server-validated for exposure + reach.
6. **Economy numbers missing:** ticket payout distribution, sell-offer vs scratch EV (offer must be a real tradeoff), gold prize range, tool/upgrade price curves, carry capacity start/max.
7. **Carry capacity vs. gold:** does the gold ticket take a bag slot? If bag is full, can the player still claim it? (Suggest: always allowed.)
8. **Vacuum tools auto-collect** — can they accidentally pull the gold? Brief says gold stays until claimed and ride-on collects *ordinary* tickets only; assume all tools skip gold, and it should be spotted exposed.
9. **Persistence of "unused tickets"** — must save each ticket's type, color, and pre-rolled prize so reloading can't reroll. Save-on-sell/scratch commit to prevent dupes.
10. **Scratch commit rule:** "starting a scratch commits" → decide how a partial scratch is saved if the player leaves mid-scratch (recommend: prize revealed server-side at start, paid on start).
11. **Mobile input:** tap, scratch-drag, held vacuum, and driving the ride-on all need touch/gamepad schemes.
12. **Roblox compliance:** lottery/gambling theme — scratch-ticket prizes are in-game cash only, no Robux purchase of tickets/odds (2026 paid random item rules). Check age-rating and monetization policy before adding any paid boosts.
13. **Tool 1 → 10 unlock cost/ordering and whether tools are bought or just unlocked** is unstated; "Tool" vs "stat" currency is the same cash.
14. **Telemetry/leaderboard:** ordered DataStores per board; playtime must be saved periodically, not only on leave.
15. **"Days survived" needs a mechanic.** Nothing in the brief can end a run or define a day. Options: (a) day = fixed real-time cycle (e.g. 10 min) and a daily rent/upkeep bill; failing to pay ends the run (resets cash/tickets, keeps upgrades+tools); (b) hazard-based. Option (a) doubles as a cash sink. Needs user decision before building.

---

## Starter economy (v0 — tune by simulation)
Everything is cash. Numbers are first-pass guesses.

### Ordinary ticket (base values at tier 1)
Scratch prize table: $0 40% · $5 30% · $10 15% · $25 9% · $100 4.5% · $500 1.5% → **EV $17.25**
Machine offer: **$12 flat** (~70% of EV). Scratching pays ~44% more on average but takes time and 40% of tickets pay $0, so selling is the safe/fast option and scratching the greedy one.
Gold ticket: scratch always pays $150–$1,000 (avg **$400**); machine offer **$300**. Gold win counts to leaderboard either way.

### Pile tiers (scale with highest tool owned, t = 1..10)
- Pile size: 120, 150, 190, 240, 300, 380, 480, 600, 750, 900 (x1.25/tier)
- Prize multiplier on ALL ticket + gold values and offers: x2^(t-1) (x1 ... x512)
- Target hunt income ~ $800 at t1, growing ~2.5x per tier (~90 s per hunt at its tier).

### Tools
| # | Tool | Price |
|---|------|-------|
| 1 | Ticket Grabber | free |
| 2 | Dustpan Scoop | $1,500 |
| 3 | Hand Rake | $5,000 |
| 4 | Push Broom | $15,000 |
| 5 | Shovel | $40,000 |
| 6 | Handheld Vacuum | $100,000 |
| 7 | Leaf Blower | $250,000 |
| 8 | Shop Vac | $600,000 |
| 9 | Rotary Sweeper | $1,500,000 |
| 10 | Ride-on Ticket Vacuum | $3,500,000 |
Each tool should take ~2-3 hunts of income at the previous tier.

### Upgrades (15 levels each, level n cost = base x 1.5^(n-1))
| Stat | Level 0 -> 15 | Base cost | Max-level cost |
|------|---------------|-----------|----------------|
| Movement Speed | 16 -> 31 studs/s (+1/lvl) | $150 | ~$44k |
| Dig Speed (cooldown) | 1.00s -> 0.40s (x0.94/lvl) | $200 | ~$58k |
| Reach | 10 -> 32.5 studs (+1.5/lvl) | $250 | ~$73k |
| Carry Capacity | 20 -> 200 tickets (+12/lvl) | $300 | ~$88k |
| Scratch Speed (strip width) | 1.0x -> 2.5x (+0.1/lvl) | $200 | ~$58k |
Buying every level of every upgrade costs ~ $960k total (about mid-game, before tools 9-10).
Upgrade prices do NOT scale with pile tier, so they get cheap late; consider scaling price by x1.5 per tier above t4 if they become irrelevant.

### Sinks / safety
- Carry cap 20 at start ~ 20 x $12 = $240 per bag -> frequent sell trips early (intended); bag 200 late.
- Gold claim never blocked by a full bag.
- All payouts rolled server-side when the ticket is created and stored with the ticket.
