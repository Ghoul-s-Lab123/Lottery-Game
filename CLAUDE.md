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

## Phase 05 / 07 / 04-scripting (Albert's Claude, 2026-11-27, Gameplay place, all tested in Play)

Work split (Albert's list, 2026-11-27): Albert's Claude = gameplay systems (05, 07, 04 scripting, 08 saving, 09 checks); Ghoul = look, assets, owner jobs. The HUD and counter windows below are working first versions; Ghoul's phase 08 screens may restyle them (`HuntUi` holds the shared look).

- **Pile** (`Server.Pile`): height field, 50 x 80 columns of 2 x 2 studs, 0.5-stud layers; one layer = one ticket. Content per layer from a per-server seed (Ordinary / rarity / `Gem_<tier>`), so nothing per ticket is stored. Columns are server Parts in `Workspace.Pile` (attribute `Top` = special top content); KeepClear zones stay empty and the pile slopes down to them (`MaxStep` 2 layers), so ladders and the equipment pad stay reachable. Tickets slide (no column > 2 layers above a neighbour). The edit-time `TicketBedPreview` is destroyed only in the running server. Join batch: +2,500 tickets per admitted player, never on the gold column, nothing after gold.
- **Gold** (`Server.Gold`): 5-10 layers deep; a glint shows within 3 layers; exposed = lies on top with a hold-E "Claim" prompt. First valid claim wins (flag set before any yield), `HuntState.resolve(finder)`; `Gold.grantFinderReward` is the disabled reward hook (shows `Config.GoldenReward.DevMessage`). Hunt-end gems: tickets this hunt / 20 + team bonus 25.
- **Dig** (`Server.Dig`): the one collection pipeline. Checks equipped owned tool, alive, not on a ladder, cooldown, reach to the real column top, bag room; tickets -> bag + `RunStats.addCollected`, gems -> saved `Gems`. Shapes per `ToolCatalog.Action`; hand upgrades (cash this hunt + gems forever, capped at MaxLevel) only change the Ticket Grabber.
- **Tools** (`Server.Tools`): owned tools become Roblox Tools from `AssetKit.Tools`. **Nine tools** since 2026-11-28: the Leaf Blower was removed (Albert; id `LeafBlower` retired, never reuse it; its model is in `ServerStorage._Backups.Retired_LeafBlower_2026_11_28`). Rotary Sweeper is pushed in front; Ride-on starts ANYWHERE (no equipment-pad rule since 2026-11-28), you sit (the character's own sit animation; this place is **R15**) and drive with normal controls; it leaves on unequip / ladder / death. Both machines collect standing still too (`Dig.sweep` has no speed check) and only where there are tickets. Both hands hold them (`ToolMotion.machineGrip`: sweeper bar ends, Ride-on wheel at 9 and 3 o'clock; the Ride-on's steering wheel was made 1.6x wider so two blocky hands fit). In first person the machine is kept solid (`HandView` sets LocalTransparencyModifier 0 after the camera fades your character) and your hands on it are drawn at 60 %. Bag capacities +40 % (2026-11-28): 35 / 70 / 140 / 280 / 560 / 1120. Worn bag on the UpperTorso. Copies AssetKit previews to `ReplicatedStorage.HuntAssets` at runtime.
- **Clients**: `PileClient` (ticket meshes on column tops, rarity tickets, spinning gems), `ToolClient` (click/tap, hold repeats, aim ring, flying tickets), `HuntHud`, `StationClient` (the 5 counter windows from `StationPrompt`), `HuntUi` (shared look, toasts).
- **Save schema 3** (`Config.Data.SchemaVersion = 3`, `Schema`): adds `Gems`, `HandLevels` (permanent), `OwnedBagIds`; schema 2 profiles migrate (fields start empty). The Lobby must use the same Data modules before it saves.
- **Robux**: `ProductCatalog` rebuilt for the rework: kinds `GemPack`, `Tool`, `Bag` (cash packs and old upgrade targets removed; none was ever configured). Fulfillments registered in `Server.Hunt`. Duplicate Tool / Bag = `DuplicateFallbackGems` (owner sets; unset = not sellable). No ids, so every paid button stays off ("Forever with Robux: not on sale yet").
- **Tuning**: every pile / gem / rarity / tool-feel number is TEST in `Shared.HuntTuning` (kept out of Config so Config stays identical in both places).
- **Studio test hook**: `ServerStorage._HuntDev:Invoke(action, userId, ...)`: Gold, Uncover, Use, Give, Sell, SetBag, Gems, Receipt, Total, Release, Reload.
- **Handed tools (2026-11-28, Albert's Claude)**: LEFT hand = tool, in first person AND on the body others see. **Only the Ticket Grabber puts tickets in the RIGHT hand** (a compact stack; `ToolMotion` `Hand = true`); every other tool flicks its load over the left shoulder into the bag on the back (`WornBag`; first person: up and out of view at the top left), and the right arm is left to the normal animations (Albert, 2026-11-28). One table, `Shared.ToolMotion` (per tool: working end `Tip`, `Style`, `Cycle`, `Contact`/`Release` shares, `Weight`, rest poses `View` (camera space) and `World` (root space), `Reach` cap, stack sheets cap 8 at 0.45 scale). Server: hand tools have no Handle (`RequiresHandle = false`, part `Body`) and a `LeftGrip` weld to the LeftHand's LeftGripAttachment while equipped (`Server.Tools.holdLeft`); `Dig.stats` caps reach with `ToolMotion.reach` (Scoop 6.5, Rake 5.5, Broom 8, Shovel 8.5; grabber telescopes, vacuums / blower keep range). Client: `ArmIK` (two-bone R15 IK; this place's rig uses **AnimationConstraint** joints, `Att1 = Att0 * Transform`, written in PreSimulation), `ToolStroke` (stroke curves per style), `TicketStack` (the hand stack; rises only when a ticket lands), `HandView` (first person: cloned forearm cuffs + hands, shirt via `TextureID = ShirtTemplate`, full-size tool, grabber jaws + telescoping rod; replaces the old `ViewModel`, kept), `WorldRig` (everyone else's body pose from replicated state only: held Tool, `Machine`, `BagCount`, and pile deltas with `by`; their tickets wait on the pile until their working end arrives). `ToolClient` predicts as before but hands the tickets to `HandView.stroke`; `PileView.PutBack` lets go of tickets the server refused; `PileView.Moved` passes `by`. Studio test switches: `_HandViewTest:Invoke(speed)` (0 freezes the first-person stroke; returns `U` = stroke progress), Workspace attributes `RigSelfTest` (your own strokes go to your body, as others see it) and `RigTimeScale`; `_WorldRigTest:Invoke(userId)` returns `U` and each flight's state. To look at yourself from outside: Humanoid.AutoRotate = false (first person turns you to face the camera) and LocalTransparencyModifier 0 every frame.
- **TEST PANEL (Studio only, both places)**: press **P** (or the TEST tab, bottom right). One client script `StarterPlayerScripts.TestPanelClient` (byte-identical in both places) draws whatever buttons the place's server module sends over `ReplicatedStorage._TestPanel` (RemoteFunction, only made when `RunService:IsStudio()`; live servers never create it and the client deletes itself). Gameplay: `Server.TestPanel` (started from `Hunt.start`): cash, gems, every tool, bags + fills, hand levels (hunt and forever), golden ticket (show / go / uncover / find it now via `Gold.testClaim`), join batch, moves, save. Lobby: `Lobby.TestPanel` (started in `Lobby.Main`'s Studio block): gems, forever hand levels and items, moves, save. Buttons marked SAVED write the real profile (Studio has API access); red ones ask "SURE?". FIND IT NOW counts a real win. Add a button = one line in the place's `spec()` + a branch in `act()`.
- **Lobby saving (phase 08)**: the Lobby loads/saves profiles with IDENTICAL copies of the Data modules (`ServerScriptService.Lobby.Data.{Schema, ProfileStore, PlayerData, MockDataStore}`) and of `Shared.{Config, ToolCatalog, BagCatalog, HandUpgradeCatalog, HuntTuning}`. Change one place's copy = change the other (check with a length + hash compare). `Schema.serialize` is the save whitelist: a mismatch between places drops fields.
- **Teleport handoff**: `PlayerData.release(player)` saves and drops the lease before a teleport; `PlayerData.reload(player)` claims again if the teleport fails. Used by `Lobby.Parties.beginTravel` (all members, in its own thread, max 8 s) and `Server.PostGold` RETURN TO LOBBY. The starter Ticket Grabber is always owned (`Session.owns`), even during a handoff.
- **Gem Upgrades booth** (Lobby): `Lobby.GemShop` (`GemShopRemotes.Buy`: profile ready, at the booth, one mutation takes gems + adds the permanent level, then saves); `BoothClient`'s Upgrades panel sells the 3 hand upgrades (prices `HuntTuning.HandGems`, TEST). Classes booth unchanged (no class data).
- **Phase 09 checks done**: remote fuzzing (bad types, NaN / huge vectors, wrong tool, 200 grabs in one frame = 1 grab), shop requests away from counters refused, unknown Robux product left pending, server pile cost ~0.05 ms / frame. Not done: phone / real-device frame rate, 2-player and published teleport tests (owner list).

## Working rules for this project

- Follow the phases in order: 01, 02, 02B, 03–09. Read the phase `.txt`, look at **every** PNG in its folder, and read `OWNER_CHANGES.md` before starting.
- The owner's latest request wins over the prompt text, and the prompt text wins over the diagrams. Diagrams 06 and 07 still show the old 24-stud depth and 90 × 90 lobby.
- Do only the current phase, and report real tests. Don't publish, spend Robux, or delete places or data without the owner's OK.
- Ask design questions in plain chat with a recommendation. The owner answers directly.
