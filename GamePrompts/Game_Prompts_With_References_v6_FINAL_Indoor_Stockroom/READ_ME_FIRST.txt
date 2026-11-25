VERSION 6 + OWNER CHANGES (2026-11-25) — TWO PLACES, ENCLOSED TICKET-STORE STOCKROOM
This is the prompt handoff pack in use. It now includes the owner's changes of 2026-11-25; the original v6 text is preserved in the source zip. The change log is in GamePrompts/OWNER_CHANGES.md.

ORDER
1. If work has already started, read SEND_FIRST_IF_ALREADY_STARTED.txt.
2. Read 00_START_HERE/00_START_HERE.txt and _Reference_Info/CONTRACT_CURRENT.txt.
3. Do the phases in order: 01, 02, 02B, 03, 04, 05, 06, 07, 08, 09. Attach or inspect ALL PNGs in each phase folder. Finish and verify each phase before the next.
4. Phase 07 contains the full purchase design; phase 08 integrates UI and saving. Product setup can stay disabled while the rest of the game is built.

CURRENT DIRECTION
TWO Roblox places in one universe.
- LOBBY = the start place "Lottery-Game" (126779117472575), server size 16.
  - Players form parties in circles.
  - The leader sets FRIENDS or PUBLIC and a max size of 1–4.
  - Only the leader can press START; a 30-second auto-start starts when the party is created.
- GAMEPLAY = "gameplay" (81218982278176), server size 4, one reserved server per party.
  - It holds one enclosed ticket-store stockroom with solid walls and a complete roof over both zones: a smaller in-map lobby with the shops on the LEFT, and a much larger rectangular ticket pit on the RIGHT, with direct open access between them.
- Ladders are the normal way out of the pit.
- No Return-to-Lobby during the hunt; when the golden ticket is found, players choose LEAVE or RETURN TO LOBBY.

BLOCKOUT
- Pit 100 x 160 studs, 40.8 studs below the rim.
- In-map lobby 120 x 120.
- 10-stud rim.
- Roof underside 28 studs above the rim.
- Use shelves, ticket-stock boxes, teal/cream walls, simple roof beams and restrained warm lights.

PILE
- One shared pile per gameplay server.
- Each player who joins adds a batch of tickets; leaving never removes any.

SAVING
- Save Money, OwnedToolIds and UpgradeLevels; only the Gameplay place saves.
- Never save pit state.
- Bags, inspection state and discovery counts are session-only. Exchange the bag before leaving.

PURCHASES AND REWARD
- Money can be earned, or bought in fixed Robux packs.
- Tools and permanent upgrades can be bought with earned money OR directly with Robux; both routes grant the same benefit.
- Exact prices, product IDs and pack amounts are configuration to set later. No paid random outcome.
- The golden-ticket finder gets something special; the exact reward is intentionally undecided.
  - Build the server-only hook now, disabled by default.
  - Do not invent a reward, show 'reward granted' when none exists, or create promised future claims.

TOOLS AND UPGRADES
- Ten original Blender tool designs.
- Ride-on equipment uses a clear pad below; riders dismount before climbing.
- Permanent upgrades: Movement Speed, Dig Speed, Reach, Carry Capacity and Scratch Speed. Caps and prices live in configuration; no claimed playtested balance.

FILES AND REFERENCES
- 00 context; 01 foundation; 02 movement/ladders; 02B Lobby place/parties/travel; 03 Blender assets; 04 in-map lobby; 05 shared pile/gold/hunt end; 06 pit environment; 07 tools/upgrades/purchases; 08 UI/saving; 09 QA.
- The original four ticket/tool sheets are preserved.
- Diagrams 06 (top-down) and 07 (section) still show the older 24-stud depth and 90 x 90 lobby: the written values win.
- Order of authority: owner request > CONTRACT_CURRENT/phase text > measured diagrams > illustrative concept details.
- The TikTok video itself was not viewed (login/birthdate gate). No video dimensions or unseen details are claimed.
- See _Reference_Info for source notes, image prompts, pending owner decisions and official Roblox implementation references.
