import json
import os
import sys

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GAME_DATA_PATH = os.path.join(SCRIPT_DIR, "game_data.json")
SAVE_GAME_PATH = os.path.join(SCRIPT_DIR, "save_game.json")


# load json file
def load_json(path):
	with open(path, "r", encoding="utf-8") as f:
		return json.load(f)


# save json file
def save_json(path, data):
	with open(path, "w", encoding="utf-8") as f:
		json.dump(data, f, indent=2)


# game state container
class GameState:
	def __init__(self, gd: dict):
		self.gd = gd
		self.rooms = gd.get("rooms", {})
		self.inventory = gd.get("inventory", [])
		self.completed = gd.get("completed", [])
		self.metadata = gd.get("metadata", {})
		self.current_room_name = None
		saved_room = gd.get("saved room", None)
		
		if isinstance(saved_room, str) and saved_room in self.rooms:
			self.current_room_name = saved_room

	# get a room by name
	def get_room(self, name: str) -> dict:
		return self.rooms.get(name, {})

	# current room dict
	def current_room(self) -> dict:
		if self.current_room_name is None:
			return {}
		return self.get_room(self.current_room_name)

	# set current room name
	def set_current_room(self, name: str) -> None:
		if name in self.rooms:
			self.current_room_name = name
			self.gd["saved room"] = name

'''
def _names_list(lst, key):
	names = []
	for x in lst or []:
		val = x.get(key)
		if isinstance(val, str):
			names.append(val)
	return names
'''

# find by name (npc, puzzle)
def _find_by_name(lst, name):
	name_l = (name or "").strip().lower()
	for x in lst or []:
		if str(x.get("name", "")).strip().lower() == name_l:
			return x
	return None


# npc dialogue
def npc_speech(state: GameState, noun: str):
	room = state.current_room()
	npcs = room.get("npc", [])
	npc = _find_by_name(npcs, noun)
	if npc is None:
		return "invalid input"
	print(npc.get("dialogue", ""))
	return "end of dialogue"


# drop item in current room
def drop_item(state: GameState, noun: str):
    room = state.current_room()
    items = room.setdefault("items", [])
    item_index = next((i for i, it in enumerate(state.inventory)
                if str(it).strip().lower() == (noun or "").strip().lower()), None)
    if item_index is None:
        return "invalid input"
    item = state.inventory[item_index]
    items.append(item)
    del state.inventory[item_index]
    print(f"Dropped {item}")
    return None


# grab item if it's in the room
def grab_item(state: GameState, noun: str):
	room = state.current_room()
	items = room.setdefault("items", [])
	item_index = next((i for i, it in enumerate(items)
		 if str(it).strip().lower() == (noun or "").strip().lower()), None)
	if item_index is None:
		return "invalid input"
	item = items[item_index]
	state.inventory.append(item)
	del items[item_index]
	print(f"Grabbed {item}")
	return None

# interact with puzzle
def interact(state: GameState, noun: str):
    room = state.current_room()
    puzzles = room.get("puzzles", [])
    puzzle = _find_by_name(puzzles, noun)
    if puzzle is None:
        return "invalid input"

    if not puzzle.get("done", False):
        puzzle["done"] = True
        name = puzzle.get("name", "")
        if name:
            if name not in state.completed:
                state.completed.append(name)
        print("You have completed the puzzle")

		# add reward to inventory
        reward = puzzle.get("reward", "")
        if isinstance(reward, str) and reward.strip():
            state.inventory.append(reward)

		# consume needed item for puzzle
        need = puzzle.get("need", "")
        if isinstance(need, str) and need.strip():
            for i, it in enumerate(list(state.inventory)):
                if str(it).strip().lower() == need.strip().lower():
                    del state.inventory[i]
                    break

        return None

    else:
        return "You have already completed this puzzle"


# save and quit
def save_and_quit(state: GameState):
    state.gd["saved room"] = state.current_room_name
    save_json(SAVE_GAME_PATH, state.gd)
    print("Game saved. Goodbye!")
    sys.exit(0)


# show room info
def _print_room_overview(state: GameState, room: dict):
	print(room.get("desc", ""))
	# Exits
	for direction in ("north", "east", "south", "west"):
		target = room.get(direction, "")
		if isinstance(target, str) and target.strip():
			print(f"There is a way to the {direction}: {target}")
	# Items
	items = room.get("items", [])
	if items:
		print("You see the following items: " + ", ".join(map(str, items)))
	# NPCs
	npcs = room.get("npc", [])
	if npcs:
		print("You see the following NPCs:")
		for npc in npcs:
			print(str(npc.get("name", "")))
			desc = npc.get("desc", "")
			if desc:
				print(desc)
	# Puzzles (only shows those not done)
	puzzles = room.get("puzzles", [])
	not_done = [p for p in puzzles if not p.get("done", False)]
	if not_done:
		print("You see the following:")
		for p in not_done:
			puzzle_name = p.get("name", "")
			if puzzle_name:
				print(puzzle_name)
	# Inventory
	inv = state.inventory or []
	print("You have the following items in your inventory: " + ", ".join(map(str, inv)))


