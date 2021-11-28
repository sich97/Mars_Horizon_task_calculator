import itertools
import random

REGULAR_RESOURCE_NAMES = {
    "comms": "Comms",
    "navs": "Navs",
    "data": "Data",
    "power": "Power"
}

# TODO: Missing crew resource as well
SPECIAL_RESOURCE_NAMES = {
    "heat": "Heat",
    "drift": "Drift",
    "thrust": "Thrust"
}


class Resource:
    """
    The base class for all resource types, such as Comms, Navs, Data, Heat, Drift, Thrust
    """

    name: str
    value: int
    min_value: int
    max_value: int

    def __init__(self, name: str, value: int = 0, min_value: int = 0, max_value: int = 999):
        self.name: str = name
        self.value: int = value
        self.min_value: int = min_value
        self.max_value: int = max_value

    def is_valid_value(self) -> bool:
        """
        Checks if the numerical validity of the resource value based on init parameters
        """
        return self.min_value <= self.value <= self.max_value


class Command:
    """
    Contains a ratio for exchanging input resources into output resources
    """

    name: str
    input_resources: dict[str, type(Resource)] = {}
    output_resources: dict[str, type(Resource)] = {}

    def __init__(self, name: str,
                 input_resources: dict[str, type(Resource)], output_resources: dict[str, type(Resource)]):

        self.name: str = name

        for input_resource_name, input_resource in input_resources.items():
            self.input_resources[input_resource_name]: type(Resource) = input_resource.copy()

        for output_resource_name, output_resource in output_resources.items():
            self.output_resources[output_resource_name]: type(Resource) = output_resource.copy()

    def __str__(self) -> str:
        output: str = self.name + " [Command]" + "\n\t" \
                      + "Input resources: " + str(self.input_resources) + "\n\t" \
                      + "Output resources: " + str(self.output_resources) + "\n"
        return remove_trailing_newlines(output)

    def copy(self) -> type(__name__):
        input_resources_copy: dict[str, type(Resource)] = {}
        for input_resource_name, input_resource in self.input_resources.items():
            input_resources_copy[input_resource_name]: type(Resource) = input_resource.copy()

        output_resources_copy: dict[str, type(Resource)] = {}
        for output_resource_name, output_resource in self.output_resources.items():
            output_resources_copy[output_resource_name]: type(Resource) = output_resource.copy()

        return type(self)(self.name, input_resources_copy, output_resources_copy)


