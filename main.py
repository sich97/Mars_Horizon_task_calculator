import time

from PyQt5.QtCore import QRegExp
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, \
    QGroupBox, QFormLayout, QLineEdit, QCheckBox, QPushButton, QSizePolicy
from PyQt5.QtGui import QRegExpValidator
import sys

from task_calculator import calculator
from data_structure import Command, Route, BaseResource, REGULAR_RESOURCE_NAMES, SPECIAL_RESOURCE_NAMES, \
    Comms, Navs, Data, Heat, Drift, Thrust, Power, Crew

DEBUG = True

# TODO: Heat is still calculated for some reason. Have to find a solution to have the certain resources not calculate each round if they're not a part of the task


class MainWindow(QMainWindow):
    # TODO: Implement a way to prevent user input when calculating
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle("Mars Horizon Task Calculator")

        # Center this window on screen
        qt_rectangle = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())

        # Fill the GUI
        main_widget = QWidget()
        self.local_layout = QVBoxLayout()
        main_widget.setLayout(self.local_layout)
        self.setCentralWidget(main_widget)

        self.starting_resources = ResourcesListWidget("Starting resources", self)
        self.local_layout.addWidget(self.starting_resources)

        self.objective_resources = ResourcesListWidget("Objective", self)
        self.local_layout.addWidget(self.objective_resources)

        self.amount_of_turns = SingularIntInput(self, "Amount of turns: ", 3)
        self.local_layout.addWidget(self.amount_of_turns)

        self.commands_per_turn = SingularIntInput(self, "Amount of commands per turn: ", 3)
        self.local_layout.addWidget(self.commands_per_turn)

        self.continue_calculating = False
        self.calculate_button = QPushButton("Calculate", parent=self)
        self.local_layout.addWidget(self.calculate_button)
        self.calculate_button.clicked.connect(self.calculate_button_clicked)

        self.output_field = QLabel(parent=self)
        self.local_layout.addWidget(self.output_field)

        self.available_commands_widget = AvailableCommandsWidget("Available commands", self)
        self.local_layout.addWidget(self.available_commands_widget)
        self.available_commands_widget.add_row()

        self.add_row_button = QPushButton("+", parent=self)
        self.local_layout.addWidget(self.add_row_button)
        self.add_row_button.clicked.connect(self.available_commands_widget.add_row)

    def calculate_button_clicked(self):
        if not self.continue_calculating:
            calculation_arguments: dict[str, any] = self.parse_input()
            self.calculate_button.setText("Stop")
            self.continue_calculating = True
            self.output_field.setText("Calculating...")
            QApplication.processEvents()
            calculator(**calculation_arguments)
        else:
            self.continue_calculating = False
            self.output_field.setText("Stopping...")
            QApplication.processEvents()

    def parse_input(self) -> dict[str, any]:
        if not DEBUG:
            output: dict[str, any] = {"available_commands": get_available_commands(self),
                                      "starting_resources": get_starting_resources(self),
                                      "amount_of_turns": get_amount_of_turns(self),
                                      "commands_per_turn": get_commands_per_turn(self),
                                      "objective": get_objective(self),
                                      "gui": self}
        else:
            output: dict[str, any] = {
                "available_commands": {
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
                                                             SPECIAL_RESOURCE_NAMES["thrust"]: Thrust(4, value=1),
                                                             SPECIAL_RESOURCE_NAMES["drift"]: Drift([-2, 2], -4, 4,
                                                                                                    value=1)
                                                         }
                                                         )
                },
                "starting_resources": {
                    REGULAR_RESOURCE_NAMES["comms"]: Comms(value=1),
                    REGULAR_RESOURCE_NAMES["navs"]: Navs(),
                    REGULAR_RESOURCE_NAMES["data"]: Data(),
                    REGULAR_RESOURCE_NAMES["power"]: Power(value=10),

                    SPECIAL_RESOURCE_NAMES["heat"]: Heat(4, 1, 3, 2),
                    SPECIAL_RESOURCE_NAMES["crew"]: Crew(2),
                    SPECIAL_RESOURCE_NAMES["drift"]: Drift([-2, 2], -4, 4, value=2),
                    SPECIAL_RESOURCE_NAMES["thrust"]: Thrust(4, value=3)
                },
                "amount_of_turns": 2,
                "commands_per_turn": 3,
                "objective": {
                    REGULAR_RESOURCE_NAMES["comms"]: Comms(value=7),
                    REGULAR_RESOURCE_NAMES["navs"]: Navs(value=7)
                },
                "gui": self
            }
        return output

    def present_results(self, valid_routes: list[Route]) -> None:
        self.continue_calculating = False
        self.output_field.setText("Done: " + str(len(valid_routes)))
        self.calculate_button.setText("Calculate")
        QApplication.processEvents()
        print()


