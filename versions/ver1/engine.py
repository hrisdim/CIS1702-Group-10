import json
import os
import sys

# note: possibly import time? sleep might help make the menus more readable
import time
# We imported time

	# note: add commenting during / after testing
	# remove notes and mention when fix has been made
	# josh made major fixes to code it now runs to win and loss
	# assign someone to time.sleep()

# Save location for current game and saved game data
# GAME_DATA_PATH = "game_data.json"
# SAVE_GAME_PATH = "save_game.json"

# REMOVE THIS AFTER TESTING
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
GAME_DATA_PATH = os.path.join(BASE_PATH, "game_data.json")
SAVE_GAME_PATH = os.path.join(BASE_PATH, "save_game.json")


#line by line slow printing function
def slow_print(text, delay=0.6):
	"""
	Prints text line-by-line with a delay for readability.
	"""
	if not isinstance(text, str) or not text.strip():
		return

	for line in text.split("\n"):
		print(line)
		time.sleep(delay)





def get_room(gd, name):
	""" Retrives the room data based on the room's name"""
	return gd.get("rooms", {}).get(name, {})


def find_by_name(list, name):
	""" Finds an item in a list of dictionaries based on its name key"""
	for it in list or []:
		if (it.get("name", "")).strip().lower() == name.strip().lower():
			return it
	return None


def npc_speech(gd, room_name, noun):
	""" Outputs the corresponding dialogue based on the npc's name """
	room = get_room(gd, room_name)
	npc_list = room.get("npc", [])
	npc = find_by_name(npc_list, noun)
	if npc is None:
		return "invalid input"
	else:
		slow_print(npc.get("dialogue", "")) # changed to slow print
		return "End of Dialogue"


def drop_item(gd, room_name, noun):
	""" Removes a valid item from the player's inventory and adds it to the current room's items"""
	room = get_room(gd, room_name)
	items = room.setdefault("items", [])
	if isinstance(noun, str) and noun.strip():
		for it in gd.get("inventory", []):
			if it.strip().lower() == noun.strip().lower():
				gd["inventory"].remove(it)
				items.append(it)
				print(f"Dropped {it}") # kept as fast print
				return None
			return "invalid input"
	return "invalid input"


def grab_item(gd, room_name, noun):
	""" Adds a valid item from the current room's items to the player's inventory """
	room = get_room(gd, room_name)
	items = room.setdefault("items", [])
	if isinstance(noun, str) and noun.strip():
		for it in items:
			if it.strip().lower() == noun.strip().lower():
				gd["inventory"].append(it)
				items.remove(it)
				print(f"Grabbed {it}") # kept as fast print
				return None
		return "invalid input"
	return "invalid input"


def interact(gd, room_name, noun):
	""" 
	Interaction with a puzzle in the current room.
	- Validation checks if puzzle exists and is not already done
	- Checks if puzzle requirements are met and returns if not
	- Marks puzzle as done and adds it to completed list
	- Adds puzzle reward to inventory if there is one
	- Consumes needed item from inventory if there is one
	- Checks for win/lose condition and exits game if met
	"""
	room = get_room(gd, room_name)
	puzzles = room.get("puzzles", [])
	puzzle = find_by_name(puzzles, noun)
	inventory = gd.get("inventory", [])
	if puzzle is None:
		return "invalid input"

	# check if puzzle has been previously completed
	if not puzzle.get("done", False):
		name = puzzle.get("name", "")

		# check if player meets requirements for puzzle
		need = puzzle.get("need", "")
		if need:
			if isinstance(need, str) and need.strip():
				hasneed = False
				for it in inventory:
					if it.strip().lower() == need:
						# consume item needed for puzzle
						inventory.remove(it)
						hasneed = True
						slow_print(f"You have used {need}") # changed to slow print
						break
				#checks if player has required item and returns if not
				if not hasneed:
					slow_print("Nothing happens") # changed to slow print
					return None
					
		# marks puzzle as complete
		puzzle["done"] = True
		if name and name not in gd.get("completed", []):
			gd.setdefault("completed", []).append(name)
			slow_print("You have completed the puzzle") #changed to slow print

		# add reward to inventory
		reward = puzzle.get("reward", "")
		if isinstance(reward, str) and reward.strip():	
			inventory.append(reward)
			slow_print(f"You have received {reward}") # changed to slow print

		

		# check for win/lose condition
		win = (gd.get("metadata", {}).get("win", ""))
		lose = (gd.get("metadata", {}).get("lose", ""))
		if name == win:
			print("You win!") # kept as fast print
			quit()
		if name == lose:
			print("You lose!") # kept as fast print
			quit()
		return None

	else:
		return "You have already completed this puzzle"


def save_and_quit(gd, room_name):
	""" Saves current game state to file and exits program """
	gd["saved room"] = room_name
	with open(SAVE_GAME_PATH, "w", encoding="utf-8") as f:
		json.dump(gd, f, indent=2)
	slow_print("Game saved. Quitting.") # changed to slow print
	quit()


def move_player(gd, room_name, noun):
	""" 
	Based on direction input, moves player to target room if possible.
	- Validates direction input
	- Checks if target room exists
	- Checks if any requirements to enter target room are met
	- Loads target room if all checks pass
	"""
	direction = noun.strip().lower()
	if direction not in {"north", "east", "south", "west"}:
		return "invalid input"

	current = gd.get("rooms", {}).get(room_name, {})
	target_name = (current.get(direction, "")).strip()
	if not target_name:
		return "invalid input"

	target_room = gd.get("rooms", {}).get(target_name)
	if not target_room:
		return "invalid input"

	requirement = (target_room.get("requirement", "")).strip()
	completed_puzzles = gd.get("completed", []) # Changed variable name to completed puzzles
	if requirement:
		if target_name in completed_puzzles: # Same thing here
			load_room(gd, target_name)
			slow_print(f"You have moved to the {target_name}") # changed to slow print
			return target_name
		if not any(it.strip().lower() == requirement.lower() for it in gd.get("completed", [])):
			slow_print("You can't go there yet.") # changed to slow print
			return None
		else:
			load_room(gd, target_name)
	else: # Added else statement as fallback incase a room has no requirement to enter 
			## not a fallback we just need it to load the room if there is no requirement
		slow_print(f"You have moved to the {target_name}") # changed to slow print
		load_room(gd, target_name) 


