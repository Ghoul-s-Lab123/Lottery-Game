# Owner changes to the v6 prompt pack

The pack itself says the user's request comes before its written rules. These decisions override the matching parts of every phase prompt. Read this file before starting each phase.

## 2026-11-26, polish pass (party interaction, record wall, flicker, attendants)

1. **No world text at the rings.** The four rings are painted on their own office-floor tiles (`CircleN.Floor`).
   - A ring tints amber while it holds a party.
2. **Parties are created and joined deliberately.** Walking into a ring no longer creates a party.
   - Each client shows ONE ticket-style prompt chip for the nearest eligible ring, at its front edge, within 8 studs.
     - It reads "Create party" on an empty ring, or "Join party · n/max" for a party you're allowed to join.
     - Keyboard E and gamepad X work natively; touch taps the chip (`StarterPlayerScripts.PromptChip`).
   - "Create party" opens a ticket-shaped setup panel (Access Public/Friends, Party size 1–4, one amber "Create party" button, ×).
     - Opening the panel reserves nothing.
     - The server claims the ring atomically (`Request "Create", ring, privacy, size`) and places the host inside.
   - Joining never opens host settings.
   - In a party the view stays clear apart from a small strip: one countdown line, Start / Settings (host), Leave.
     - Disbanding a party that has other members asks for a red confirm.
   - After leaving, the same ring stays quiet until the player steps away and comes back.
3. **Record wall** behind the spawn.
   - Timber case with a cap, two legs, a shared ticket crest, and brass-rimmed header plaques (trophy / ticket stubs / stopwatch).
   - Gold, silver and bronze rank badges. Long names are cut off with "…".
   - Empty state: one paper slip per section ("First win still up for grabs", "First ticket collector goes here", "Set the first time").
4. **Flicker fixes**, found by a coplanar-face scan:
   - Awning stripes overlapped by 0.02 studs on one plane.
   - Ring plates sat 0.06 above the floor.
   - The walkway bands were stacked on the paving.
   - The compass layers were 0.06 apart; they're now ≥ 0.12.
   - The cubby uprights' tops were flush with the top shelf.
   - The Upgrades posts and back wall were flush with the deck edges.
   - The marquee uplights floated in front of the header.
5. **Attendants**: static, non-colliding, part-built R6 figures on 1-stud platforms behind the counters.
   - Mechanic at Upgrades; dispatcher at Classes.
   - Each booth keeps its single counter prompt.
6. **Blender assets** in use: Ticket (92 tris), TicketRoll (102), Wrench (172). The owner imported them.
   - They live in `ServerStorage.LobbyKit.Meshes`, and LobbyBuilder clones them (part-built fallback only if a mesh is missing).
   - Uses: 6 tickets (marquee, office crest, board crest and backing, 2 stub emblems), 22 rolls, 1 wrench. About 3,000 mesh triangles in total, and no CSG left.

## 2026-11-26, late (Lobby redesign: "neighborhood ticket courtyard at dusk"). Replaces the party boxes and the 4-booth plaza below.

1. **Generated lobby.** `ServerStorage.LobbyBuilder` (edit-time) builds the only `Workspace.LobbyMap`; re-running it replaces the map. Façade templates live in `ServerStorage.LobbyKit`.
2. **Compact layout.**
   - The compass spawn sits at the origin, facing +Z toward the golden-ticket marquee.
   - The open-front ticket office is straight ahead, with **4 party rings of radius 5.5** (`Config.Party.CircleCount` / `CircleRadius`). The owner changed this from 6 smaller rings the same evening.
   - Classes is on the screen-left (+X) and Upgrades on the screen-right (−X).
   - The three-section leaderboard is directly behind the spawn.
   - Measured walk (R6, walk speed 16): 2.22 s to the inner rings, 2.58 s to the outer rings.
   - The front has corner posts only, because inner posts hid the outer ring labels from the spawn.
3. **Party stations are text-only.** Each is a thin white floor ring plus a floating label: `0/4 · Touch to create a party`, `n/max · Join party` (`· friends only` for FRIENDS parties), `Party full`, and `Teleporting in N...` for the last 10 s (`Config.Party.DepartingLabelSeconds`).
   - There are no map thumbnails, posters or voting.
   - The party rules are unchanged, including LEAVE-only exit: an invisible ring fence blocks only members.
4. **Exactly two booths.**
   - **Upgrades** lists `UpgradeCatalog`. Purchases aren't open: phase 07 isn't built and the Lobby still loads no profiles.
   - **Classes** shows an honest "No classes yet". The project has no class data, so none were invented.
   - The Tools, Daily Gift and Cash Store booths are gone.
5. **Lifetime leaderboards** (Total Wins, Tickets Collected, Time Record).
   - Profile schema v2 adds `Stats = { Wins, TicketsCollected, BestRunSeconds }`. This extends "save only Money, OwnedToolIds, UpgradeLevels".
   - `Gameplay Server.RunStats` credits the WHOLE TEAM on `HuntState.Resolved` (owner decision 2026-11-26).
     - Every party member still on the server when gold is found gets +1 Win.
     - Each member's Time Record candidate is their own time from arriving on the server to gold being found.
     - Members who left earlier get nothing.
     - The finder's separate special reward is still TBD (pending item 1).
   - Phase 05 must call `RunStats.addCollected(player, n)` when tickets enter the bag. Spending never lowers that total.
   - The ordered stores in `Config.Leaderboards` are indexes only. Studio sessions use the `TEST_<TestProfileKey>_` copies.
   - The Lobby reads them in `Lobby.Leaderboards` and shows "No records yet" when a store is empty.