class SingularIntInput(QWidget):
    def __init__(self, parent: QWidget, label: str = "", value: int = 0):
        super(SingularIntInput, self).__init__(parent=parent)
        self.local_layout = QHBoxLayout()
        self.setLayout(self.local_layout)

        self.label = QLabel(label)
        self.label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Maximum)
        self.local_layout.addWidget(self.label)

        self.input = QLineEdit()
        self.input.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        self.input.setText(str(value))
        self.input.setValidator(QRegExpValidator(QRegExp("^[0-9]+$")))
        self.local_layout.addWidget(self.input)


class AvailableCommandsWidget(QGroupBox):
    def __init__(self, name: str, parent: QWidget):
        super(AvailableCommandsWidget, self).__init__(name, parent=parent)
        self.local_layout = QFormLayout()
        self.setLayout(self.local_layout)

    def add_row(self) -> None:
        self.local_layout.addRow(CommandLineWidget(self, self.local_layout.rowCount()))

    def delete_row(self, row_num: int) -> None:
        self.local_layout.removeRow(row_num)


class CommandLineWidget(QGroupBox):
    def __init__(self, parent: QWidget, row_num: int, name=""):
        super(CommandLineWidget, self).__init__("", parent=parent)
        self.local_layout = QHBoxLayout()
        self.setLayout(self.local_layout)

        self.row_num = row_num

        self.is_active = QCheckBox()
        self.local_layout.addWidget(self.is_active)

        self.command_name = QLineEdit(self)
        self.command_name.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum))
        self.command_name.setPlaceholderText("Type command name here")
        self.command_name.textChanged.connect(self.command_name_changed)
        self.command_name.setText(name)

        self.local_layout.addWidget(self.command_name)

        self.input_resource_list = ResourcesListWidget("Input resources", self)
        self.local_layout.addWidget(self.input_resource_list)

        self.output_resource_list = ResourcesListWidget("Output resources", self)
        self.local_layout.addWidget(self.output_resource_list)

        self.delete_button = QPushButton("-", parent=self)
        self.local_layout.addWidget(self.delete_button)
        self.delete_button.clicked.connect(lambda: parent.delete_row(self.row_num))

    def command_name_changed(self):
        if not self.command_name.text():
            self.is_active.setChecked(False)
        else:
            self.is_active.setChecked(True)


class ResourcesListWidget(QGroupBox):
    def __init__(self, name: str, parent: QWidget, readonly: bool = False):
        self.readonly = readonly
        resource_names: list[str] = list(REGULAR_RESOURCE_NAMES.values()) + list(SPECIAL_RESOURCE_NAMES.values())
        super(ResourcesListWidget, self).__init__(name, parent=parent)
        self.local_layout = QHBoxLayout()
        self.setLayout(self.local_layout)

        for resource_name in resource_names:
            self.local_layout.addWidget(ResourceWidget(self, resource_name, 0))


class ResourceWidget(QWidget):
    # TODO: Implementer knapper for å øke/minke verdi
    def __init__(self, parent: QWidget, name: str, value: int = 0, readonly: bool = False):
        super(ResourceWidget, self).__init__(parent=parent)
        self.local_layout = QVBoxLayout()
        self.setLayout(self.local_layout)

        self.name = name

        self.label = QLabel(self.name)
        self.local_layout.addWidget(self.label)
        self.value = QLineEdit()
        self.value.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.value.setText(str(value))
        self.value.setValidator(QRegExpValidator(
            QRegExp("^[0-9]+$")))  # TODO: Tillat negative tall for drift (hvis dette stemmer med spillet)
        self.value.setReadOnly(readonly)
        self.local_layout.addWidget(self.value)


