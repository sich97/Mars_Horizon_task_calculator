import itertools
from data_structure import Command, Turn, Route


def calculator(available_commands: list[Command], current_resources: dict[str, int],
               amount_of_turns: int, amount_of_commands_per_turn: int, objective: dict[str, int]) -> Route:
    """
    :param available_commands:
    :param current_resources:
    :param amount_of_turns:
    :param amount_of_commands_per_turn:
    :param objective:
    :return:
    """
    valid_turns: list[Turn] = get_valid_turn(available_commands, current_resources, amount_of_commands_per_turn)
    test_route = Route([valid_turns[0]], amount_of_turns)


def get_valid_turn(available_commands: list[Command], current_resources: dict[str, int],
                   amount_of_commands: int) -> list[Turn]:
    """
    :param available_commands:
    :param current_resources:
    :param amount_of_commands:
    :return:
    """
    command_permutations: list[tuple[Command]] = list(itertools.product(available_commands, repeat=amount_of_commands))
    valid_turns: list[Turn] = filter_command_permutations(command_permutations, current_resources, amount_of_commands)
    return valid_turns


def filter_command_permutations(command_permutations: list[tuple[Command]],
                                current_resources: dict[str, int], amount_of_commands: int) -> list[Turn]:
    """
    :param command_permutations:
    :param current_resources:
    :param amount_of_commands:
    :return:
    """
    valid_turns: list[Turn] = []

    for command_permutation in command_permutations:

        proposed_turn: Turn = Turn([], amount_of_commands)

        hypothetical_current_resources = current_resources.copy()

        for command in command_permutation:

            # Subtract resource cost from hypothetical resource pool
            for resource_cost_type in command.input_resources.keys():
                hypothetical_current_resources[resource_cost_type] -= command.input_resources[resource_cost_type]

            # If negative resource numbers after subtraction
            if not all(i >= 0 for i in hypothetical_current_resources.values()):
                break

            else:
                # Add resource gain to hypothetical resource pool
                for resource_gain_type in command.output_resources.keys():
                    hypothetical_current_resources[resource_gain_type] += command.output_resources[resource_gain_type]

                # Add the valid command to the proposed permutation
                proposed_turn.append(command)

                # If this was the last command needed for a full turn
                if len(proposed_turn) == amount_of_commands:
                    # Add the permutation to the list of valid permutations, together with the result
                    valid_turns.append(proposed_turn)

    return valid_turns.copy()
