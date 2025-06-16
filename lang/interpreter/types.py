from interpreter.stack import *

# list of types
NULL_TYPE = 'NULL'

NUMBER_TYPE = 'NUMBER'
STRING_TYPE = 'STRING'
BOOLEAN_TYPE = 'BOOLEAN'

OBJECT_TYPE = 'OBJECT'
LIST_TYPE = 'LIST'
TUPLE_TYPE = 'TUPLE'

FUNCTION_TYPE = 'FUNCTION'

# types that are valid object keys
OBJECT_KEY_TYPES = [STRING_TYPE, NUMBER_TYPE]

# function type stored in container
# closure represents stack where the function was declared
class FunctionValue:
  def __init__(self, callable, closure: Stack):
    self.callable = callable
    self.closure = closure

# to compute value type
def get_value_type(value):
  if value == None:
    return NULL_TYPE
  
  if isinstance(value, (int, float)):
    return NUMBER_TYPE
  if isinstance(value, str):
    return STRING_TYPE
  if isinstance(value, bool):
    return bool
  
  if isinstance(value, dict):
    return OBJECT_TYPE
  if isinstance(value, list):
    return LIST_TYPE
  if isinstance(value, tuple):
    return TUPLE_TYPE
  
  if isinstance(value, FunctionValue):
    return FUNCTION_TYPE