## 2026-11-26 (Lobby look and party boxes)

1. **Lobby is a decorated town plaza plus a lottery store.** Players spawn OUTSIDE in an enclosed plaza in front of the store "Lucky Ticket Co.", which has a giant glowing "FIND THE GOLDEN TICKET!" ticket on its roof. Buildings close the plaza on every side: players must never see the void. The camera max zoom is 40.
2. **Shop booths are outside, next to the spawn, and they must WORK.** This overrides "the Lobby has no shops or economy" and "the Lobby never claims or saves profiles". The booth list is pending (OWNER_DECISIONS_PENDING item 7). UPGRADES is confirmed. The booths are built but not wired yet.
3. **Party circles became party boxes** inside the store: rectangular rooms with transparent white walls and an open entrance facing the aisle.
   - Walking in creates or joins a party, as before.
   - Once in a party, a player can leave only with the LEAVE button (or by disconnecting). Walking out no longer leaves: the door blocks members, and a member found outside is put back.
   - The leader pressing LEAVE disbands the party.
   - Each box has a screen showing the leader, the player count with slot dots, the timer, and PUBLIC / FRIENDS ONLY.
4. **Later the same day (rebuild, Lobby v31):**
   - Party boxes are bigger (24 x 22) and built into the store's side walls.
   - Each box has NO sign above it, only a big 3D block numeral (1-6). The timer, player dots and privacy are on a screen INSIDE the box.
   - The map was rebuilt to look designed rather than "AI generated", using the composition rules in the LihFolk vault: one hero (the golden ticket), modular town buildings with varied roofs, market kiosks with 3D roof icons, and no glowing floor pads.

## 2026-11-25 (latest decisions; earlier same-day items 1 and 2 were replaced)

1. **Two places in one universe.** This overrides v6's "ONE Roblox place", "no separate gameplay place, party-travel gate, TeleportService flow or reserved session" and "do not add back party matchmaking or private party pits".
   - **Lobby place:** the start place (Lottery-Game, id 126779117472575), because the start place can't be changed. Server size 16. Players form parties of up to 4 here, then the party teleports together.
   - **Gameplay place:** a new place in the same universe, not created yet. Server size 4. One private (reserved) server per party. It holds the stockroom map: the in-room lobby with shops, upgrades, exchange and inspect, plus the ticket pit.
   - Both places share the same saved profile (Money, OwnedToolIds, UpgradeLevels). The session lock already covers the handoff when a player teleports.
   - The shops stay in the in-room lobby of the Gameplay place.
2. **Ladders stay.** Two full-height ladders on the west pit wall at Z -24 and +24, as in v6. The "UI teleport instead of ladders" idea was dropped.
3. **Pit 1.7 times deeper.** The bottom is at Y = -40.8 (was -24). The opening is still 100 x 160 and the roof underside is still Y = +28.
4. **In-map lobby 120 x 120** (in the Gameplay place). It spans X -130..-10 and Z -60..60, and still adjoins the west rim directly. Spawn is at (-115, 0, 0), facing the pit.
5. **The pile grows with players.** Each player who joins the party's gameplay server adds a batch of tickets to the shared pile, placed on the surface and never over the ladder landings or the equipment pad. Leaving never removes tickets. This overrides:
   - Phase 02: "their arrival must not generate or resize a pile"
   - Phase 05: "workload independent of joins/leaves"

   The batch size, the starting pile size and the maximum are test numbers to set in phase 05. Gold rules are unchanged: one gold ticket per pile, and a join's batch never moves it.
6. **Parties (Lobby place).**
   - Walking into a circle creates a party, and that player becomes the leader.
   - The leader picks FRIENDS (only the leader's friends can join) or PUBLIC (anyone can join), and a max size of 1, 2, 3 or 4.
   - Only the leader has a START button.
   - A 30-second timer starts when the leader creates the party. If it hits 0, the party is teleported automatically.
   - The whole party goes to a fresh private Gameplay server.
   - The Gameplay place ID is 81218982278176. Server sizes are set by the owner: Lobby 16, Gameplay 4.
7. **Getting back to the Lobby.**
   - During the hunt, a player has to leave the game.
   - Only after the golden ticket is found do all players get two options: LEAVE or RETURN TO LOBBY.
   - This replaces v6's automatic refill after gold.
8. **Prompt files updated.**
   - Every phase .txt now ends with `_Reference_Info/CONTRACT_CURRENT.txt`.
   - New phase `02B_Lobby_Place_Parties_and_Travel`.
   - Open questions with defaults are in `_Reference_Info/OWNER_DECISIONS_PENDING.txt` (items 5–12).
   - The original v6 wording is still in the source zip.
9. **The map is still a blockout.** The final look comes from phases 03, 04 and 06.
