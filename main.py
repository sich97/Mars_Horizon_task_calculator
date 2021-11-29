from task_calculator import calculator
from data_structure import Command, Route, Resource, REGULAR_RESOURCE_NAMES, SPECIAL_RESOURCE_NAMES, \
    Comms, Navs, Data, Heat, Drift, Thrust, Power

DEBUG = True


def main() -> None:
    """
    TODO: Fill this description and comment/typehint this function
    """
    if not DEBUG:
        available_commands: dict[str, Command] = {}

        while True:
            user_action = input("Input another command? [Y/n]: ")
            if user_action.lower() == "n":
                break
            else:
                get_new_command(available_commands)
    else:
        # TODO: Add special resources to debug in order to test them as well
        available_commands: dict[str, Command] = {
            "Power to comms": Command("Power to comms",
                                      {
                                          REGULAR_RESOURCE_NAMES["power"]: Power(value=1),
                                      },
                                      {
                                          REGULAR_RESOURCE_NAMES["comms"]: Comms(value=2)
                                      }
                                      ),

            "Comms and power to navs": Command("Comms and power to navs",
                                               {
                                                   REGULAR_RESOURCE_NAMES["comms"]: Comms(value=2),
                                                   REGULAR_RESOURCE_NAMES["power"]: Power(value=1)
                                               },
                                               {
                                                   REGULAR_RESOURCE_NAMES["navs"]: Navs(value=5)
                                               }
                                               ),

            "Navs to data and comms": Command("Navs to data and comms",
                                              {
                                                  REGULAR_RESOURCE_NAMES["navs"]: Navs(value=3)
                                              },
                                              {
                                                  REGULAR_RESOURCE_NAMES["data"]: Data(value=2),
                                                  REGULAR_RESOURCE_NAMES["comms"]: Comms(value=2)
                                              }
                                              )
        }

    if not DEBUG:
        current_resources: dict[str, type(Resource)] = get_resources(" you start with: ")

    else:
        # TODO: Add special resources to debug in order to test them as well
        current_resources: dict[str, type(Resource)] = {
            REGULAR_RESOURCE_NAMES["comms"]: Comms(value=1),
            REGULAR_RESOURCE_NAMES["navs"]: Navs(),
            REGULAR_RESOURCE_NAMES["data"]: Data(),
            REGULAR_RESOURCE_NAMES["power"]: Power(value=10)
        }

    if not DEBUG:
        amount_of_turns: int = int(input("Enter how many turns for this task: "))
        amount_of_commands_per_turn: int = int(input("Enter how many commands per turn: "))
    else:
        amount_of_turns: int = 4
        amount_of_commands_per_turn: int = 4

    if not DEBUG:
        objective: dict[str, type(Resource)] = get_resources(" required by the objective: ")
    else:
        objective: dict[str, type(Resource)] = {
            REGULAR_RESOURCE_NAMES["comms"]: Comms(value=10),
            REGULAR_RESOURCE_NAMES["comms"]: Navs(value=10)
        }

    possible_routes: list[Route] = calculator(available_commands, current_resources, amount_of_turns,
                                              amount_of_commands_per_turn, objective)

    print(len(possible_routes))
    print(possible_routes)


def get_resources(suffix: str = ": ") -> dict[str, type(Resource)]:
    """
    TODO: Fill this description and comment/typehint this function
    """
    comms_amount: int = int(input("Input the amount of comms" + suffix))
    navs_amount: int = int(input("Input the amount of navs" + suffix))
    data_amount: int = int(input("Input the amount of data" + suffix))
    power_amount: int = int(input("Input the amount of power" + suffix))

    starting_resources: dict[str, type(Resource)] = {
        REGULAR_RESOURCE_NAMES["comms"]: Comms(value=comms_amount),
        REGULAR_RESOURCE_NAMES["navs"]: Navs(value=navs_amount),
        REGULAR_RESOURCE_NAMES["data"]: Data(value=data_amount),
        REGULAR_RESOURCE_NAMES["power"]: Power(value=power_amount)
    }

    starting_resources += get_special_resources(suffix=suffix)

    return starting_resources


def get_special_resources(suffix: str = ": ") -> dict[str, type(Resource)]:
    """
    TODO: Fill this description and comment/typehint this function
    TODO: Missing crew
    """
    special_resources: dict[str, type(Resource)] = {}

    user_action: str = input("Would you like to add a special resource? [Y/n]: ")
    if not user_action.lower() == "n":
        while True:
            list_available_resource_types(SPECIAL_RESOURCE_NAMES)
            chosen_special_resource_name: str = list(SPECIAL_RESOURCE_NAMES.values())[int(input(
                "Enter the number corresponding with the special resource you'd like to add: "))]
            amount: int = int(input("Input the amount of " + chosen_special_resource_name + suffix))

            if chosen_special_resource_name == SPECIAL_RESOURCE_NAMES["heat"]:
                overheat = int(input("Input overheat limit: "))
                min_heat_gain = int(input("Input min heat gain: "))
                max_heat_gain = int(input("Input max heat gain: "))
                special_resources[SPECIAL_RESOURCE_NAMES["heat"]]: type(Resource) = \
                    Heat(overheat, min_heat_gain, max_heat_gain, value=amount)

            elif chosen_special_resource_name == SPECIAL_RESOURCE_NAMES["drift"]:
                min_drift = int(input("Input min possible drift: "))
                max_drift = int(input("Input max possible drift: "))
                drift_bounds = []
                drift_bounds[0] = int(input("Input min drift bound: "))
                drift_bounds[1] = int(input("Input max drift bound: "))
                special_resources[SPECIAL_RESOURCE_NAMES["drift"]]: type(Resource) = \
                    Drift(drift_bounds, min_drift, max_drift, value=amount)

            elif chosen_special_resource_name == SPECIAL_RESOURCE_NAMES["thrust"]:
                max_thrust = int(input("Input max possible thrust: "))
                required_thrust = int(input("Input required thrust: "))
                special_resources[SPECIAL_RESOURCE_NAMES["thrust"]]: type(Resource) = \
                    Thrust(max_thrust, required_thrust, value=amount)

            continue_adding: str = input("Input another special resource? [Y/n]: ")
            if continue_adding.lower() == "n":
                break

    return special_resources


def get_new_command(available_commands: dict[str, Command]) -> None:
    """
    TODO: Fill this description and comment/typehint this function
    """
    command_name: str = input("Please input the command name: ")

    command_resources_in: dict[str, type(Resource)] = get_resources(" the command consumes: ")

    command_resources_out: dict[str, type(Resource)] = get_resources(" the command produces: ")

    available_commands[command_name]: Command = Command(command_name, command_resources_in, command_resources_out)


def list_available_resource_types(list_of_names: dict[str, str]) -> None:
    """
    TODO: Fill this description and comment/typehint this function
    """
    output_string: str = ""
    for resource_type_index in range(len(list_of_names.items())):
        output_string += str(resource_type_index) + ": " + list(list_of_names.items())[resource_type_index][1] + "\n"
    print(output_string)


if __name__ == "__main__":
    main()
