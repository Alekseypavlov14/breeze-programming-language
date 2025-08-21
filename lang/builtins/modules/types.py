from interpreter.types import *
from interpreter.exceptions import *
from builtins.declarations import *

# maps python type to Breeze type constant name
map_type_to_string = {
  UNKNOWN_TYPE: 'unknown',
  NULL_TYPE: 'null',
  NUMBER_TYPE: 'number',
  STRING_TYPE: 'string',
  BOOLEAN_TYPE: 'boolean',
  OBJECT_TYPE: 'object',
  LIST_TYPE: 'list',
  TUPLE_TYPE: 'tuple',
  FUNCTION_TYPE: 'function',
}

# returns string with type 
def type(value):
  type_value = get_value_type(value)
  return map_type_to_string[type_value]
type_function_declaration = FunctionBuiltInDeclaration('_builtin_types_type', 1, type)


# constructors and mappers for different types
def string_constructor(value):
  type_value = get_value_type(value)

  if type_value == NULL_TYPE:
    return "null"
  
  if type_value == NUMBER_TYPE:
    return str(value)
  
  if type_value == STRING_TYPE:
    return str(value)
  
  if type_value == BOOLEAN_TYPE:
    if value: 
      return "true"
    else: 
      return "false"

  if type_value == LIST_TYPE:
    stringified = "[\n"

    for item in value:
      stringified += f'\t{string_constructor(item)}\n'

    stringified += ']'

    return stringified

  if type_value == TUPLE_TYPE:
    stringified = "(\n"

    for item in value:
      stringified += f'\t{string_constructor(item)}\n'

    stringified += ')'

    return stringified
  
  if type_value == OBJECT_TYPE:
    stringified = "{\n"

    for key, value in value:
      stringified += f'\t{string_constructor(key)}: ${string_constructor(value)}\n'

    stringified += '}'

    return stringified
  
  if type_value == FUNCTION_TYPE:
    return f"function"

  raise ValueError(f'Invalid value passed to string constructor: {value}') 
string_constructor_declaration = FunctionBuiltInDeclaration('_builtin_types_string', 1, string_constructor)

def number_constructor(value):
  type_value = get_value_type(value)

  if type_value == NULL_TYPE:
    return 0
  
  if type_value == NUMBER_TYPE:
    return float(value)
  
  if type_value == STRING_TYPE:
    try:
      return float(value)
    except:
      raise ValueError(f'Invalid value passed to number constructor: {string_constructor(value)}')

  if type_value == BOOLEAN_TYPE:
    return float(value)
  
  raise ValueError(f'Invalid value passed to number constructor: {string_constructor(value)}') 
number_constructor_declaration = FunctionBuiltInDeclaration('_builtin_types_number', 1, number_constructor)

def boolean_constructor(value):
  try:
    return bool(value)
  except:
    raise ValueError(f'Invalid value passed to boolean constructor: {string_constructor(value)}')
boolean_constructor_declaration = FunctionBuiltInDeclaration('_builtin_types_boolean', 1, boolean_constructor)

def list_constructor(value):
  type_value = get_value_type(value)

  if type_value == LIST_TYPE:
    return list(value)
  
  if type_value == TUPLE_TYPE:
    return list(value)
  
  raise ValueError(f'Invalid value passed to list constructor: {string_constructor(value)}') 
list_constructor_declaration = FunctionBuiltInDeclaration('_builtin_types_list', 1, list_constructor)

def tuple_constructor(value):
  type_value = get_value_type(value)

  if type_value == LIST_TYPE:
    return tuple(value)
  
  if type_value == TUPLE_TYPE:
    return tuple(value)
  
  raise ValueError(f'Invalid value passed to tuple constructor: {string_constructor(value)}') 
tuple_constructor_declaration = FunctionBuiltInDeclaration('_builtin_types_tuple', 1, tuple_constructor)

def object_constructor(value):
  type_value = get_value_type(value)

  if type_value == TUPLE_TYPE:
    obj = {}

    for index in range(len((value))):
      obj[index] = value[index]

    return obj
  
  if type_value == LIST_TYPE:
    obj = {}

    for index in range(len((value))):
      obj[index] = value[index]

    return obj
  
  if type_value == OBJECT_TYPE:
    return dict(value)
  
  raise ValueError(f'Invalid value passed to object constructor: {string_constructor(value)}')
object_constructor_declaration = FunctionBuiltInDeclaration('_builtin_types_object', 1, object_constructor)


# export list
declarations = [
  type_function_declaration,

  number_constructor_declaration,
  string_constructor_declaration,
  boolean_constructor_declaration,

  list_constructor_declaration,
  tuple_constructor_declaration,
  object_constructor_declaration,
]
