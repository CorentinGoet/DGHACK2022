from unittest import TestCase
from ASMera import Interpreter


class TestInterpreter(TestCase):

    def setUp(self) -> None:
        pass

    def inputOutputTest(self, input_file_path: str, output_file_path: str) -> None:
        # Read input file
        input_file = open(input_file_path, "r")
        src_code = input_file.read()
        input_file.close()

        # Read expected output file
        output_file = open(output_file_path, "r")
        expected_output = output_file.read()
        output_file.close()

        # Run interpreter
        interpreter = Interpreter(src_code)
        interpreter.find_functions()
        interpreter.remove_comments()
        interpreter.parse_clean_code()
        interpreter.run()

        # Compare output with expected
        self.assertEqual(expected_output, interpreter.stdout)

    def testReq1(self) -> None:
        """
        Tests the interpreter on the example_input.txt file provided by the CTF.
        """
        self.inputOutputTest("examples/example_input.txt",
                             "examples/example_output.txt")

    def testReq2(self) -> None:
        """
        Tests the interpreter on the example_incrementer_input.txt provided by the CTF.
        """
        self.inputOutputTest("examples/example_incrementer_input.txt",
                             "examples/example_incrementer_output.txt")

    def testIncrementer(self):
        """
        Tests the incrementer instruction.
        """
        self.inputOutputTest("test/test_incrementer_input.txt",
                             "test/test_incrementer_output.txt")

    def testSi(self):
        """
        Tests the si instruction.
        """
        self.inputOutputTest("test/test_si_input.txt",
                             "test/test_si_output.txt")

    def testMessage(self):
        """
        Tests the message instruction.
        """
        self.inputOutputTest("test/test_message_input.txt",
                             "test/test_message_output.txt")

    def testComments(self):
        """
        Tests the removal of comments
        """
        self.inputOutputTest("test/test_commentaires_input.txt",
                             "test/test_commentaire_output.txt")