def get_resource_from_name(name: str, value: int) -> type(BaseResource):
    if name == REGULAR_RESOURCE_NAMES["comms"]:
        return Comms(value=value)
    elif name == REGULAR_RESOURCE_NAMES["navs"]:
        return Navs(value=value)
    elif name == REGULAR_RESOURCE_NAMES["data"]:
        return Data(value=value)
    elif name == REGULAR_RESOURCE_NAMES["power"]:
        return Power(value=value)

    elif name == SPECIAL_RESOURCE_NAMES["heat"]:
        return Heat(4, 0, 3, value=value)
    elif name == SPECIAL_RESOURCE_NAMES["drift"]:
        return Drift([-2, 2], -4, 4, value=value)
    elif name == SPECIAL_RESOURCE_NAMES["thrust"]:
        return Thrust(4, value=value)
    elif name == SPECIAL_RESOURCE_NAMES["crew"]:
        return Crew(value=value)


def get_amount_of_turns(gui: MainWindow) -> int:
    if not gui.amount_of_turns.input.text():
        value: int = 0
    else:
        value: int = int(gui.amount_of_turns.input.text())
    return value


def get_commands_per_turn(gui: MainWindow) -> int:
    if not gui.commands_per_turn.input.text():
        value: int = 0
    else:
        value: int = int(gui.commands_per_turn.input.text())
    return value


# TODO: Would it be possible to generalize some of these functions to make the code more maintaneable?


def get_objective(gui: MainWindow) -> dict[str, type(BaseResource)]:
    objective: dict[str, type(BaseResource)] = {}
    objective_layout: QHBoxLayout = gui.objective_resources.local_layout
    for resource_index in range(objective_layout.count()):
        resource: ResourceWidget = objective_layout.itemAt(resource_index).widget()
        if not resource.value.text():
            value: int = 0
        else:
            value: int = int(resource.value.text())
        objective[resource.name] = get_resource_from_name(resource.name, value)
    return objective


def get_starting_resources(gui: MainWindow) -> dict[str, type(BaseResource)]:
    starting_resources: dict[str, type(BaseResource)] = {}
    starting_resources_layout: QHBoxLayout = gui.starting_resources.local_layout
    for resource_index in range(starting_resources_layout.count()):
        resource: ResourceWidget = starting_resources_layout.itemAt(resource_index).widget()
        if not resource.value.text():
            value: int = 0
        else:
            value: int = int(resource.value.text())
        starting_resources[resource.name] = get_resource_from_name(resource.name, value)
    return starting_resources


def get_available_commands(gui: MainWindow) -> dict[str, Command]:
    available_commands: dict[str, Command] = {}
    commands_layout: QFormLayout = gui.available_commands_widget.local_layout
    for row_index in range(commands_layout.rowCount()):
        row: CommandLineWidget = commands_layout.itemAt(row_index).widget()
        if row.is_active:
            input_resources: dict[str, type(BaseResource)] = {}
            for input_resource_index in range(row.input_resource_list.local_layout.count()):
                input_resource: ResourceWidget = \
                    row.input_resource_list.local_layout.itemAt(input_resource_index).widget()
                if not input_resource.value.text():
                    input_value: int = 0
                else:
                    input_value: int = int(input_resource.value.text())
                input_resources[input_resource.name]: type(BaseResource) = \
                    get_resource_from_name(input_resource.name, input_value)

            output_resources: dict[str, type(BaseResource)] = {}
            for output_resource_index in range(row.output_resource_list.local_layout.count()):
                output_resource: ResourceWidget = \
                    row.output_resource_list.local_layout.itemAt(output_resource_index).widget()
                if not output_resource.value.text():
                    output_value: int = 0
                else:
                    output_value: int = int(output_resource.value.text())
                output_resources[output_resource.name]: type(BaseResource) = \
                    get_resource_from_name(output_resource.name, output_value)

            command: Command = Command(row.command_name.text(), input_resources, output_resources)
            available_commands[row.command_name.text()]: Command = command
    return available_commands


''' # TODO: Depreceated
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
'''

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
