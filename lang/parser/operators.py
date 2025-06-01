from parser.types.expressions import *
from shared.tokens import *

import math
import inspect

# base precedence 
# use for initializing expression parsing
BASE_PRECEDENCE = -1

# defines operators priority
# from most to least
OPERATOR_PRECEDENCE = [
  (ASSIGN_TOKEN, BinaryOperationExpression),

  (OR_TOKEN, BinaryOperationExpression),
  (AND_TOKEN, BinaryOperationExpression),

  (EQUAL_TOKEN, BinaryOperationExpression),
  (NOT_EQUAL_TOKEN, BinaryOperationExpression),

  (LESS_THAN_TOKEN, BinaryOperationExpression),
  (LESS_THAN_OR_EQUAL_TOKEN, BinaryOperationExpression),
  (GREATER_THAN_TOKEN, BinaryOperationExpression),
  (GREATER_THAN_OR_EQUAL_TOKEN, BinaryOperationExpression),

  (PLUS_ASSIGN_TOKEN, BinaryOperationExpression),
  (MINUS_ASSIGN_TOKEN, BinaryOperationExpression),

  (MULTIPLICATION_ASSIGN_TOKEN, BinaryOperationExpression),
  (DIVISION_ASSIGN_TOKEN, BinaryOperationExpression),

  (PLUS_TOKEN, BinaryOperationExpression),
  (MINUS_TOKEN, BinaryOperationExpression),

  (MULTIPLICATION_TOKEN, BinaryOperationExpression),
  (DIVISION_TOKEN, BinaryOperationExpression),

  (INCREMENT_TOKEN, UnaryOperationExpression),
  (DECREMENT_TOKEN, UnaryOperationExpression),

  (LEFT_SQUARE_BRACKET_TOKEN, GroupingExpression),
  (LEFT_PARENTHESES_TOKEN, GroupingExpression),

  (DOT_TOKEN, BinaryOperationExpression),
]

# get operator tokens
OPERATOR_TOKENS = list(map(lambda group: group[0], OPERATOR_PRECEDENCE))

# operator token precedence getter
# smaller precedence = more important operator
def get_operator_precedence(token: Token):
  # iterate through tokens
  for index in range(len(OPERATOR_TOKENS)):
    # check each token
    if token.type == OPERATOR_TOKENS[index][0]:
      # return precedence
      return index
    
  # fallback value
  return math.inf

def is_unary_operator(operator: Token):
  return is_operator_of_class(operator, UnaryOperationExpression)

def is_binary_operator(operator: Token):
  return is_operator_of_class(operator, BinaryOperationExpression)

def is_grouping_operator(operator: Token):
  return is_operator_of_class(operator, GroupingExpression)

# receives token and class from hierarchy of expression classes
# returns if the token is assigned to the expression class or its derived subclass
def is_operator_of_class(operator: Token, expression_class):
  # iterate through operators
  for token, token_class in OPERATOR_PRECEDENCE:
    if operator == token:
      # check if it is a unary operator
      return inspect.isclass(expression_class) and issubclass(token_class, expression_class)
  
  # return False if not found
  return False

# specifies grouping close tokens
GROUPING_OPERATOR_CLOSING_TOKENS = [
  (LEFT_SQUARE_BRACKET_TOKEN, RIGHT_SQUARE_BRACKET_TOKEN),
  (LEFT_PARENTHESES_TOKEN, RIGHT_PARENTHESES_TOKEN),
]

# util to get closing token by opening token
def get_grouping_operator_closing_token(operator: Token):
  for opening, closing in GROUPING_OPERATOR_CLOSING_TOKENS:
    if opening == operator:
      return closing
    
  # fallback
  return None 
