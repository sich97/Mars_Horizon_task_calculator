class Command:
    name: str
    input_resources: dict[str, int]
    output_resources: dict[str, int]

    def __init__(self, name: str, input_resources: dict[str, int], output_resources: dict[str, int]):
        self.name = name
        self.input_resources = input_resources.copy()
        self.output_resources = output_resources.copy()

    def __str__(self):
        output = self.name + " [Command]" + "\n\t"\
                 + "Input resources: " + str(self.input_resources) + "\n\t"\
                 + "Output resources: " + str(self.output_resources) + "\n"
        return remove_trailing_newlines(output)

    def copy(self):
        return type(self)(self.name, self.input_resources.copy(), self.output_resources.copy())


class Turn:
    commands: list[Command]
    max_command_amount: int

    def __init__(self, commands: list[Command], max_command_amount: int = None):
        if max_command_amount:
            self.max_command_amount = max_command_amount

        if self.max_command_amount:
            if len(commands) > self.max_command_amount:
                raise AttributeError(
                    "Error when attempting to add command to Turn object beyond its specified max command amount!")
        self.commands = commands.copy()

    def __str__(self):
        output = "[Turn]: "
        for command in self.commands:
            output += "\n" + indent_string(str(command))
        output += "\n"
        return remove_trailing_newlines(output)

    def __len__(self):
        return len(self.commands)

    def append(self, command: Command):
        if self.max_command_amount:
            if len(self.commands) + 1 > self.max_command_amount:
                raise AttributeError(
                    "Error when attempting to add command to Turn object beyond its specified max command amount!")
        self.commands.append(command.copy())
        return True

    def copy(self):
        return type(self)(self.commands.copy(), self.max_command_amount)


class Route:
    turns = []
    max_turn_amount = None

    def __init__(self, turns: list[Turn], max_turn_amount: int = None):
        if max_turn_amount:
            self.max_turn_amount = max_turn_amount

        if self.max_turn_amount:
            if len(turns) > self.max_turn_amount:
                raise AttributeError(
                    "Error when attempting to add turn to Route object beyond its specified max turn amount!")
        self.turns = turns.copy()

    def __str__(self):
        output = "[Route]: "
        for turn in self.turns:
            output += "\n" + indent_string(str(turn))
        output += "\n"
        return remove_trailing_newlines(output)

    def __len__(self):
        return len(self.turns)

    def append(self, turn: Turn):
        if self.max_turn_amount:
            if not len(self.turns) + 1 > self.max_turn_amount:
                raise AttributeError(
                    "Error when attempting to add turn to Route object beyond its specified max turn amount!")
        self.turns.append(turn.copy())
        return True

    def copy(self):
        return type(self)(self.turns.copy(), self.max_turn_amount)


def indent_string(string: str) -> str:
    new_string = "\t" + string.replace("\n", "\n\t")
    return new_string


def remove_trailing_newlines(string: str) -> str:
    for i in range(len(string) - 1, -1, -1):
        if not string[i] == "\n":
            return string[:i+2]
    return string