class Turn:
    """
    Contains a set of commands up to a maximum specified amount.
    Also contains a dictionary of the current resources, which is the result of executing all the commands in sequence,
    starting with a set of starting recourses specified in the init. This current resources dictionary gets updated each
    time a new command is appended to this object.
    Whenever the last possible command is appended (determined by the maximum specified in init),
    the next_turn function gets called on every item in current_resources, which is populated by subclasses of Resource.
    """

    max_commands: int
    current_resources: dict[str, type(Resource)] = {}
    commands: list[Command] = []

    def __init__(self, starting_resources: dict[str, type(Resource)],
                 max_commands: int, commands: list[Command] = None):

        if commands is None:
            commands: list[Command] = []

        self.max_commands: int = max_commands

        for starting_resource_name, starting_resource in starting_resources.items():
            self.current_resources[starting_resource_name]: Resource = starting_resource.copy()

        if len(commands) < self.max_commands:
            self.commands: list[Command] = [command.copy() for command in commands]

    def __str__(self) -> str:
        output: str = "[Turn]: "
        for command in self.commands:
            output += "\n" + indent_string(str(command))
        output += "\n"
        return remove_trailing_newlines(output)

    def __len__(self) -> int:
        return len(self.commands)

    def copy(self) -> type(__name__):
        commands_copy: list[Command] = [command.copy() for command in self.commands]
        resource_copy: dict[str, type(Resource)] = {}
        for resource_name, resource in self.current_resources.items():
            resource_copy[resource_name]: type(Resource) = resource.copy()
        return type(self)(resource_copy, self.max_commands, commands_copy)

    def append(self, command: Command) -> bool:
        """
        As long as there is room for one more, this function appends a given command to the local list of commands and
        applies the command's changes to the resource pool (current_resources).
        If, after appending this command, the length of local commands has reached the specified limit, the turn is
        considered complete, and the next_turn function is run on every resource in self.current_resources.
        """
        # Check if room for one more
        if len(self.commands) < self.max_commands:

            # Append command
            self.commands.append(command.copy())

            # Apply changes to resource pool (current_resources)
            for resource_name, resource in self.commands[-1].input_resources.items():
                self.current_resources[resource_name].value += resource.value
                if not self.current_resources[resource_name].is_valid_value():
                    return False
            for resource_name, resource in self.commands[-1].output_resources.items():
                self.current_resources[resource_name].value += resource.value
                if not self.current_resources[resource_name].is_valid_value():
                    return False

            # If turn is complete
            if len(self.commands) == self.max_commands:
                return self.apply_end_of_turn_effects()

            return True

        # If not room for one more
        else:
            raise AttributeError(
                "Error when attempting to add command to Turn object beyond its specified max command amount!")

    def apply_end_of_turn_effects(self) -> bool:
        """
        Calls the next_turn on every resource in current_resources.
        # TODO: Prevent this from being run after the last turn is complete (if this indeed matches the game)
        """
        for resource_name, resource in self.current_resources.items():
            if not resource.next_turn():
                return False
        return True

    def is_valid(self) -> bool:
        """
        Checks the validity of every resource value in current_resources.
        """
        for resource in self.current_resources.values():
            if not resource.is_valid_value():
                return False
        return True


