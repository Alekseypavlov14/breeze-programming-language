from interpreter.stack import *
from interpreter.exceptions import *
from resolution.module import *
from parser.types.expressions import *
from parser.types.statements import *
from shared.keywords import *
from shared.tokens import *
from lexer.token import *

# executes AST
class Interpreter:
  def __init__(self):
    # modules of application
    self.modules: list[Module] = []
    # list of stacks for each module
    self.stacks: list[Stack] = []

    # alias for current executing module
    # order of execution is defined by Resolver
    self.current_module: Module | None = None
    # represents the index of current module
    # equals -1 if no current module
    self.current_module_index = -1
    
    # alias for current stack
    # using imported functions requires switching the stack
    self.current_stack: Stack | None = None

  # method to load app modules to application
  # creates stack for each module
  def load_modules(self, modules: list[Module]):
    # set modules list
    self.modules = modules
    # create stacks for each module
    self.stacks = [Stack() for _ in modules]

  # method that executes the list of modules
  def execute(self):
    pass

  # execute statements

  def execute_statement(self):
    pass

  # evaluate expressions
  
  # this methods delegates evaluation based on expression type
  def evaluate_expression(self, expression: Expression):
    pass

  # binary expressions
  def evaluate_binary_expression(self, expression: Expression):
    pass

  def evaluate_addition_expression(self, expression: BinaryOperationExpression):
    left = self.evaluate_expression(expression.left)
    right = self.evaluate_expression(expression.right)

  def evaluate_subtraction_expression(self, expression: BinaryOperationExpression):
    pass

  # fundamental expressions
  def evaluate_identifier_expression(self, expression: IdentifierExpression):
    return self.current_stack.get_container_by_name(expression.name)

  def evaluate_literal_expression(self, expression: LiteralExpression):
    if is_token_of_type(expression.value, STRING_TOKEN):
      return self.create_readable_container(expression.value.code)
    if is_token_of_type(expression.value, NUMBER_TOKEN):
      return self.create_readable_container(float(expression.value.code))
    if is_token_of_type(expression.value, map_keyword_to_token(TRUE_KEYWORD)):
      return self.create_readable_container(True)
    if is_token_of_type(expression.value, map_keyword_to_token(FALSE_KEYWORD)):
      return self.create_readable_container(False)
    if is_token_of_type(expression.value, map_keyword_to_token(NULL_KEYWORD)):
      return self.create_readable_container(None)
    
    raise ExpressionError(f'Error during literal parsing: {expression.value}')

  # utils
  def create_readable_container(self, value):
    return ReadableContainer('', value)
