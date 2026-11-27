# Work log

Shared notebook between Albert's Claude and Ghoul's Claude. Newest entry on top.

## 2026-11-27 (evening) — Albert's Claude: Studio TEST PANEL (both places)

**Done (Studio):** press **P** in a Studio play-test (or the TEST tab, bottom right).
- Gameplay (`Server.TestPanel`, started from `Hunt.start` only in Studio): cash +100 .. +1M / 0, gems (saved), any of the 10 tools or all, forever tools / bags (saved, like a Robux buy), pick any bag, fill the bag (real odds / rare mix / one of each rarity), sell, empty, hand upgrades (hunt levels and saved gem levels, +1 / MAX / 0), golden ticket (SHOW IT beam, GO THERE, UNCOVER IT, FIND IT NOW), +1 join batch, teleport to stockroom / pit, fast walk, save now, reset my save.
- Lobby (`Lobby.TestPanel`, started in `Lobby.Main`'s Studio block): gems, forever hand levels, forever tools / bags, teleport to spawn / Upgrades booth / party ring 1, save now, reset my save.
- One client script, `StarterPlayerScripts.TestPanelClient`, byte-identical in both places (12873 chars, hash 1616539340). It only draws what the server sends, so each place has its own buttons.
- Small edits: `Gold.testClaim(player)` (Studio-only, runs the normal claim with all its checks); `Lobby.Main` now starts Parties BEFORE PlayerData (in Studio, PlayerData's DataStore check made PartyClient warn "Infinite yield ... PartyRemotes").

**Tested in Play:** every gameplay button (mouse clicks and remote calls), the SURE? double tap, gold beam, find-it-now (banner, LEAVE / RETURN panel, +25 gems); every Lobby button; the Lobby loaded the gems the gameplay test saved. No errors in Output (Lobby still shows the old streaming warning for `Circle1`).

**Ghoul should know:** the panel is safe live (the remote is never created outside Studio; the client deletes itself). SAVED buttons change your real profile in Studio. FIND IT NOW and a real Studio claim both count a win on the leaderboard data.

## 2026-11-27 (later) — Albert's Claude: Lobby saving, gem Upgrades booth, teleport handoff, phase 09 checks

**Done (Studio, both places):**
- Lobby loads and saves profiles: identical copies of the Data modules in `Lobby.Data`, plus `Shared` Config (schema 3), ToolCatalog, BagCatalog, HandUpgradeCatalog, HuntTuning (all verified byte-identical with a hash). Includes Ghoul's newer pile tuning (MoundLayers 18, NoiseLayers 4).
- Gem Upgrades booth works (`Lobby.GemShop` + `BoothClient` Upgrades panel).
- Handoff: `PlayerData.release` / `reload` (both places); wired into `Lobby.Parties.beginTravel` and gameplay `PostGold` RETURN TO LOBBY.
- `Session.owns`: the starter grabber is always owned.
- `Lobby.Main` starts PlayerData and GemShop; ProcessReceipt there still answers NotProcessedYet.

**Tested:** Lobby loads the same save (149 gems); bought Reach level 1 for 15 gems -> 134; then the gameplay place loaded Gems 134 + Reach 1 and the grabber reached 13.5 studs; release -> "released", reload -> "ready" with gems kept; fuzzing every gameplay remote (nothing granted, 200-grab spam = 1 grab).

**Not tested (needs publishing / the owner):** a real Lobby -> Gameplay -> Lobby teleport (Studio loads the last SAVED place versions, which don't have this code yet), 2-player party, phones.

**Ghoul should know:** the Lobby's `Infinite yield possible on Circle1` warning in PartyClient is from map streaming (the rings arrive a moment later); it was there before.

## 2026-11-27 — Albert's Claude: phase 05 pile, phase 07 tools + economy, counter windows (Gameplay place)

**Done (in Studio, Team Create; scripts live there, not in this repo):**
- Real ticket pile (`Server.Pile` + `PileClient`), join batches, golden ticket with one-winner hand claim (`Server.Gold`), hunt-end gems.
- All ten tools work (`Server.Dig`, `Server.Tools`, `ToolClient`), including the Rotary Sweeper and the Ride-on (pad start, sit, drive).
- Counter windows for TOOLS, BAGS, UPGRADES, SELL, SCRATCH (`StationClient`), HUD (`HuntHud`), shared look (`HuntUi`).
- Save schema 3: Gems, permanent HandLevels, OwnedBagIds. Old saves migrate. Gems tested: they persist across sessions.
- Robux: ProductCatalog rebuilt (GemPack / Tool / Bag), fulfillments registered, paid buttons off.
- Small edits in Ghoul's modules: `Main` (one line: `Hunt.start()`), `Session` (`handLevel`, `addGems`, `BagMix` attribute), `Shop.buyHand` (counts gem levels), `PlayerData` (Gems / PermHand_ attributes), `Schema`, `Config` (SchemaVersion 3 only), `ProductCatalog`.

**Tested in Play:** every hand tool (shapes and layer counts), sweeper while walking (220 tickets), ride-on refused off the pad and driving on it (filled an 800 Wagon), gold claim (banner + LEAVE / RETURN panel + win credit + gems), buying a tool / bag / hand level from the windows, server refusals (too far, wrong tool, smaller bag, away from counter), unknown Robux product left pending.

**Next (Albert's Claude):** Lobby loads/saves profiles with the same Data modules + the gem Upgrades booth; phase 09 security and performance checks.

**Ghoul should know:**
- `Config` changed (SchemaVersion 3). The Lobby's copy must match before the Lobby saves anything, or it will refuse schema-3 profiles. I'll copy it when I do the Lobby.
- The HUD and windows are working versions; restyle freely, keep the remote calls (`ShopRemotes.Request`, `ToolRemotes.*`, `HuntEvent`).
- All tuning numbers are TEST in `Shared.HuntTuning`.