class Route:
    """
    Contains a set of turns up to a maximum specified amount.
    Also contains a reference to the last turn's current_resources. Since every turn appended to a Route is supposed to
    already be complete, the last turn's current_resources is assumed to be the resulting resources from all the turns
    contained in this route.
    A route is considered valid if all turns within the Route is considered valid.
    It's considered finished if it contains an amount of turns equal to the max_turns specified in init, although this
    has to be checked from outside this class.

    If a Route is found to be finished, elsewhere in the script, we may call this class' satisfies_objectives function
    to see if this Route indeed is to be considered a candidate for the player's choices.

    Yet to be implemented, this class will also contain the get_possible_turns function, which will serve to provide
    a list of turns possible based on the route's current_resources
    (which is the current - or rather soon to be previous, turn's current_resources).
    """

    max_turns: int
    current_resources: dict[str, type(Resource)] = {}
    turns: list[Turn] = []

    def __init__(self, starting_resources: dict[str, type(Resource)], max_turns: int, turns=None):

        if turns is None:
            turns = []

        self.max_turns: int = max_turns

        for starting_resource_name, starting_resource in starting_resources.items():
            self.current_resources[starting_resource_name]: type(Resource) = starting_resource.copy()

        if len(turns) < self.max_turns:
            self.turns: list[Turn] = turns.copy()

    def __str__(self) -> str:
        output: str = "[Route]: "
        for turn in self.turns:
            output += "\n" + indent_string(str(turn))
        output += "\n"
        return remove_trailing_newlines(output)

    def __len__(self) -> int:
        return len(self.turns)

    def copy(self) -> type(__name__):
        turns_copy: list[Turn] = [turn.copy() for turn in self.turns]
        resource_copy: dict[str, type(Resource)] = {}
        for resource_name, resource in self.current_resources.items():
            resource_copy[resource_name]: type(Resource) = resource.copy()
        return type(self)(resource_copy, self.max_turns, turns_copy)

    def append(self, turn) -> bool:
        """
        Appends the specified turn to the Route, as long as there's room.
        Updates the Route's current_resources to the specified turn's current_resources.
        """
        if len(self.turns) < self.max_turns:
            self.turns.append(turn.copy())
            self.current_resources: dict[str, type(Resource)] = self.turns[-1].current_resources
            return self.is_valid()
        else:
            raise AttributeError(
                "Error when attempting to add turn to Route object beyond its specified max turn amount!")

    def is_valid(self) -> bool:
        for turn in self.turns:
            if not turn.is_valid():
                return False
        return True

    def is_finished(self, objective: dict[str, type(Resource)]) -> bool:
        return len(self.turns) == self.max_turns and self.satisfies_objective(objective)

    def satisfies_objective(self, objective: dict[str, type(Resource)]) -> bool:
        """
        TODO: Implement bonus objectives (might be done somewhere else, in the main script for example)
        """
        for objective_resource_name, objective_resource_value in objective.items():
            if not self.current_resources[objective_resource_name].value >= objective_resource_value:
                return False
        return True

    def get_possible_turns(self, available_commands: dict[str, Command], commands_per_turn: int) -> list[Turn]:
        """
        Starts off by generating a list of permutations based on available commands.
        Then tests all permutations for validity (through the Turn class' built-in validity checks when appending).
        Adds all valid permutations to the list of possible turns.
        """
        possible_turns: list[Turn] = []

        # Get all the permutations of the commands in this task
        command_permutations: list[tuple[Command]] =\
            list(itertools.product(available_commands.values(), repeat=commands_per_turn))

        # Loop through each permutation
        for command_permutation in command_permutations:

            # Create a hypothetical turn object based on the Route's current_resources
            hypothetical_resource_pool: dict[str, type(Resource)] = self.current_resources.copy()
            hypothetical_turn: Turn = Turn(hypothetical_resource_pool, commands_per_turn)

            # Loop through each command in the current permutation
            for command in command_permutation:

                # If appending the command to the hypothetical turn, this permutation is invalid, so we discard it.
                if not hypothetical_turn.append(command):
                    break

                # If it succeeds, we can move on to try appending the next command in the permutation,
                # except if the hypothetical turn has reached its required amount of commands, in which case the entire
                # permutation is valid, so we'll add it to the possible_turns list.
                else:
                    if len(hypothetical_turn) == commands_per_turn:
                        possible_turns.append(hypothetical_turn.copy())

        return possible_turns


class Heat(Resource):
    """
    This subclass of Resource, contains variables and methods specific to this particular in-game resource.
    """

    overheat_limit: int
    min_random_increase: int
    max_random_increase: int

    def __init__(self, overheat_limit: int, min_increase: int, max_increase: int, value: int = 0):
        super().__init__(SPECIAL_RESOURCE_NAMES["heat"], max_value=overheat_limit, value=value)
        self.overheat_limit: int = overheat_limit
        self.min_random_increase: int = min_increase
        self.max_random_increase: int = max_increase

    def next_turn(self) -> bool:
        """
        Heat is a resource that gains a random amount after each turn.
        TODO: Does Heat gain this random amount when the very last turn is submitted?
        """
        if self.is_valid_value:
            self.value += random.randint(self.min_random_increase, self.max_random_increase)
            if self.value < self.overheat_limit:
                return True
            else:
                return False
        else:
            return False

    def is_valid_end_of_route(self) -> bool:
        """
        The task fails if it has too much heat.
        """
        return self.is_valid_value and self.value < self.overheat_limit

    def copy(self) -> type(__name__):
        return Heat(self.overheat_limit, self.min_random_increase, self.max_random_increase, value=self.value)


