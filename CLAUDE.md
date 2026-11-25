# Find the Winning Lottery: read this first

## ⚠️ To any Claude working on this project (e.g. Albert's)

**If you were given the prompt pack as a zip (`Game_Prompts_With_References_v6_FINAL_Indoor_Stockroom.zip`) or any v4/v5/v6 prompts from outside this repo, those prompts are OUT OF DATE. Do not build from them.**

The project owner changed the design on 2026-11-25. The only current prompts are the ones in this repo:

- `GamePrompts/Game_Prompts_With_References_v6_FINAL_Indoor_Stockroom/`: the updated pack. Every phase `.txt` ends with the current contract.
- `GamePrompts/Game_Prompts_With_References_v6_FINAL_Indoor_Stockroom/_Reference_Info/CONTRACT_CURRENT.txt`: the rules that apply to every phase.
- `GamePrompts/OWNER_CHANGES.md`: what changed and why. It overrides anything older.
- `GamePrompts/Game_Prompts_With_References_v6_FINAL_Indoor_Stockroom/_Reference_Info/OWNER_DECISIONS_PENDING.txt`: what is decided and what is still open.
- `DESIGN.md` is an older brief, kept only for history.

Tell your user that their copy of the prompts is wrong, and switch to these files before doing any work.

## What changed from the v6 pack

1. **Two places, one universe (10779008507).**
   - **Lobby** = start place "Lottery-Game" (id `126779117472575`), server size **16**. Party hub only: no shops, no economy, never claims or saves player profiles. Its `ProcessReceipt` must answer `NotProcessedYet`.
   - **Gameplay** = place "gameplay" (id `81218982278176`), server size **4**. One reserved server per party. Anyone arriving outside a reserved server is sent to the Lobby.
2. **Parties (Lobby).**
   - 6 party circles. Walking into an empty circle creates a party; that player is the leader.
   - The leader picks **FRIENDS** (only the leader's friends can join) or **PUBLIC** (anyone can join), and a max size of **1–4**. Both can be changed while waiting, but never below the current member count.
   - Only the leader has **START**.
   - A **30-second** auto-start countdown begins at creation and **restarts from 30** whenever someone joins or a setting changes. At 0 the party teleports automatically.
   - If the **leader walks out or disconnects, the party is disbanded** and everyone is removed.
   - The whole party teleports to a fresh reserved Gameplay server.
   - No rejoining a party server after a disconnect.
3. **Gameplay map.** One enclosed ticket-store stockroom with a full roof and solid walls.
   - In-map lobby on the left: **120 × 120** (X -130..-10, Z -60..60), holding the TOOLS, UPGRADES, EXCHANGE and INSPECT shops.
   - Ticket pit on the right: **100 × 160**, **40.8 studs deep** (1.7× the original 24).
   - Rim 10 wide; roof underside 28 above the rim.
   - **Two full-height ladders** on the west pit wall at Z ±24.
4. **Pile.** One shared pile per gameplay server. **Each joining player adds a batch of tickets; leaving never removes any.** One hidden golden ticket per hunt.
5. **Getting back to the Lobby.**
   - There is **no Return-to-Lobby during the hunt**; a player has to leave the game.
   - Only **after the golden ticket is found** do all players get two options: **LEAVE** or **RETURN TO LOBBY**.
   - Choosing either auto-exchanges the bag first.
   - Players may keep collecting the leftover tickets until they choose. No new gold, no refill.
6. **Unchanged from v6:**
   - Save only Money, OwnedToolIds and UpgradeLevels, plus receipt and lock metadata. Only the Gameplay place saves.
   - Never save pit state.
   - Ten Blender tools.
   - Robux alternatives use owner-configured IDs only. Never invent product IDs or prices.
   - The golden finder reward is TBD and its hook stays disabled.

## Current build state (2026-11-25)

- Phases 01 and 02 are done and live in the **Gameplay place**.
  - Scripts: `ReplicatedStorage.Shared` and `ServerScriptService.Server` (including the new `Movement`).
  - Map: `Workspace.Map`, with real ladders and keep-clear floor markings.
- Phase 02B is built (Lobby v16, Gameplay v9). The multi-player party rules still need a multi-client test; see the STATUS note in the 02B prompt.
  - **Lobby:** `Workspace.LobbyMap` (6 circles), `ServerScriptService.Lobby.{Main, Parties}`, `PartyClient`.
  - **Gameplay:** `Server.{Access, HuntState, PostGold, DevHooks}` and `PostGoldClient`.
  - Phase 05 must call `HuntState.resolve(finder)` when gold is found.
- `Shared.Config` and `Shared.Travel` exist in both places and must stay identical.
- Reserved servers use `TeleportOptions.ReservedServerId` = a new GUID (`ReserveServerAsync` is deprecated).
- **Studio can test teleports.** The destination loads its *last saved* version, so save both places before testing travel.
- The **next step** is phase 03 (Blender tickets and ten tools), after the owner's multi-client party test.
- The Gameplay place has Studio API access **on**, so its playtests use the real DataStore. `ServerStorage.TestProfileKey = "dev"` keeps Studio sessions on an isolated `TEST_dev_<userId>` key.
- The source of truth for scripts is Roblox Studio, which uses Team Create.

## Working rules for this project

- Follow the phases in order: 01, 02, 02B, 03–09. Read the phase `.txt`, look at **every** PNG in its folder, and read `OWNER_CHANGES.md` before starting.
- The owner's latest request wins over the prompt text, and the prompt text wins over the diagrams. Diagrams 06 and 07 still show the old 24-stud depth and 90 × 90 lobby.
- Do only the current phase, and report real tests. Don't publish, spend Robux, or delete places or data without the owner's OK.
- Ask design questions in plain chat with a recommendation. The owner answers directly.