def parse_input(gd, action, room_name):
	"""
	Parses user input into verb and noun, then calls corresponding function.
	"""
	txt = action.strip()

	if not txt:
		return "invalid input"
	
	split_list = txt.split(" ", 1)
	verb = split_list[0].lower()
	noun = split_list[1] if len(split_list) > 1 else ""

	match verb:
		case "go":
			return move_player(gd, room_name, noun)
		case "grab":
			return grab_item(gd, room_name, noun)
		case "drop":
			return drop_item(gd, room_name, noun)
		case "check":
			return interact(gd, room_name, noun)
		case "talk":
			return npc_speech(gd, room_name, noun)
		case "help":
			print(gd.get("metadata", {}).get("help", "")) # kept as fast print cuz guide could be like a million years long
			return None
		case "quit":
			return save_and_quit(gd, room_name)
		case _:
			return "invalid input"


def load_room(gd, room_name):
	"""
	Main game loop for the current room.
	- Displays room description, exits, items, NPCs, puzzles, and inventory
	- Asks for user input
	- Parses input and calls corresponding functions
	- Loop continues until game is exited
	"""

	while True:
		room = get_room(gd, room_name)
		slow_print(room.get("desc", ""))  # first item changed to slow print for testing
		slow_print("There is a way:") # changed to slow print
		for direction in ("north", "east", "south", "west"):
			target = room.get(direction, "")
			if isinstance(target, str) and target.strip():
				slow_print(f"  - {direction.capitalize()}: {target.capitalize()}") # changed to slow print
		
		items = room.get("items", [])
		if items:
			slow_print("You spot the following items:") # changed to slow print
			for item in items:
				slow_print(f"  - {item}") # changed to slow print
			slow_print("") # changed to slow print
		
		npcs = room.get("npc", [])
		if npcs:
			slow_print("You talk to the following NPCs:") # changed to slow print
			for npc in npcs:
				slow_print(f"  - {npc.get("name", "")}") # changed to slow print
				slow_print(f"    {npc.get("desc", "")}") # changed to slow print
			slow_print("") # changed to slow print (idk if these blank things rlly need it but oh well)

		puzzles = room.get("puzzles", [])
		not_done = [p for p in puzzles if not p.get("done", False)]
		if not_done:
			slow_print("You can interact with:") #changed to slow print
			for p in not_done:
				name = p.get("name", "")
				if name:
					slow_print(f"  - {name}") # changed to slow print
			slow_print("") # changed to slow print

		slow_print("You have the following items in your inventory:") # changed to slow print
		for item in gd.get("inventory", []):
			slow_print(f"  - {item}") # changed to slow print
		slow_print("") # changed to slow print
		
		try:
			action = input("What do you do?\n")
		except EOFError:
			# exit if input stream closes
			save_and_quit(gd, room_name)
		result = parse_input(gd, action, room_name)

		if isinstance(result, str) and result.strip():
			if result == "invalid input":
				print("Please enter a valid action") # kept as fast print


def main_menu(gd):
	"""
	Displays main menu and handles loading/starting game.
	- Shows game title, description and help guide
	- Asks for user input to load saved game or start new game
	- Loads appropriate room based on user choice
	"""
	metadata = gd.get("metadata", {})
	print(metadata.get("title", "")) # all 3 kept as fast print
	print(metadata.get("desc", ""))
	print(metadata.get("help", ""))

	if os.path.exists(SAVE_GAME_PATH):
		while True:
			choice = input("Would you like to load your last game? (yes/no) ").strip().lower()
			if choice == "yes":
				# load saved game
				with open(SAVE_GAME_PATH, "r", encoding="utf-8") as f:
					sg = json.load(f)
				gd = sg
				gd["rooms"] = sg.get("rooms", {})
				gd["inventory"] = sg.get("inventory", [])
				gd["completed"] = sg.get("completed", [])
				gd["metadata"] = sg.get("metadata", {})
				saved_room_name = sg.get("saved room", None)
				if isinstance(saved_room_name, str) and saved_room_name in gd.get("rooms", {}):
					load_room(gd, saved_room_name)
					return
				
			if choice == "no":
				while True:
					choice = input("Would you like to start a new game? (yes/no) ").strip().lower()
					if choice == "yes":
						first_room_name =  next(iter(gd.get("rooms", {})), None)
						load_room(gd, first_room_name)
						return
					if choice == "no":
						return
					print("Please enter a valid answer") # kept as fast print
				break
			print("Please enter a valid answer") # kept as fast print
	else:
		while True:
			choice = input("Would you like to start? (yes/no) ").strip().lower()
			if choice == "yes":
				first_room_name =  next(iter(gd.get("rooms", {})), None)
				load_room(gd, first_room_name)
				return
			if choice == "no":
				return
			print("Please enter a valid answer") # kept as fast print


def main():
	"""
	Main function to start the game.
	"""
	with open(GAME_DATA_PATH, "r") as f:
		gd = json.load(f)
	main_menu(gd)
	

if __name__ == "__main__":
	main()

