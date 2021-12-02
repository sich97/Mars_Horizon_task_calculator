from task_calculator import calculator
from data_structure import Command, Route, BaseResource, REGULAR_RESOURCE_NAMES, SPECIAL_RESOURCE_NAMES, \
    Comms, Navs, Data, Heat, Drift, Thrust, Power, Crew

DEBUG = True


def main() -> None:
    """
    TODO: Fill this description and comment/typehint this function
    TODO: Need to find alternatives to the current datastructure where resource and resource cost is intermingled and generally very chaotic
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
                                              ),
            "Heat to power": Command("Heat to power",
                                     {
                                         SPECIAL_RESOURCE_NAMES["heat"]: Heat(4, 1, 3, value=2)
                                     },
                                     {
                                         REGULAR_RESOURCE_NAMES["power"]: Data(value=2)
                                     }
                                     ),
            "Crew and data to navs": Command("Crew and data to navs",
                                             {
                                                 SPECIAL_RESOURCE_NAMES["crew"]: Navs(value=2),
                                                 REGULAR_RESOURCE_NAMES["data"]: Data(value=2)
                                             },
                                             {
                                                 REGULAR_RESOURCE_NAMES["navs"]: Navs(value=8)
                                             }
                                             ),
            "Drift to data": Command("Drift to data",
                                     {
                                         SPECIAL_RESOURCE_NAMES["drift"]: Drift([-2, 2], -4, 4, value=-1)
                                     },
                                     {
                                         REGULAR_RESOURCE_NAMES["data"]: Data(value=3)
                                     }
                                     ),
            "Power to thrust and drift": Command("Power to thrust and drift",
                                                 {
                                                     REGULAR_RESOURCE_NAMES["power"]: Power(value=2)
                                                 },
                                                 {
                                                     SPECIAL_RESOURCE_NAMES["thrust"]: Thrust(20, 4, value=1),
                                                     SPECIAL_RESOURCE_NAMES["drift"]: Drift([-2, 2], -4, 4, value=1)
                                                 }
                                                 )
        }

    if not DEBUG:
        current_resources: dict[str, type(BaseResource)] = get_resources(" you start with: ")

    else:
        # TODO: Add special resources to debug in order to test them as well
        current_resources: dict[str, type(BaseResource)] = {
            REGULAR_RESOURCE_NAMES["comms"]: Comms(value=1),
            REGULAR_RESOURCE_NAMES["navs"]: Navs(),
            REGULAR_RESOURCE_NAMES["data"]: Data(),
            REGULAR_RESOURCE_NAMES["power"]: Power(value=10),

            SPECIAL_RESOURCE_NAMES["heat"]: Heat(4, 1, 3, 2),
            SPECIAL_RESOURCE_NAMES["crew"]: Crew(2),
            SPECIAL_RESOURCE_NAMES["drift"]: Drift([-2, 2], -4, 4, value=2),
            SPECIAL_RESOURCE_NAMES["thrust"]: Thrust(20, 4, value=3)
        }

    if not DEBUG:
        amount_of_turns: int = int(input("Enter how many turns for this task: "))
        amount_of_commands_per_turn: int = int(input("Enter how many commands per turn: "))
    else:
        amount_of_turns: int = 3
        amount_of_commands_per_turn: int = 3

    if not DEBUG:
        objective: dict[str, type(BaseResource)] = get_resources(" required by the objective: ")
    else:
        objective: dict[str, type(BaseResource)] = {
            REGULAR_RESOURCE_NAMES["comms"]: Comms(value=10),
            REGULAR_RESOURCE_NAMES["navs"]: Navs(value=10)
        }

    available_commands["Empty command"] = Command("Empty command", {}, {})
    possible_routes: list[Route] = calculator(available_commands, current_resources, amount_of_turns,
                                              amount_of_commands_per_turn, objective)

    print(len(possible_routes))
    for route in possible_routes:
        for resource_name, resource in route.current_resources.items():
            if resource.value < resource.min_value or resource.value > resource.max_value:
                raise ValueError("Found invalid value")


def get_resources(suffix: str = ": ") -> dict[str, type(BaseResource)]:
    """
    TODO: Fill this description and comment/typehint this function
    """
    comms_amount: int = int(input("Input the amount of comms" + suffix))
    navs_amount: int = int(input("Input the amount of navs" + suffix))
    data_amount: int = int(input("Input the amount of data" + suffix))
    power_amount: int = int(input("Input the amount of power" + suffix))

    starting_resources: dict[str, type(BaseResource)] = {
        REGULAR_RESOURCE_NAMES["comms"]: Comms(value=comms_amount),
        REGULAR_RESOURCE_NAMES["navs"]: Navs(value=navs_amount),
        REGULAR_RESOURCE_NAMES["data"]: Data(value=data_amount),
        REGULAR_RESOURCE_NAMES["power"]: Power(value=power_amount)
    }

    starting_resources += get_special_resources(suffix=suffix)

    return starting_resources


def get_special_resources(suffix: str = ": ") -> dict[str, type(BaseResource)]:
    """
    TODO: Fill this description and comment/typehint this function
    TODO: Make sure the list of special resources, as well as the regular ones, always has a key for each resource (I think this is necessary)
    """
    special_resources: dict[str, type(BaseResource)] = {}

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
                special_resources[SPECIAL_RESOURCE_NAMES["heat"]]: type(BaseResource) = \
                    Heat(overheat, min_heat_gain, max_heat_gain, value=amount)

            elif chosen_special_resource_name == SPECIAL_RESOURCE_NAMES["drift"]:
                min_drift = int(input("Input min possible drift: "))
                max_drift = int(input("Input max possible drift: "))
                drift_bounds = []
                drift_bounds[0] = int(input("Input min drift bound: "))
                drift_bounds[1] = int(input("Input max drift bound: "))
                special_resources[SPECIAL_RESOURCE_NAMES["drift"]]: type(BaseResource) = \
                    Drift(drift_bounds, min_drift, max_drift, value=amount)

            elif chosen_special_resource_name == SPECIAL_RESOURCE_NAMES["thrust"]:
                max_thrust = int(input("Input max possible thrust: "))
                required_thrust = int(input("Input required thrust: "))
                special_resources[SPECIAL_RESOURCE_NAMES["thrust"]]: type(BaseResource) = \
                    Thrust(max_thrust, required_thrust, value=amount)

            elif chosen_special_resource_name == SPECIAL_RESOURCE_NAMES["crew"]:
                max_crew = int(input("Input the amount of crew: "))
                special_resources[SPECIAL_RESOURCE_NAMES["crew"]]: type(BaseResource) = Crew(max_crew)

            continue_adding: str = input("Input another special resource? [Y/n]: ")
            if continue_adding.lower() == "n":
                break

    return special_resources


def get_new_command(available_commands: dict[str, Command]) -> None:
    """
    TODO: Fill this description and comment/typehint this function
    """
    command_name: str = input("Please input the command name: ")

    command_resources_in: dict[str, type(BaseResource)] = get_resources(" the command consumes: ")

    command_resources_out: dict[str, type(BaseResource)] = get_resources(" the command produces: ")

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
