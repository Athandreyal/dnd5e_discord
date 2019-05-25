# import dnd5e_enums as enums
# import dnd5e_character_classes as character


# root 'thing' class for the dnd world - if it has a cost, and can be held in an inventory somewhere, it begins here
class Item:

	# qty is the quantity of this item you currently interact with - someone has to know how many there are.
	# enum_type is an enum referencing exactly what this is
	def __init__(self, name, cost, weight, qty, enum_type, equip_to, function):
		self.name = name
		self.cost = cost
		self.weight = weight
		self.qty = qty
		self.type = enum_type
		self.function = function
		self.equip_to = equip_to

	# todo: item sales for economy purposes
	# todo: write item function reference code
	#  todo: write item registration code - if the function needs to be in a list on the target, make sure it puts
	#   itself there