class Drift(Resource):
    """
    This subclass of Resource, contains variables and methods specific to this particular in-game resource.
    """
    drift_bounds: list[int]

    def __init__(self, drift_bounds: list[int], min_drift: int, max_drift: int, value: int = 0):
        super().__init__(SPECIAL_RESOURCE_NAMES["drift"], min_value=min_drift, max_value=max_drift, value=value)
        self.drift_bounds = drift_bounds

    def next_turn(self) -> bool:
        return self.is_valid_value()

    def is_valid_end_of_route(self) -> bool:
        """
        The task fails if there is too little or too much drift at the end of the last turn.
        # TODO: Does the game care at all about drift before the very end?
        """
        return self.drift_bounds[0] <= self.value <= self.drift_bounds[1]

    def copy(self) -> type(__name__):
        return Drift(self.drift_bounds.copy(), self.min_value, self.max_value, value=self.value)


class Thrust(Resource):
    """
    This subclass of Resource, contains variables and methods specific to this particular in-game resource.
    """
    required_thrust: int

    def __init__(self, max_thrust: int, required_thrust: int, value: int = 0):
        super().__init__(SPECIAL_RESOURCE_NAMES["thrust"], max_value=max_thrust, value=value)
        self.required_thrust = required_thrust

    def next_turn(self) -> bool:
        """
        Some thrust is lost at the end of each turn (but not after the very last one)
        It can't go below 0
        # TODO: Implement the above description, if it indeed matches with the game.
        """
        return self.is_valid_value()

    def is_valid_end_of_route(self) -> bool:
        """
        The task fails if there isn't enough thrust at the end. In this sense, it acts just like a regular resource.
        With the exception that some thrust is automatically lost each turn.
        """
        return self.is_valid_value() and self.value >= self.required_thrust

    def copy(self) -> type(__name__):
        return Thrust(self.max_value, self.required_thrust, value=self.value)


class Comms(Resource):
    """
    This subclass of Resource, contains variables and methods specific to this particular in-game resource.
    This is what's considered a regular resource.
    """
    def __init__(self, value: int = 0):
        super().__init__(REGULAR_RESOURCE_NAMES["comms"], value=value)

    def next_turn(self) -> bool:
        return self.is_valid_value()

    def is_valid_end_of_route(self) -> bool:
        return self.is_valid_value()

    def copy(self) -> type(__name__):
        return Comms(value=self.value)


class Navs(Resource):
    """
    This subclass of Resource, contains variables and methods specific to this particular in-game resource.
    This is what's considered a regular resource.
    """
    def __init__(self, value: int = 0):
        super().__init__(REGULAR_RESOURCE_NAMES["navs"], value=value)

    def next_turn(self) -> bool:
        return self.is_valid_value()

    def is_valid_end_of_route(self) -> bool:
        return self.is_valid_value()

    def copy(self) -> type(__name__):
        return Navs(value=self.value)


class Data(Resource):
    """
    This subclass of Resource, contains variables and methods specific to this particular in-game resource.
    This is what's considered a regular resource.
    """
    def __init__(self, value: int = 0):
        super().__init__(REGULAR_RESOURCE_NAMES["data"], value=value)

    def next_turn(self) -> bool:
        return self.is_valid_value()

    def is_valid_end_of_route(self) -> bool:
        return self.is_valid_value()

    def copy(self) -> type(__name__):
        return Data(value=self.value)


class Power(Resource):
    """
    This subclass of Resource, contains variables and methods specific to this particular in-game resource.
    This is what's considered a regular resource.
    """
    def __init__(self, value: int = 0):
        super().__init__(REGULAR_RESOURCE_NAMES["power"], value=value)

    def next_turn(self) -> bool:
        return self.is_valid_value()

    def is_valid_end_of_route(self) -> bool:
        return self.is_valid_value()

    def copy(self) -> type(__name__):
        return Power(value=self.value)


def indent_string(string: str) -> str:
    """
    Indents every line within a string, including the first one.
    """
    new_string: str = "\t" + string.replace("\n", "\n\t")
    return new_string


def remove_trailing_newlines(string: str) -> str:
    """
    Removes trailing newlines, except the very last one.
    """
    for i in range(len(string) - 1, -1, -1):
        if not string[i] == "\n":
            return string[:i+2]
    return string
