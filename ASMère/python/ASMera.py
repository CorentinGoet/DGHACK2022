"""
ASMera

This program is part of the ASMera challenge from DG'Hack2022.
---

@author CorentinGoet

---

This is an interpreter for the custom assembly language of the challenge.
"""

import re
import sys


class Instruction:
    """
    An instruction has a function and a list of parameters.
    """

    def __init__(self, fun, parameters):
        """
        Constructor for the Instruction class.

        :param fun: function to execute.
        :param parameters: parameters of the function.
        """
        self.function = fun
        self.parameters = parameters

    def execute(self):
        """
        Execute the instruction
        """
        self.function(self.parameters)

    def __str__(self):
        return self.function.__name__ + " " + self.parameters


class Interpreter:

    def __init__(self, source_code):
        self.variables = {}
        self.functions = {}
        self.stdout = ""
        self.source_code = source_code
        self.clean_source = []
        self.instructions = []
        self.skip = False   # boolean value to skip instruction during execution or not (used for 'si' instruction)

    def find_functions(self):

        lines = self.source_code.split('\n')
        i = 0
        while i < len(lines):
            regex = re.compile(r'\w+:')
            match = regex.match(lines[i])

            if match:
                function_name = match.group(0)[:-1]

                # check for existing functions
                if function_name in self.functions.keys():
                    raise ValueError(f"Error on line {i}: a function with the name {function_name} has already been defined.")

                instructions = []
                i += 1
                retour_regex = re.compile(r'retour')

                while not retour_regex.match(lines[i]):
                    instructions.append(self.parse_instruction(lines[i]))
                    i += 1

                self.functions[function_name] = instructions
                i += 1  # remove retour instruction

            else:
                self.clean_source.append(lines[i])
                i += 1

    def remove_comments(self):
        for i, line in enumerate(self.clean_source):
            if ';' in line:
                self.clean_source[i] = line.split(';')[0]

    def parse_clean_code(self):
        """
        Parse the clean code to find the instructions.
        """
        for line in self.clean_source:
            self.instructions.append(self.parse_instruction(line))

    def parse_instruction(self, line) -> Instruction:
        """
        Parses a line of source code to find an instruction.
        """

        # do nothing with blank lines and comments
        if line == '' or line[0] == ";":
            return Instruction(self.idle, "")

        instruction_kw = line.split(" ")[0]
        if len(line.split(" ")) > 1:
            parameters = line[len(instruction_kw):].strip(" ")
        else:
            parameters = ""

        instruction_map = {
            "message": self.message,
            "incrementer": self.incrementer,
            "appel": self.appel,
            "nombre": self.nombre,
            "si": self.si,
            "finsi": self.finsi
        }

        if instruction_kw not in instruction_map.keys():
            raise ValueError(f"Error: Unknown instruction {instruction_kw} in line: {line}")
        else:
            return Instruction(instruction_map[instruction_kw], parameters)

    def run(self):
        """
        Execute the instructions contained in the source code.
        """

        for instruction in self.instructions:
            instruction.execute()

        if self.stdout[-1] == '\n':
            self.stdout = self.stdout[:-1]

    def message(self, parameters):
        """
        message instruction.
        """
        if self.skip:
            return

        result_string = ""

        # find strings between double quotes
        quoted = parameters.split("\"")

        for i, string in enumerate(quoted):
            if string == "":    # skip empty strings
                continue

            if i % 2 == 0:  # Not encapsulated by the quotes

                string = string.strip()  # discard leading and ending whitspaces
                if len(string) == 0:
                    continue

                words = string.split(" ")

                for j, word in enumerate(words):

                    if len(word) == 0:  # skip empty words
                        continue

                    if j+i > 0 and result_string[-1] != " ":
                        result_string += ' '    # add space between each word

                    if word[0] == '$':  # find variables
                        variable_name = word[1:]
                        if variable_name in self.variables.keys():
                            result_string += str(self.variables.get(variable_name))
                        else:
                            raise ValueError(f"Unkown variable: {word}")
                    else:
                        result_string += word
                        if j == len(words) - 1 and i < len(quoted) -1:
                            result_string += " "

            else:           # Between quotes
                result_string += string

        self.stdout += result_string + '\n'

    def incrementer(self, parameters):
        """
        incremeter instruction.
        """

        if self.skip:
            return

        # parse parameters
        if len(parameters.split(' ')) > 2:
            raise ValueError(f'Too many arugments for instruction: incrementer {parameters}')

        if len(parameters.split(' ')) < 2:
            raise ValueError(f'Too few arugments for instruction: incrementer {parameters}')

        variable_name, value = parameters.split(' ')
        self.variables[variable_name] += int(value)

    def appel(self, parameters):
        """
        appel instruction
        """
        if self.skip:
            return

        # parse parameters
        if len(parameters.split(' ')) > 1:
            raise ValueError(f"Too many arguments for function call: appel {parameters}")

        if len(parameters.split(' ')) < 1:
            raise ValueError(f"Not enough arguments for function call: appel {parameters}")

        function_name = parameters.split(" ")[0]

        # make sure the function called exists
        if function_name not in self.functions.keys():
            raise ValueError(f"Unknown function: {function_name} called.")

        for instruction in self.functions.get(function_name):
            instruction.execute()

    def nombre(self, parameters):
        """
        nombre instruction
        """
        if self.skip:
            return

        # parse parameters
        if len(parameters.split(' ')) > 2:
            raise ValueError(f'Too many arugments for variable declaration: nombre {parameters}')

        if len(parameters.split(' ')) < 2:
            raise ValueError(f'Too few arugments for variable declaration: nombre {parameters}')

        variable_name, value = parameters.split(' ')

        # add the new variable to the map
        self.variables[variable_name] = int(value)

    def idle(self, parameters):
        """
        This function does nothing.
        """
        pass

    def si(self, parameters):
        """
        Custom if.
        skips the next instructions if the condition is false
        """
        if self.skip:
            return

        # parsing parameters
        param1, operator, param2 = parameters.split(" ")

        # replacing variables with their value
        if param1[0] == "$":
            variable_name = param1[1:]
            if variable_name in self.variables.keys():
                param1 = self.variables.get(variable_name)
            else:
                raise ValueError(f"Unknown variable: {param1}")
        else:
            # if the parameter is not a variable it is an integer
            param1 = int(param1)

        if param2[0] == "$":
            variable_name = param2[1:]
            if variable_name in self.variables.keys():
                param2 = self.variables.get(variable_name)
            else:
                raise ValueError(f"Unknown variable: {param2}")
        else:
            # if the parameter is not a variable it is an integer
            param2 = int(param2)

        if operator == '<':
            self.skip = not (param1 < param2)
        elif operator == '>':
            self.skip = not (param1 > param2)
        elif operator == '<=':
            self.skip = not (param1 <= param2)
        elif operator == '>=':
            self.skip = not (param1 >= param2)
        elif operator == '!=':
            self.skip = not (param1 != param2)
        elif operator == '==':
            self.skip = not (param1 == param2)
        else:
            raise ValueError(f"Invalid operator: {operator}")

    def finsi(self, parameter):
        """
        reset skip value to false.
        """
        self.skip = False


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 " + sys.argv[0] + " <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    f = open(filename)
    source_code = f.read()
    f.close()

    interpreter = Interpreter(source_code)
    interpreter.find_functions()
    interpreter.remove_comments()
    interpreter.parse_clean_code()
    interpreter.run()
    print(interpreter.stdout)


if __name__ == '__main__':
    main()


