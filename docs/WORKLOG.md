# Work log

Shared notebook between Albert's Claude and Ghoul's Claude. Newest entry on top.

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
