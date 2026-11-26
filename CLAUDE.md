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
   - **Lobby** = start place "Lottery-Game" (id `126779117472575`), server size **16**. Party hub with two booths (Upgrades, Classes) and the lifetime leaderboards. The booths are read-only until the Lobby gets a proper profile handoff: it still never claims or saves profiles, and its `ProcessReceipt` answers `NotProcessedYet`.
   - **Gameplay** = place "gameplay" (id `81218982278176`), server size **4**. One reserved server per party. Anyone arriving outside a reserved server is sent to the Lobby.
2. **Parties (Lobby).**
   - 4 party rings (was 6 until 2026-11-26). A player creates a party at an empty ring through its prompt and setup panel (walking in does nothing); that player is the leader. Others join through the ring's "Join party" prompt.
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
6. **Economy rework (owner, 2026-11-26 evening).** It overrides the save rules below; see OWNER_CHANGES.
   - Cash is per hunt. Tools and bags bought with cash last one hunt; bought with Robux they are owned forever.
   - Gems are saved. They buy permanent hand upgrades (the starter Ticket Grabber) in the Lobby, so the Lobby must save profiles.
   - Gems are found in the pit in colour tiers, and tickets have rarity tiers worth more. Bags come in tiers.
7. **Unchanged from v6** (except where item 6 overrides it):
   - Save only Money, OwnedToolIds, UpgradeLevels and (schema v2, 2026-11-26) lifetime `Stats` for the leaderboards, plus receipt and lock metadata. Only the Gameplay place saves.
   - Never save pit state.
   - (2026-11-26) The Lobby booths must work, so the Lobby will need to load and save profiles. That is not built yet.
   - Ten Blender tools.
   - Robux alternatives use owner-configured IDs only. Never invent product IDs or prices.
   - The golden finder reward is TBD and its hook stays disabled.

## Current build state (2026-11-25)

- Phases 01 and 02 are done and live in the **Gameplay place**.
  - Scripts: `ReplicatedStorage.Shared` and `ServerScriptService.Server` (including the new `Movement`).
  - Map: `Workspace.Map`, with real ladders and keep-clear floor markings.
- Phase 02B is built. The Lobby was redesigned twice on 2026-11-26; the current build is Lobby v49 / Gameplay v14. The multi-player party rules still need a 2-player Studio test (Test -> Clients and Servers).
  - **Lobby (redesign, late 2026-11-26):** the courtyard is generated by `ServerStorage.LobbyBuilder`, which creates `Workspace.LobbyMap` with 4 rings, 2 booths and the leaderboards. Scripts: `ServerScriptService.Lobby.{Main, Parties, Leaderboards}`, plus the client scripts `PartyClient`, `BoothClient` and `PromptChip`. Parties are created through a per-player prompt and setup panel, never by walking in. See OWNER_CHANGES 2026-11-26 (late, and the polish pass).
  - **Gameplay:** `Server.RunStats` records lifetime stats (schema v2).
  - **Gameplay:** `Server.{Access, HuntState, PostGold, DevHooks}` and `PostGoldClient`.
  - Phase 05 must call `HuntState.resolve(finder)` when gold is found (the whole team gets the leaderboard win), and `RunStats.addCollected(player, n)` when tickets enter the bag.
- `Shared.Config` and `Shared.Travel` exist in both places and must stay identical.
- Reserved servers use `TeleportOptions.ReservedServerId` = a new GUID (`ReserveServerAsync` is deprecated).
- **Studio can test teleports.** The destination loads its *last saved* version, so save both places before testing travel.
- **Phase 03 (2026-11-26): done and approved by the owner, including unique colours per tool. Gameplay saved as v20.**
  - **Phase 03 extension (2026-11-26): done and approved by the owner. Gameplay saved as v24.**
    - Pit gems in 6 tiers, 6 rarity ticket prints, and 6 bags rebuilt from the owner's reference sheets: Satchel, TicketPouch, Backpack, Tube, Sack and Wagon.
    - Templates are in `ServerStorage.AssetKit.{Gems, Tickets.Rarity, Bags}`. Every id is in `Assets/MANIFEST.md`.
    - The Blender build runs headless: `blender -b Assets/Blender/FWL_Phase03_TicketsAndTools.blend --python Assets/Blender/scripts/run_extension.py -- [--export] [--save] [--preview DIR]`.
  - Next: phase 04.
  - Tickets (regular 36 tris + gold 76, with printed detail) and all ten tools (smoothed: bevels and smooth shading) are in `Assets/`: the `.blend` source, rebuild scripts, two GLBs, two textures, and `MANIFEST.md` / `manifest.json` with tris and grip offsets.
  - Uploaded at the owner's request (group assets 86634259228339 tickets, 91521913312817 tools). Templates are in Gameplay `ServerStorage.AssetKit` (`Tools.<Id>`, `Tickets`). See `Assets/MANIFEST.md` "Roblox import status".
  - Regular tickets tint through `MeshPart.Color` via a `SurfaceAppearance` set to `AlphaMode.Overlay` (a plain TextureID draws see-through pixels black). Keep `RenderFidelity = Precise` on every asset clone, or the distance LOD drops pieces.
- The Gameplay place has Studio API access **on**, so its playtests use the real DataStore. `ServerStorage.TestProfileKey = "dev"` keeps Studio sessions on an isolated `TEST_dev_<userId>` key.
- The source of truth for scripts is Roblox Studio, which uses Team Create.

## Working rules for this project

- Follow the phases in order: 01, 02, 02B, 03–09. Read the phase `.txt`, look at **every** PNG in its folder, and read `OWNER_CHANGES.md` before starting.
- The owner's latest request wins over the prompt text, and the prompt text wins over the diagrams. Diagrams 06 and 07 still show the old 24-stud depth and 90 × 90 lobby.
- Do only the current phase, and report real tests. Don't publish, spend Robux, or delete places or data without the owner's OK.
- Ask design questions in plain chat with a recommendation. The owner answers directly.
