from data_structure import Command, Turn, Route, Resource, Heat, Thrust, Drift, Comms, Navs, Data


def calculator(available_commands: dict[str, Command], starting_resources: dict[str, type(Resource)],
               amount_of_turns: int, commands_per_turn: int, objective: dict[str, type(Resource)]) -> list[Route]:
    """
    # TODO: Complete this function
    """
    starting_routes: list[Route] = []

    # Fill the starting routes list with possible routes from the get-go
    empty_route: Route = Route(starting_resources, amount_of_turns)
    possible_turns_from_empty_route: list[Turn] = empty_route.get_possible_turns(available_commands, commands_per_turn)
    for possible_turn in possible_turns_from_empty_route:
        starting_routes.append(Route(starting_resources, amount_of_turns))
        valid = starting_routes[-1].append(possible_turn)
        if not valid:
            starting_routes.pop()

    # TODO: Is this how you wanna do it? I've learned from my mistake and know when to stop coding. This feels like one of those times
