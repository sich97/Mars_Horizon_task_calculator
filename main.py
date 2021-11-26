from task_calculator import calculator
from data_structure import Command, Turn, Route

AVAILABLE_RESOURCE_TYPES = [
    "Communication",
    "Navigation",
    "Data",
    "Power"
]

DEBUG = True


def main():
    if not DEBUG:
        available_commands = []

        while True:
            user_action = input("Input another command? [Y/n]: ")
            if user_action.lower() == "n":
                break
            else:
                available_commands.append(get_new_command())

        current_resources = {}
        update_current_resources(current_resources)

        amount_of_turns = int(input("Enter how many turns for this task: "))
        amount_of_commands_per_turn = int(input("Enter how many commands per turn: "))

        objective = get_objective()

        optimal_route: Route = calculator(available_commands, current_resources, amount_of_turns,
                                          amount_of_commands_per_turn, objective)

    else:
        optimal_route: Route = calculator([
            Command("Comms_and_nav_to_data", {AVAILABLE_RESOURCE_TYPES[0]: 3, AVAILABLE_RESOURCE_TYPES[1]: 2},
                    {AVAILABLE_RESOURCE_TYPES[2]: 8}),
            Command("Data_to_comms_and_nav", {AVAILABLE_RESOURCE_TYPES[2]: 3},
                    {AVAILABLE_RESOURCE_TYPES[0]: 4, AVAILABLE_RESOURCE_TYPES[1]: 3}),
            Command("Power_to_comms", {AVAILABLE_RESOURCE_TYPES[3]: 1},
                    {AVAILABLE_RESOURCE_TYPES[0]: 2}),
            Command("Power_to_data", {AVAILABLE_RESOURCE_TYPES[3]: 2},
                    {AVAILABLE_RESOURCE_TYPES[2]: 4}),
        ],
            {AVAILABLE_RESOURCE_TYPES[0]: 0, AVAILABLE_RESOURCE_TYPES[1]: 0, AVAILABLE_RESOURCE_TYPES[2]: 0,
             AVAILABLE_RESOURCE_TYPES[3]: 8},
            2,
            4,
            {AVAILABLE_RESOURCE_TYPES[0]: 8, AVAILABLE_RESOURCE_TYPES[1]: 8}
        )

    print("The optimal route is: ")
    print(optimal_route)


def get_objective():
    objective = {}
    while True:
        user_action = input("Input another objective resource? [Y/n]: ")
        if user_action.lower() == "n":
            break
        else:
            resource_type = get_resource_type()
            resource_amount = get_resource_amount()
            objective[resource_type] = resource_amount

    return objective


def update_current_resources(current_resources):
    for resource in AVAILABLE_RESOURCE_TYPES:
        current_resources[resource] = int(input("How many of the following resource do you currently have? ["
                                                + resource.upper() + "]: "))


def get_new_command():
    command_name = input("Please input the command name: ")

    command_resources_in = {}
    while True:
        user_action = input("Input another IN resource? [Y/n]: ")
        if user_action.lower() == "n":
            break
        else:
            resource_type = get_resource_type()
            resource_amount = get_resource_amount()
            command_resources_in[resource_type] = resource_amount

    command_resources_out = {}
    while True:
        user_action = input("Input another OUT resource? [Y/n]: ")
        if user_action.lower() == "n":
            break
        else:
            resource_type = get_resource_type()
            resource_amount = get_resource_amount()
            command_resources_out[resource_type] = resource_amount

    return Command(command_name, command_resources_in, command_resources_out)


def get_resource_type():
    list_available_resource_types()
    chosen_resource_type =\
        AVAILABLE_RESOURCE_TYPES[int(input("Type the number associated with the resource type: ")) - 1]
    return chosen_resource_type


def get_resource_amount():
    return int(input("Please enter the amount: "))


def list_available_resource_types():
    output_string = ""
    for i in range(len(AVAILABLE_RESOURCE_TYPES)):
        output_string += str(i+1) + ":\t" + AVAILABLE_RESOURCE_TYPES[i] + "\n"
    print(output_string)


if __name__ == "__main__":
    main()
