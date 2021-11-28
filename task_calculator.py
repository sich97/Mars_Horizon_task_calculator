from data_structure import Command, Turn, Route, Resource


def calculator(available_commands: dict[str, Command], starting_resources: dict[str, type(Resource)],
               amount_of_turns: int, commands_per_turn: int, objective: dict[str, type(Resource)]) -> list[Route]:
    """
    TODO: Fill this description and comment/typehint this function
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

    print(len(starting_routes))
    if False:
        for route in starting_routes:
            print(route)

    valid_routes: list[Route] = starting_routes
    for turn in range(2, amount_of_turns + 1, 1):
        valid_routes = get_next_turn_routes(valid_routes, available_commands, commands_per_turn)

    return valid_routes


def get_next_turn_routes(previous_turn_routes: list[Route], available_commands: dict[str, Command],
                         commands_per_turn: int) -> list[Route]:
    """
    TODO: Fill this description and comment/typehint this function
    """

    valid_routes: list[Route] = []
    for route in previous_turn_routes:
        possible_turns: list[Turn] = route.get_possible_turns(available_commands, commands_per_turn)
        for possible_turn in possible_turns:
            route_copy: Route = route.copy()
            if route_copy.append(possible_turn):
                valid_routes.append(route_copy)

    return valid_routes
