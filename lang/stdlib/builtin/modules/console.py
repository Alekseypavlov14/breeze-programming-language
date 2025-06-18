from stdlib.builtin.declarations import *

# implementation for console output
# defines simplest console output
def console_output_implementation(message: str):
  print(message, end='')

console_output_declaration = FunctionBuiltInDeclaration('_builtin_console_output', 1, console_output_implementation)

# implementation for console input
# defines input with message
def console_input_implementation(message: str):
  return input(message)

console_input_declaration = FunctionBuiltInDeclaration('_builtin_console_input', 1, console_input_implementation)

# export list
declarations = [
  console_output_declaration,
  console_input_declaration,
]
