import itertools
import random

# TODO: Need to find alternatives to the current datastructure where resource and resource cost is intermingled (because they are made of the same resource/BaseResource and generally very chaotic
REGULAR_RESOURCE_NAMES = {
    "comms": "Comms",
    "navs": "Navs",
    "data": "Data",
    "power": "Power"
}

SPECIAL_RESOURCE_NAMES = {
    "heat": "Heat",
    "drift": "Drift",
    "thrust": "Thrust",
    "crew": "Crew"
}


class BaseResource:
    """
    The base class for all resource types, such as Comms, Navs, Data, Heat, Drift, Thrust
    """

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

    def __init__(self, name: str,
                 input_resources: dict[str, type(BaseResource)], output_resources: dict[str, type(BaseResource)]):

        self.name: str = name

        self.input_resources: dict[str, type(BaseResource)] = {}
        for input_resource_name, input_resource in input_resources.items():
            self.input_resources[input_resource_name]: type(BaseResource) = input_resource.copy()

        self.output_resources: dict[str, type(BaseResource)] = {}
        for output_resource_name, output_resource in output_resources.items():
            self.output_resources[output_resource_name]: type(BaseResource) = output_resource.copy()

    def __repr__(self) -> str:
        output = f"Command({self.name}, {self.input_resources}, {self.output_resources})"
        return output

    def copy(self) -> type(__name__):
        input_resources_copy: dict[str, type(BaseResource)] = {}
        for input_resource_name, input_resource in self.input_resources.items():
            input_resources_copy[input_resource_name]: type(BaseResource) = input_resource

        output_resources_copy: dict[str, type(BaseResource)] = {}
        for output_resource_name, output_resource in self.output_resources.items():
            output_resources_copy[output_resource_name]: type(BaseResource) = output_resource
        return Command(self.name, input_resources_copy, output_resources_copy)


class Turn:
    """
    Contains a set of commands up to a maximum specified amount.
    Also contains a dictionary of the current resources, which is the result of executing all the commands in sequence,
    starting with a set of starting recourses specified in the init. This current resources dictionary gets updated each
    time a new command is appended to this object.
    Whenever the last possible command is appended (determined by the maximum specified in init),
    the next_turn function gets called on every item in current_resources, which is populated by subclasses of Resource.
    """

    def __init__(self, starting_resources: dict[str, type(BaseResource)],
                 max_commands: int, commands: list[Command] = None):

        self.max_commands: int = max_commands

        if commands is None:
            self.commands: list[Command] = []
        else:
            if len(commands) <= self.max_commands:
                self.commands: list[Command] = [command.copy() for command in commands]

        self.current_resources: dict[str, type(BaseResource)] = {}
        for starting_resource_name, starting_resource in starting_resources.items():
            self.current_resources[starting_resource_name]: BaseResource = starting_resource.copy()

    def __repr__(self) -> str:
        output = f"Turn({self.current_resources}, {self.max_commands}, commands={self.commands})"
        return output

    def __len__(self) -> int:
        return len(self.commands)

    def copy(self) -> type(__name__):
        commands_copy: list[Command] = [command.copy() for command in self.commands]
        resource_copy: dict[str, type(BaseResource)] = {}
        for resource_name, resource in self.current_resources.items():
            resource_copy[resource_name]: type(BaseResource) = resource.copy()

        return Turn(resource_copy, self.max_commands, commands=commands_copy)

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
                self.current_resources[resource_name].value -= resource.value
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

    def __init__(self, starting_resources: dict[str, type(BaseResource)], max_turns: int, turns=None):

        self.max_turns: int = max_turns

        if turns is None:
            self.turns = []
        else:
            if len(turns) < self.max_turns:
                self.turns: list[Turn] = turns.copy()

        self.current_resources: dict[str, type(BaseResource)] = {}
        for starting_resource_name, starting_resource in starting_resources.items():
            self.current_resources[starting_resource_name]: type(BaseResource) = starting_resource.copy()

    def __repr__(self) -> str:
        output = f"Route({self.current_resources}, {self.max_turns}, turns={self.turns})"
        return output

    def __len__(self) -> int:
        return len(self.turns)

    def copy(self) -> type(__name__):
        turns_copy: list[Turn] = [turn.copy() for turn in self.turns]
        resource_copy: dict[str, type(BaseResource)] = {}
        for resource_name, resource in self.current_resources.items():
            resource_copy[resource_name]: type(BaseResource) = resource.copy()
        return Route(resource_copy, self.max_turns, turns=turns_copy)

    def append(self, turn) -> bool:
        """
        Appends the specified turn to the Route, as long as there's room.
        Updates the Route's current_resources to the specified turn's current_resources.
        """
        if len(self.turns) < self.max_turns:
            self.turns.append(turn.copy())
            self.current_resources: dict[str, type(BaseResource)] = self.turns[-1].current_resources
            return self.is_valid()
        else:
            raise AttributeError(
                "Error when attempting to add turn to Route object beyond its specified max turn amount!")

    def is_valid(self) -> bool:
        for turn in self.turns:
            if not turn.is_valid():
                return False
        return True

    def is_finished(self, objective: dict[str, type(BaseResource)]) -> bool:
        return len(self.turns) == self.max_turns and self.satisfies_objective(objective)

    def satisfies_objective(self, objective: dict[str, type(BaseResource)]) -> bool:
        """
        TODO: Implement bonus objectives (might be done somewhere else, in the main script for example)
        """
        for objective_resource_name, objective_resource in objective.items():
            if not self.current_resources[objective_resource_name].value >= objective_resource.value:
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
            list(itertools.product(list(available_commands.values()).copy(), repeat=commands_per_turn))

        # Loop through each permutation
        for command_permutation in command_permutations:

            # Create a hypothetical turn object based on the Route's current_resources
            hypothetical_resource_pool: dict[str, type(BaseResource)] = self.current_resources.copy()
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


