from interpreter.stack import *
from interpreter.exceptions import *
from interpreter.types import *

from resolution.module import *

from parser.types.expressions import *
from parser.types.statements import *

from lexer.token import *

from shared.keywords import *
from shared.tokens import *

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
    if is_expression_of_class(expression, NullExpression):
      return
    if is_expression_of_class(expression, LiteralExpression):
      return self.evaluate_literal_expression(expression)
    if is_expression_of_class(expression, IdentifierExpression):
      return self.evaluate_identifier_expression(expression)
    if is_expression_of_class(expression, UnaryOperationExpression):
      return self.evaluate_unary_expression(expression)
    if is_expression_of_class(expression, BinaryOperationExpression):
      return self.evaluate_binary_expression(expression)
    if is_expression_of_class(expression, GroupingExpression):
      return self.evaluate_grouping_expression(expression)
    if is_expression_of_class(expression, GroupingApplicationExpression):
      return self.evaluate_grouping_application_expression(expression)
    
    raise SyntaxError('Invalid expression found')

  # unary expressions
  def evaluate_unary_expression(self, expression: UnaryOperationExpression):
    if is_token_of_type(expression.operator, NOT_TOKEN):
      return self.evaluate_not_expression(expression)
    if is_token_of_type(expression.operator, BIT_NOT_TOKEN):
      return self.evaluate_bit_not_expression(expression)
    if is_token_of_type(expression.operator, INCREMENT_TOKEN):
      return self.evaluate_increment_expression(expression)
    if is_token_of_type(expression.operator, DECREMENT_TOKEN):
      return self.evaluate_decrement_expression(expression)
    
    raise SyntaxError(f'Invalid operator used: {expression.operator}')

  def evaluate_not_expression(self, expression: UnaryOperationExpression):
    container: ReadableContainer = self.evaluate_expression(expression.operand)
    if not is_container_of_type(container, ReadableContainer):
      raise ExpressionError('Operand value is not readable')

    return self.create_readable_container(not container.read())
  
  def evaluate_bit_not_expression(self, expression: UnaryOperationExpression):
    container: ReadableContainer = self.evaluate_expression(expression.operand)
    if not is_container_of_type(container, ReadableContainer):
      raise ExpressionError('Operand value is not readable')
    
    value = container.read()

    if self.is_value_of_type(value, NUMBER_TYPE):
      return self.create_readable_container(~round(value))

    raise TypeError(f'Unary operator {expression.operator.code} with type {get_value_type(value)} is not supported')

  def evaluate_increment_expression(self, expression: UnaryOperationExpression):
    container: TransformContainer = self.evaluate_expression(expression.operand)
    if not is_container_of_type(container, TransformContainer):
      raise ExpressionError('Operand value is not readable and writable')
    
    value = container.read()

    if self.is_value_of_type(value, NUMBER_TYPE):
      container.write(value + 1)
      return container
    
    raise TypeError(f'Unary operator {expression.operator.code} with type {get_value_type(value)} is not supported')

  def evaluate_decrement_expression(self, expression: UnaryOperationExpression):
    container: TransformContainer = self.evaluate_expression(expression.operand)
    if not is_container_of_type(container, TransformContainer):
      raise ExpressionError('Operand value is not readable and writable')
    
    value = container.read()

    if self.is_value_of_type(value, NUMBER_TYPE):
      container.write(value - 1)
      return container
    
    raise TypeError(f'Unary operator {expression.operator.code} with type {get_value_type(value)} is not supported')

  # binary expressions
  def evaluate_binary_expression(self, expression: BinaryOperationExpression):
    if is_token_of_type(expression.operator, ASSIGN_TOKEN):
      return self.evaluate_assign_expression(expression)
    if is_token_of_type(expression.operator, DOT_TOKEN):
      return self.evaluate_member_access_expression(expression)
    if is_token_of_type(expression.operator, PLUS_TOKEN):
      return self.evaluate_addition_expression(expression)
    if is_token_of_type(expression.operator, MINUS_TOKEN):
      return self.evaluate_subtraction_expression(expression)
    if is_token_of_type(expression.operator, MULTIPLICATION_TOKEN):
      return self.evaluate_multiplication_expression(expression)
    if is_token_of_type(expression.operator, DIVISION_TOKEN):
      return self.evaluate_division_expression(expression)
    if is_token_of_type(expression.operator, EXPONENTIAL_TOKEN):
      return self.evaluate_exponential_expression(expression)
    if is_token_of_type(expression.operator, REMAINDER_TOKEN):
      return self.evaluate_remainder_expression(expression)
    if is_token_of_type(expression.operator, BIT_AND_TOKEN):
      return self.evaluate_bit_and_expression(expression)
    if is_token_of_type(expression.operator, BIT_OR_TOKEN):
      return self.evaluate_bit_or_expression(expression)
    if is_token_of_type(expression.operator, BIT_XOR_TOKEN):
      return self.evaluate_bit_xor_expression(expression)
    if is_token_of_type(expression.operator, LEFT_SHIFT_TOKEN):
      return self.evaluate_left_shift_expression(expression)
    if is_token_of_type(expression.operator, RIGHT_SHIFT_TOKEN):
      return self.evaluate_right_shift_expression(expression)
    if is_token_of_type(expression.operator, PLUS_ASSIGN_TOKEN):
      return self.evaluate_addition_and_assign_expression(expression)
    if is_token_of_type(expression.operator, MINUS_ASSIGN_TOKEN):
      return self.evaluate_subtraction_and_assign_expression(expression)
    if is_token_of_type(expression.operator, MULTIPLICATION_ASSIGN_TOKEN):
      return self.evaluate_multiplication_and_assign_expression(expression)
    if is_token_of_type(expression.operator, DIVISION_ASSIGN_TOKEN):
      return self.evaluate_division_and_assign_expression(expression)
    if is_token_of_type(expression.operator, EXPONENTIAL_ASSIGN_TOKEN):
      return self.evaluate_exponential_and_assign_expression(expression)
    if is_token_of_type(expression.operator, REMAINDER_ASSIGN_TOKEN):
      return self.evaluate_remainder_and_assign_expression(expression)
    if is_token_of_type(expression.operator, BIT_AND_ASSIGN_TOKEN):
      return self.evaluate_bit_and_and_assign_expression(expression)
    if is_token_of_type(expression.operator, BIT_OR_ASSIGN_TOKEN):
      return self.evaluate_bit_or_and_assign_expression(expression)
    if is_token_of_type(expression.operator, BIT_XOR_ASSIGN_TOKEN):
      return self.evaluate_bit_xor_and_assign_expression(expression)
    if is_token_of_type(expression.operator, LEFT_SHIFT_ASSIGN_TOKEN):
      return self.evaluate_left_shift_and_assign_expression(expression)
    if is_token_of_type(expression.operator, RIGHT_SHIFT_ASSIGN_TOKEN):
      return self.evaluate_right_shift_and_assign_expression(expression)
    if is_token_of_type(expression.operator, OR_TOKEN):
      return self.evaluate_or_expression(expression)
    if is_token_of_type(expression.operator, AND_TOKEN):
      return self.evaluate_and_expression(expression)
    if is_token_of_type(expression.operator, EQUAL_TOKEN):
      return self.evaluate_equal_expression(expression)
    if is_token_of_type(expression.operator, NOT_EQUAL_TOKEN):
      return self.evaluate_not_equal_expression(expression)
    if is_token_of_type(expression.operator, LEFT_SHIFT_TOKEN):
      return self.evaluate_left_shift_expression(expression)
    if is_token_of_type(expression.operator, GREATER_THAN_TOKEN):
      return self.evaluate_greater_than_expression(expression)
    if is_token_of_type(expression.operator, LESS_THAN_TOKEN):
      return self.evaluate_less_than_expression(expression)
    if is_token_of_type(expression.operator, GREATER_THAN_OR_EQUAL_TOKEN):
      return self.evaluate_greater_than_or_equal_expression(expression)
    if is_token_of_type(expression.operator, LESS_THAN_OR_EQUAL_TOKEN):
      return self.evaluate_less_than_or_equal_expression(expression)
    
    raise SyntaxError(f'Invalid operator used: {expression.operator}')

  def evaluate_assign_expression(self, expression: BinaryOperationExpression):
    left: WriteableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, WriteableContainer):
      raise ExpressionError('Left value is not writable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left.write(right.read())

    return left

  def evaluate_member_access_expression(self, expression: BinaryOperationExpression):
    obj_container: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(obj_container, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    if not is_expression_of_class(expression.right, IdentifierExpression):
      raise SyntaxError('Object member accessed by dot has to be a literal')
  
    obj: dict = obj_container.read()
    value_container = obj.get(expression.right.name)

    if not is_container_of_type(value_container, ReadableContainer):
      raise ValueError('Accessed value is not readable')
    
    return value_container

  def evaluate_addition_expression(self, expression: BinaryOperationExpression):
    left: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()

    # handle number addition
    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      return self.create_readable_container(left.value + right_value)
    
    # handle string concatenation
    if self.is_value_of_type(left_value, STRING_TYPE) and self.is_value_of_type(right_value, STRING_TYPE):
      return self.create_readable_container(left_value + right_value)
    
    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')

  def evaluate_subtraction_expression(self, expression: BinaryOperationExpression):
    left: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()

    # handle number subtraction
    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      return self.create_readable_container(left.value - right_value)
    
    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')

  def evaluate_multiplication_expression(self, expression: BinaryOperationExpression):
    left: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()

    # handle number multiplication
    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      return self.create_readable_container(left.value * right_value)
    
    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')

  def evaluate_division_expression(self, expression: BinaryOperationExpression):
    left: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()

    # handle number division
    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      if right_value == 0:
        raise ValueError('Division by zero is not allowed')
      
      return self.create_readable_container(left.value / right_value)
    
    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')

  def evaluate_exponential_expression(self, expression: BinaryOperationExpression):
    left: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()

    # handle exponential
    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      if left_value < 0:
        raise ValueError('Exponential with negative base is not allowed')
      
      return self.create_readable_container(left.value ** right_value)
    
    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')

  def evaluate_remainder_expression(self, expression: BinaryOperationExpression):
    left: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()

    # handle remainder
    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      return self.create_readable_container(left.value % right_value)
    
    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')

  def evaluate_bit_and_expression(self, expression: BinaryOperationExpression):
    left: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()
    
    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      return self.create_readable_container(round(left_value) & round(right_value))
    
    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')

  def evaluate_bit_or_expression(self, expression: BinaryOperationExpression):
    left: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()
    
    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      return self.create_readable_container(round(left_value) | round(right_value))
    
    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')

  def evaluate_bit_xor_expression(self, expression: BinaryOperationExpression):
    left: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()
    
    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      return self.create_readable_container(round(left_value) ^ round(right_value))
    
    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')

  def evaluate_left_shift_expression(self, expression: BinaryOperationExpression):
    left: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()
    
    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      return self.create_readable_container(round(left_value) << round(right_value))
    
    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')

  def evaluate_right_shift_expression(self, expression: BinaryOperationExpression):
    left: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()
    
    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      return self.create_readable_container(round(left_value) >> round(right_value))
    
    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')

  def evaluate_addition_and_assign_expression(self, expression: BinaryOperationExpression):
    left: TransformContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, TransformContainer):
      raise ExpressionError('Left value is not readable and writable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()
    
    # handle number addition
    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      left.write(left_value + right_value)
      return left
    
    # handle string concatenation
    if self.is_value_of_type(left_value, STRING_TYPE) and self.is_value_of_type(right_value, STRING_TYPE):
      left.write(left_value + right_value)
      return left
    
    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')

  def evaluate_subtraction_and_assign_expression(self, expression: BinaryOperationExpression):
    left: TransformContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, TransformContainer):
      raise ExpressionError('Left value is not readable and writable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()
    
    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      left.write(left_value - right_value)
      return left

    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')
  
  def evaluate_multiplication_and_assign_expression(self, expression: BinaryOperationExpression):
    left: TransformContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, TransformContainer):
      raise ExpressionError('Left value is not readable and writable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()
    
    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      left.write(left_value * right_value)
      return left

    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')
  
  def evaluate_division_and_assign_expression(self, expression: BinaryOperationExpression):
    left: TransformContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, TransformContainer):
      raise ExpressionError('Left value is not readable and writable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()
    
    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      if right_value == 0:
        raise ValueError('Division by zero is not allowed')
    
      left.write(left_value / right_value)
      return left
    
    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')
  
  def evaluate_exponential_and_assign_expression(self, expression: BinaryOperationExpression):
    left: TransformContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, TransformContainer):
      raise ExpressionError('Left value is not readable and writable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()
    
    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      if left_value < 0:
        raise ValueError('Exponential with negative base is not allowed')
    
      left.write(left_value ** right_value)
      return left

    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')
  
  def evaluate_remainder_and_assign_expression(self, expression: BinaryOperationExpression):
    left: TransformContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, TransformContainer):
      raise ExpressionError('Left value is not readable and writable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()

    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      left.write(left_value % right_value)
      return left

    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')
  
  def evaluate_bit_and_and_assign_expression(self, expression: BinaryOperationExpression):
    left: TransformContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, TransformContainer):
      raise ExpressionError('Left value is not readable and writable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()

    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      left.write(round(left_value) & round(right_value))
      return left

    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')
  
  def evaluate_bit_or_and_assign_expression(self, expression: BinaryOperationExpression):
    left: TransformContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, TransformContainer):
      raise ExpressionError('Left value is not readable and writable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()

    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      left.write(round(left_value) | round(right_value))
      return left

    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')
  
  def evaluate_bit_xor_and_assign_expression(self, expression: BinaryOperationExpression):
    left: TransformContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, TransformContainer):
      raise ExpressionError('Left value is not readable and writable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()

    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      left.write(round(left_value) ^ round(right_value))
      return left
    
    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')
  
  def evaluate_left_shift_and_assign_expression(self, expression: BinaryOperationExpression):
    left: TransformContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, TransformContainer):
      raise ExpressionError('Left value is not readable and writable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()

    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      left.write(round(left_value) << round(right_value))
      return left
    
    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')
  
  def evaluate_right_shift_and_assign_expression(self, expression: BinaryOperationExpression):
    left: TransformContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, TransformContainer):
      raise ExpressionError('Left value is not readable and writable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()
    
    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      left.write(round(left_value) >> round(right_value))
      return left
    
    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')

  def evaluate_or_expression(self, expression: BinaryOperationExpression):
    left: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    # if left is true - return and skip right
    if left.read(): return left

    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    return right
  
  def evaluate_and_expression(self, expression: BinaryOperationExpression):
    left: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    # if left is false - return and skip right
    if not left.read(): return left

    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    return right

  def evaluate_equal_expression(self, expression: BinaryOperationExpression):
    left: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    return self.create_readable_container(left.read() == right.read())
  
  def evaluate_not_equal_expression(self, expression: BinaryOperationExpression):
    left: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    return self.create_readable_container(left.read() != right.read())
  
  def evaluate_greater_than_expression(self, expression: BinaryOperationExpression):
    left: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()
    
    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      return self.create_readable_container(left_value > right_value)
    
    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')
  
  def evaluate_less_than_expression(self, expression: BinaryOperationExpression):
    left: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()
    
    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      return self.create_readable_container(left_value < right_value)
    
    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')
  
  def evaluate_greater_than_or_equal_expression(self, expression: BinaryOperationExpression):
    left: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()
    
    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      return self.create_readable_container(left_value >= right_value)
    
    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')
  
  def evaluate_less_than_or_equal_expression(self, expression: BinaryOperationExpression):
    left: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(right, ReadableContainer):
      raise ExpressionError('Right container is not readable')
    
    left_value = left.read()
    right_value = right.read()
    
    if self.is_value_of_type(left_value, NUMBER_TYPE) and self.is_value_of_type(right_value, NUMBER_TYPE):
      return self.create_readable_container(left_value <= right_value)
    
    raise TypeError(f'Binary operation {expression.operator.code} with types {get_value_type(left_value)} and {get_value_type(right_value)} is not supported')
  
  # grouping expressions
  def evaluate_grouping_expression(self, expression: GroupingExpression):
    if is_token_of_type(expression.operator, LEFT_PARENTHESES_TOKEN):
      return self.evaluate_parentheses_expression(expression)
    if is_token_of_type(expression.operator, LEFT_SQUARE_BRACKET_TOKEN):
      return self.evaluate_square_brackets_expression(expression)

    raise SyntaxError(f'Invalid operator used: {expression.operator}')

  def evaluate_parentheses_expression(self, expression: GroupingExpression):
    # parentheses without application indicate tuple literal
    
    elements = []

    for exp in expression.expressions:
      elements.append(self.evaluate_expression(exp))

    return self.create_readable_container(tuple(elements))
  
  def evaluate_square_brackets_expression(self, expression: GroupingExpression):
    # square brackets without application indicate LIST literal

    elements = []

    for exp in expression.expressions:
      elements.append(self.evaluate_expression(exp))

    return self.create_readable_container(elements)

  # grouping application expressions
  def evaluate_grouping_application_expression(self, expression: GroupingApplicationExpression):
    if is_token_of_type(expression.right.operator, LEFT_PARENTHESES_TOKEN):
      return self.evaluate_parentheses_application_expression(expression)
    if is_token_of_type(expression.right.operator, LEFT_SQUARE_BRACKET_TOKEN):
      return self.evaluate_square_brackets_application_expression(expression)

    raise SyntaxError(f'Invalid operator used by application: {expression.operator}')

  def evaluate_parentheses_application_expression(self, expression: GroupingApplicationExpression):
    # parentheses in application is function call

    left: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    left_value = left.read()
    if not self.is_value_of_type(left_value, FUNCTION_TYPE):
      raise ValueError(f'{left_value} is not callable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Right value is not readable')
    
    right_value: list[ReadableContainer] = right.read()
    if not self.is_value_of_type(right, TUPLE_TYPE):
      raise SyntaxError('Invalid composition')
    
    arguments = []

    for argument in list(right_value):
      if not is_container_of_type(argument, ReadableContainer):
        raise ExpressionError('Argument is not readable')

      arguments.append(argument.read())

    # execute function
    return_value = left_value(*arguments)

    return self.create_readable_container(return_value)

  def evaluate_square_brackets_application_expression(self, expression: GroupingApplicationExpression):
    # square brackets in application is obj member access

    left: ReadableContainer = self.evaluate_expression(expression.left)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Left value is not readable')
    
    left_value = left.read()
    if not self.is_value_of_type(left_value, OBJECT_TYPE):
      raise SyntaxError('Cannot access members of non-object type')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Right value is not readable')
    
    right_value = right.read()
    if not self.is_value_of_type(right_value, LIST_TYPE):
      raise SyntaxError('Invalid member access')
    
    if len(right_value) != 1:
      raise SyntaxError('Member access has to be evaluated as a literal')
    
    selector: ReadableContainer = right_value[0]
    if not is_container_of_type(selector, ReadableContainer):
      raise ExpressionError('Member access expression is not readable')
    
    selector_value = selector.read()
    if not self.is_value_of_type(selector_value, *OBJECT_KEY_TYPES):
      raise SyntaxError(f'Key expression has to be literal but {get_value_type(selector_value)} received')
    
    return left_value[selector_value]

  # association expression
  def evaluate_curly_braces_expression(self, expression: AssociationExpression):
    # curly braces without application indicate OBJECT literal

    obj = {}

    # parse entries
    for key, value in expression.entries:
      # parse key

      # handle string keys without quotes (allowed for object keys)
      if is_expression_of_class(key, IdentifierExpression):
        parsed_key: str = key.name

      # handle literal keys
      elif is_expression_of_class(key, LiteralExpression):
        # validate key type
        if not self.is_value_of_type(key.value, OBJECT_KEY_TYPES):
          raise SyntaxError('Invalid key expression')
        
        parsed_key: str = key.value
      
      # handle dynamic keys (in [])
      elif is_expression_of_class(key, GroupingExpression):
        key_container: ReadableContainer = self.evaluate_expression(key)
        if not is_container_of_type(key_container, ReadableContainer):
          raise SyntaxError('Key expression is not readable')
        
        key_value = key_container.read()
        if not get_value_type(key_value, LIST_TYPE):
          raise SyntaxError('Invalid key expression')
        
        # validate "list-like" expression length
        if len(key_value) != 1:
          raise ExpressionError('Dynamic key expression must be evaluated as a literal')
        
        # get dynamic key
        first_container: ReadableContainer = key_value[0]
        if not is_container_of_type(first_container, ReadableContainer):
          raise SyntaxError('Key expression is not readable')
        
        # validate key type
        first_container_value = first_container.read()
        if not self.is_value_of_type(first_container_value, *OBJECT_KEY_TYPES):
          raise SyntaxError(f'Key expression has to be literal but {get_value_type(first_container_value)} received')

        parsed_key = first_container_value
      
      # parse value
      value_container = self.evaluate_expression(value)
      if not is_container_of_type(value_container, ReadableContainer):
        raise ExpressionError('Value is not readable')
      
      # set parsed entry
      obj[parsed_key] = value_container

    return self.create_readable_container(obj)

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


  # creates anonymous readable containers for expression evaluations
  def create_readable_container(self, value):
    return ReadableContainer('', value)
  
  # check data types of values
  def is_value_of_type(self, value, *types: list[str]):
    return get_value_type(value) in types
  