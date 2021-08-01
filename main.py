# from abaqus import *
# from abaqusConstants import *

SUPPORTED_GCODE_COMMANDS = ['G0', 'G1']

GCODE_COMMANDS_SUPPORTED_PARAMETERS = {
    "G0": ['X', 'Y', 'Z'],
    "G1": ['X', 'Y', 'Z']
}


def simulate_lines_abaqus(list_lines):
    # s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
    #     sheetSize=500.0)
    # g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    # s.setPrimaryObject(option=STANDALONE)

    for line in list_lines:
        starting_point = line["starting_point"]
        end_point = line["end_point"]
        # s.Line(point1=(float(starting_point["X"]), float(starting_point["Y"])),
        #        point2=(float(end_point["X"]), float(end_point["Y"])))

    # zoom on simulated part
    # session.viewports['Viewport: 1'].view.fitView()


def get_instructions_list_from_gcode(gcode_file_path):
    with open(gcode_file_path) as gcode_file:
        out_instruction_list = gcode_file.readlines()

    return out_instruction_list


def preprocess_gcode_instructions(gcode_instructions_list):
    out_preprocessed_gcode_instructions = gcode_instructions_list

    # delete comments
    out_preprocessed_gcode_instructions = [gcode_instruction.split(";")[0] for gcode_instruction in
                                           out_preprocessed_gcode_instructions]

    # delete lines without instructions
    out_preprocessed_gcode_instructions = [gcode_instruction for gcode_instruction in
                                           out_preprocessed_gcode_instructions
                                           if gcode_instruction != '']

    # delete "\n"
    out_preprocessed_gcode_instructions = [gcode_instruction.strip() for gcode_instruction
                                           in out_preprocessed_gcode_instructions]

    # ignore non-supported g-code commands
    out_preprocessed_gcode_instructions = [gcode_instruction for gcode_instruction in
                                           out_preprocessed_gcode_instructions
                                           if any(supported_gcode_command in gcode_instruction for
                                                  supported_gcode_command in SUPPORTED_GCODE_COMMANDS)]

    # delete non-supported parameters
    aux_gcode_instructions = []
    for gcode_instruction in out_preprocessed_gcode_instructions:
        list_gcode_instruction = gcode_instruction.split(" ")
        command = list_gcode_instruction[0]
        # get only supported parameters
        list_cleaned_parameters = [parameter for parameter in list_gcode_instruction if parameter != command and
                                   any(supported_parameter in parameter for
                                       supported_parameter in GCODE_COMMANDS_SUPPORTED_PARAMETERS[command])]
        cleaned_gcode_instruction = [command]
        for parameter in list_cleaned_parameters:
            cleaned_gcode_instruction.append(parameter)

        aux_gcode_instructions.append(cleaned_gcode_instruction)

    out_preprocessed_gcode_instructions = aux_gcode_instructions

    # delete instructions without parameters
    out_preprocessed_gcode_instructions = [gcode_instruction for gcode_instruction in
                                           out_preprocessed_gcode_instructions if len(gcode_instruction) > 1]

    return out_preprocessed_gcode_instructions


def get_numerical_difference_dictionaries(dict_1, dict_2):
    out_dict_difference = {}
    # Dictionaries should have same keys
    for key in dict_2.keys():
        out_dict_difference[key] = dict_2[key] - dict_1[key]

    return out_dict_difference


def simulate_gcode_instructions(list_gcode_instructions):
    machine_position = {"X": None, "Y": None, "Z": None}
    is_there_first_starting_point = False
    lines_to_simulate = []
    for gcode_instruction in list_gcode_instructions:
        command = gcode_instruction[0]
        parameters_concat_values = [code for code in gcode_instruction if command != code]

        # create dictionary with available params and respective values
        dict_instruction_parameters = {}
        for parameter_concat_value in parameters_concat_values:
            parameter = parameter_concat_value[0]
            value = parameter_concat_value.replace(parameter, '')
            dict_instruction_parameters[parameter] = float(value)

        if command == "G0":  # only change machine position
            # update machine position
            machine_position.update(dict_instruction_parameters)

        elif command == "G1":  # write line
            # we need to have a valid starting point
            if None in machine_position.values():
                machine_position.update(dict_instruction_parameters)

            elif not is_there_first_starting_point:
                machine_position.update(dict_instruction_parameters)
                is_there_first_starting_point = True

            else:  # we already have a valid starting point for the line
                # add line to simulate
                line_end_point = machine_position.copy()
                line_end_point.update(dict_instruction_parameters)

                lines_to_simulate.append({"starting_point": machine_position.copy(),
                                          "end_point": line_end_point.copy()})

                # print({"starting_point": machine_position.copy(),
                #        "end_point": line_end_point.copy()})

                # update machine position
                machine_position.update(dict_instruction_parameters.copy())

    # simulate g0 and g1 instructions
    simulate_lines_abaqus(lines_to_simulate)


def simulate_gcode_file(gcode_filename="file_example.gcode"):
    # get list of instructions from g-code
    print("Loading G-Code file...")
    gcode_instructions_list = get_instructions_list_from_gcode(gcode_filename)

    # pre-process gcode instructions list
    print("Pre-processing G-Code instructions...")
    gcode_instructions_list = preprocess_gcode_instructions(gcode_instructions_list)

    # simulate every G-code instruction
    print("Simulating G-Code instructions...")
    simulate_gcode_instructions(gcode_instructions_list)

    print("G-Code simulation finished.")


if __name__ == "__main__":
    simulate_gcode_file()
