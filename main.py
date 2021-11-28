from task_calculator import calculator
from data_structure import Command, Route, Resource,\
    COMMS_NAME, NAVS_NAME, DATA_NAME, HEAT_NAME, DRIFT_NAME, THRUST_NAME

AVAILABLE_RESOURCE_TYPES = [
    COMMS_NAME,
    NAVS_NAME,
    DATA_NAME,
    HEAT_NAME,
    DRIFT_NAME,
    THRUST_NAME,
]

DEBUG = False


def main() -> None:
    if not DEBUG:
        available_commands: dict[str, Command] = {}

        while True:
            user_action = input("Input another command? [Y/n]: ")
            if user_action.lower() == "n":
                break
            else:
                get_new_command(available_commands)

        current_resources: dict[str, type(Resource)] = {}

        amount_of_turns: int = int(input("Enter how many turns for this task: "))
        amount_of_commands_per_turn: int = int(input("Enter how many commands per turn: "))

        objective: dict[str, type(Resource)] = get_objective()

        possible_routes: list[Route] = calculator(available_commands, current_resources, amount_of_turns,
                                                  amount_of_commands_per_turn, objective)


def get_objective() -> dict[str, type(Resource)]:
    objective: dict[str, type(Resource)] = {}
    get_resource(objective)

    return objective


def get_resource(list_of_resources: dict[str, type(Resource)]) -> type(Resource):
    while True:
        user_action: str = input("Input another IN resource? [Y/n]: ")
        if user_action.lower() == "n":
            break
        else:
            resource_type: str = get_resource_type()
            resource_amount: int = get_resource_amount()
            list_of_resources[resource_type] = Resource(resource_type, resource_amount)
            return True


def get_new_command(available_commands: dict[str, Command]) -> None:
    command_name: str = input("Please input the command name: ")

    command_resources_in: dict[str, type(Resource)] = {}
    get_resource(command_resources_in)

    command_resources_out: dict[str, type(Resource)] = {}
    get_resource(command_resources_out)

    available_commands[command_name]: Command = Command(command_name, command_resources_in, command_resources_out)


def get_resource_type() -> str:
    list_available_resource_types()
    chosen_resource_type: str =\
        AVAILABLE_RESOURCE_TYPES[int(input("Type the number associated with the resource type: ")) - 1]
    return chosen_resource_type


def get_resource_amount() -> int:
    return int(input("Please enter the amount: "))


def list_available_resource_types() -> None:
    output_string: str = ""
    for i in range(len(AVAILABLE_RESOURCE_TYPES)):
        output_string += str(i+1) + ":\t" + AVAILABLE_RESOURCE_TYPES[i] + "\n"
    print(output_string)


if __name__ == "__main__":
    main()
