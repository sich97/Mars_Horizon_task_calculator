from data_structure import Command, Turn, Route, BaseResource
from PyQt5.Qt import QMainWindow, QApplication


def calculator(available_commands: dict[str, Command], starting_resources: dict[str, type(BaseResource)],
               amount_of_turns: int, commands_per_turn: int, objective: dict[str, type(BaseResource)],
               gui: type(QMainWindow)) -> None:
    """
    TODO: Fill this description and comment/typehint this function
    TODO: Find a way to rank the different routes based on how close they are to failing if a command fails
    """
    starting_routes: list[Route] = []

    # Fill the starting routes list with possible routes from the get-go
    empty_route: Route = Route(starting_resources, amount_of_turns)
    possible_turns_from_empty_route: list[Turn] = empty_route.get_possible_turns(available_commands, commands_per_turn)
    for possible_turn in possible_turns_from_empty_route:
        QApplication.processEvents()
        starting_routes.append(Route(starting_resources, amount_of_turns))
        valid = starting_routes[-1].append(possible_turn)
        if not valid:
            starting_routes.pop()

    valid_routes: list[Route] = starting_routes
    for turn in range(2, amount_of_turns + 1, 1):
        QApplication.processEvents()
        valid_routes = get_next_turn_routes(valid_routes, available_commands, commands_per_turn, gui)

    valid_routes: list[Route] = filter_by_objective(valid_routes, objective, gui)

    gui.present_results(valid_routes)


def filter_by_objective(valid_routes: list[Route], objective: dict[str, type(BaseResource)], gui: type(QMainWindow)) -> list[Route]:
    """
    # TODO: Fill this description and comment/typehint this function
    """
    output: list[Route] = []

    for route in valid_routes:
        QApplication.processEvents()
        if not gui.continue_calculating:
            break
        if route.satisfies_objective(objective):
            output.append(route)

    return output


def get_next_turn_routes(previous_turn_routes: list[Route], available_commands: dict[str, Command],
                         commands_per_turn: int, gui: type(QMainWindow)) -> list[Route]:
    """
    TODO: Fill this description and comment/typehint this function
    """

    valid_routes: list[Route] = []
    for route in previous_turn_routes:
        if not gui.continue_calculating:
            break
        possible_turns: list[Turn] = route.get_possible_turns(available_commands, commands_per_turn)
        for possible_turn in possible_turns:
            QApplication.processEvents()
            if not gui.continue_calculating:
                break
            route_copy: Route = route.copy()
            if route_copy.append(possible_turn):
                valid_routes.append(route_copy)

    return valid_routes
