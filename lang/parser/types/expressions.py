from lexer.token import Token
from parser.types.node import Node

# parent class for all expressions
# has no behavior
class Expression(Node):
  pass

# for expression fallback
# use to indicate lack of optional expression
class NullExpression(Expression):
  pass

# parent class for operations
# has no behavior
class OperationExpression(Expression): 
  pass

# define types of unary operation
class UnaryOperationExpression(OperationExpression):
  def __init__(self, operator: Token, operand: Expression):
    super().__init__()

    self.operator = operator
    self.operand = operand

# for prefix unary operations
class PrefixUnaryOperationExpression(UnaryOperationExpression):
  def __init__(self, operator: Token, operand: Expression):
    super().__init__(operator, operand)

# for suffix unary operations
class SuffixUnaryOperationExpression(UnaryOperationExpression):
  def __init__(self, operator: Token, operand: Expression):
    super().__init__(operator, operand)

# for either prefix or suffix (affix)
class AffixUnaryOperationExpression(UnaryOperationExpression):
  def __init__(self, operator: Token, operand: Expression):
    super().__init__(operator, operand)

# defines binary operations
class BinaryOperationExpression(OperationExpression):
  def __init__(self, operator: Token, left: Expression, right: Expression):
    super().__init__()

    self.operator = operator
    self.left = left
    self.right = right

# for strings and numbers
class LiteralExpression(Expression):
  def __init__(self, value: Token):
    super().__init__()

    self.value = value

# for accessing/writing to identifiers
class IdentifierExpression(Expression):
  def __init__(self, name: Token):
    super().__init__()

    self.name = name

# for grouping expressions
# handle (), [] etc.
class GroupingExpression(Expression):
  def __init__(self, operator: Token, expressions: list[Expression]):
    super().__init__()

    self.operator = operator
    self.expressions = expressions

# for handling function calls and array indexing
# has to explicit operator and specifies right side
class GroupingApplicationExpression(Expression):
  def __init__(self, left: Expression, right: GroupingExpression):
    super().__init__()

    self.left = left
    self.right = right

# for association (hashmap) expressions
# represents { a: 1, b: 2, c: 3 } maps
class AssociationExpression(Expression):
  def __init__(self, entries: list[tuple[Expression, Expression]]):
    super().__init__()

    self.entries = entries


# util to check if expression is of one of specified expressions
def is_expression_of_class(expression: Expression, *expressions: Expression):
  return isinstance(expression, tuple(expressions))
