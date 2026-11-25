# Owner changes to the v6 prompt pack

The pack itself says the user's request comes before its written rules. These decisions override the matching parts of every phase prompt. Read this file before starting each phase.

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
