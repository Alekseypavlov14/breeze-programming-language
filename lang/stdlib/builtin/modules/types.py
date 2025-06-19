from interpreter.types import *
from stdlib.builtin.declarations import *

# list of type constant literals
unknown_type_declaration = ConstantBuiltInDeclaration('_builtin_types_unknown', UNKNOWN_TYPE)

null_type_declaration = ConstantBuiltInDeclaration('_builtin_types_null', NULL_TYPE)

number_type_declaration = ConstantBuiltInDeclaration('_builtin_types_number', NUMBER_TYPE)
string_type_declaration = ConstantBuiltInDeclaration('_builtin_types_string', STRING_TYPE)
boolean_type_declaration = ConstantBuiltInDeclaration('_builtin_types_boolean', UNKNOWN_TYPE)

object_type_declaration = ConstantBuiltInDeclaration('_builtin_types_object', OBJECT_TYPE)
list_type_declaration = ConstantBuiltInDeclaration('_builtin_types_list', LIST_TYPE)
tuple_type_declaration = ConstantBuiltInDeclaration('_builtin_types_tuple', TUPLE_TYPE)

function_type_declaration = ConstantBuiltInDeclaration('_builtin_types_function', FUNCTION_TYPE)

# maps python type to Breeze type constant name
map_type_to_string = {
  [UNKNOWN_TYPE]: 'unknown',
  [NULL_TYPE]: 'null',
  [NUMBER_TYPE]: 'number',
  [STRING_TYPE]: 'string',
  [BOOLEAN_TYPE]: 'boolean',
  [OBJECT_TYPE]: 'object',
  [LIST_TYPE]: 'list',
  [TUPLE_TYPE]: 'tuple',
  [FUNCTION_TYPE]: 'function',
}

# returns string with type 
def type(value):
  type_value = get_value_type(value)
  return map_type_to_string[type_value]

type_function_declaration = FunctionBuiltInDeclaration('_builtin_types_type', 1, type)


# export list
declarations = [
  unknown_type_declaration,
  null_type_declaration,
  number_type_declaration,
  string_type_declaration,
  boolean_type_declaration,
  object_type_declaration,
  list_type_declaration,
  tuple_type_declaration,
  function_type_declaration
]
