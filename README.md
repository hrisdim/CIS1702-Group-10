# cis1702-cw2-cyberpython2077

Project Brief 3: Text-Based Adventure Game Engine

- Project Goal: Create a reusable "engine" for a text-based adventure game. Instead of hard-coding the story, the engine should load the game's map, rooms, and interactions from a structured data file (e.g., game_map.json).

- Key Functional Requirements:

  - On startup, the program must load the entire game world from a JSON file. This file will define rooms, descriptions, items, and connections between rooms (e.g., "north" from the "Hall" leads to the "Kitchen").

  -  The player must be able to navigate between rooms using commands like go north, go east, etc.

  - The player must have an inventory and be able to get item and drop item.
  - The program must parse user input to understand commands and arguments (e.g., verb: "go", noun: "north").

  - The game state (player's current location, inventory) must be tracked accurately.

  CIS1702 – Programming 1 (25/26) 5

  - The program must handle invalid commands and impossible actions gracefully (e.g., "You can't go that way.").

  - Include a "help" command that lists available actions.

  - The game must have a clear win or lose condition defined within the data file.

- Possible Extensions:

  - Implement "locked" doors that require a specific item from the inventory to open.

  - Add characters (NPCs) that the player can interact with using a talk to command.
  - Allow the player to save and load their game progress to a separate file.

- Marking Focus Areas: Strong separation of game logic ("engine") from game data ("JSON file"), effective use of complex data structures (nested dictionaries/lists), a robust input parser, and logical state management.

# Flowchart

<img width="2492" height="2382" alt="finishedflowchart" src="https://github.com/user-attachments/assets/821990bf-aa7a-4b4c-85a4-d7ce38478cff" />