# check room requirement
def _requirement_satisfied(state: GameState, room: dict) -> bool:
	req = str(room.get("requirement", "")).strip()
	if not req:
		return True
	# inventory check
	req_l = req.lower()
	if any(str(it).strip().lower() == req_l for it in state.inventory):
		return True
	# completed exact or similar match (handles "a front door" vs "front door")
	for c in state.completed:
		c_l = str(c).strip().lower()
		if c_l == req_l or (c_l in req_l) or (req_l in c_l):
			return True
	return False


# move player
def move_player(state: GameState, noun: str):
	direction = (noun or "").strip().lower()
	if direction not in {"north", "east", "south", "west"}:
		return "invalid input"

	current = state.current_room()
	target_name = str(current.get(direction, "")).strip()
	if not target_name:
		return "invalid input"

	target_room = state.get_room(target_name)
	if not target_room:
		return "invalid input"

	if not _requirement_satisfied(state, target_room):
		print("You can't go there yet.")
		return None

	# Return the next room name to load
	return target_name


# parse user input
def parse_input(state: GameState, action: str):
	txt = (action or "").strip()
	if not txt:
		return "invalid input"
	parts = txt.split(" ", 1)
	verb = parts[0].lower()
	noun = parts[1].strip() if len(parts) > 1 else ""

	if verb == "go":
		return move_player(state, noun)
	if verb == "grab":
		return grab_item(state, noun)
	if verb == "drop":
		return drop_item(state, noun)
	if verb == "check":
		return interact(state, noun)
	if verb == "talk":
		return npc_speech(state, noun)
	if verb == "help":
		print(state.metadata.get("help", ""))
		return None
	if verb == "quit":
		return save_and_quit(state)
	print("Please enter a valid action")
	return "invalid input"


# room loop
def load_room(state: GameState, room_name: str):
	state.set_current_room(room_name)
	room = state.current_room()
	while True:
		_print_room_overview(state, room)
		try:
			action = input("\nWhat do you do? ")
		except EOFError:
			# exit if input stream closes
			save_and_quit(state)
		result = parse_input(state, action)
		if isinstance(result, str) and result.strip():
			target_room_name = result
			if target_room_name == "invalid input":
				print("Please enter a valid action")
			elif target_room_name in state.rooms:
				# moves to another room, restart loop with new room
				room = state.get_room(target_room_name)
				state.set_current_room(target_room_name)
				print("")
				continue
			else:
				pass


# first room name
def _first_room_name(gd: dict) -> str:
	rooms = gd.get("rooms", {})
	for k in rooms.keys():
		return k
	return ""


# main menu
def main_menu(state: GameState):
	md = state.metadata
	print(md.get("title", ""))
	print(md.get("desc", ""))
	print(md.get("help", ""))

	if os.path.exists(SAVE_GAME_PATH):
		while True:
			choice = input("Would you like to load your last game? (yes/no) ").strip().lower()
			if choice == "yes":
				# Load saved game
				gd_saved = load_json(SAVE_GAME_PATH)
				state.gd = gd_saved
				state.rooms = gd_saved.get("rooms", {})
				state.inventory = gd_saved.get("inventory", [])
				state.completed = gd_saved.get("completed", [])
				state.metadata = gd_saved.get("metadata", {})
				saved_room_name = gd_saved.get("saved room", None)
				if isinstance(saved_room_name, str) and saved_room_name in state.rooms:
					load_room(state, saved_room_name)
				else:
					# Goes to first room
					load_room(state, _first_room_name(state.gd))
				return
			if choice == "no":
				while True:
					start = input("Would you like to start a new game? (yes/no) ").strip().lower()
					if start == "yes":
						load_room(state, _first_room_name(state.gd))
						return
					if start == "no":
						return
					print("Please enter a valid answer")
				break
			print("Please enter a valid answer")
	else:
		while True:
			choice = input("Would you like to start? (yes/no) ").strip().lower()
			if choice == "yes":
				load_room(state, _first_room_name(state.gd))
				return
			if choice == "no":
				return
			print("Please enter a valid answer")


def main():
    gd = load_json(GAME_DATA_PATH)
    state = GameState(gd)
    main_menu(state)
	

if __name__ == "__main__":
	main()