class Heat(BaseResource):
    """
    This subclass of Resource, contains variables and methods specific to this particular in-game resource.
    """

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

    def __repr__(self) -> str:
        output = f"Heat({self.overheat_limit}, {self.min_random_increase}, {self.max_random_increase}, value={self.value})"
        return output


class Drift(BaseResource):
    """
    This subclass of Resource, contains variables and methods specific to this particular in-game resource.
    """

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

    def __repr__(self) -> str:
        output = f"Drift({self.drift_bounds}, {self.min_value}, {self.max_value}, value={self.value})"
        return output


class Thrust(BaseResource):
    """
    This subclass of Resource, contains variables and methods specific to this particular in-game resource.
    TODO: Sjekk at ikke thrust har noen max value
    """

    def __init__(self, required_thrust: int, value: int = 0):
        super().__init__(SPECIAL_RESOURCE_NAMES["thrust"], value=value)
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
        return Thrust(self.required_thrust, value=self.value)

    def __repr__(self) -> str:
        output = f"Thrust({self.max_value}, {self.required_thrust}, value={self.value})"
        return output


class Crew(BaseResource):
    """
    This subclass of Resource, contains variables and methods specific to this particular in-game resource.
    """

    def __init__(self, value: int = 0):
        super(Crew, self).__init__(SPECIAL_RESOURCE_NAMES["crew"], max_value=value, value=value)

    def next_turn(self) -> bool:
        """
        Crew resources are regained on next turn, up to the specified max value.
        """
        self.value = self.max_value
        return self.is_valid_value()

    def is_valid_end_of_route(self) -> bool:
        """
        This task does not have any special end-of-route criteria, as long as its still a valid value.
        """
        return self.is_valid_value()

    def copy(self) -> type(__name__):
        return Crew(self.max_value)

    def __repr__(self) -> str:
        output = f"Crew({self.max_value})"
        return output


class Comms(BaseResource):
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

    def __repr__(self) -> str:
        output = f"Comms(value={self.value})"
        return output


class Navs(BaseResource):
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

    def __repr__(self) -> str:
        output = f"Navs(value={self.value})"
        return output


class Data(BaseResource):
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

    def __repr__(self) -> str:
        output = f"Data(value={self.value})"
        return output


class Power(BaseResource):
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

    def __repr__(self) -> str:
        output = f"Power(value={self.value})"
        return output


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
