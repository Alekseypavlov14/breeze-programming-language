from lexer.token import Token
from parser.types.node import Node
from parser.types.expressions import *

# parent class for all statements
# has no behavior
class Statement(Node):
  pass

# handles standalone expression as statement
class ExpressionStatement(Statement):
  def __init__(self, expression: Expression):
    super().__init__()

    self.expression = expression

# defines block of statements 
class BlockStatement(Statement):
  def __init__(self, statements: list[Statement] = []):
    super().__init__()

    self.statements = statements

# defines statement of variable declaration
# can be used without initialization
class VariableDeclarationStatement(Statement):
  def __init__(self, name: Token, initialization: Expression):
    super().__init__()

    self.name = name
    self.initialization = initialization

# defines statement for constant declaration
class ConstantDeclarationStatement(Statement):
  def __init__(self, name: Token, initialization: Expression):
    super().__init__()

    self.name = name
    self.initialization = initialization

# defines statement for if/else
# statement for branches allow using single line branches and "else if"
class ConditionStatement(Statement):
  def __init__(self, condition: Expression, then_branch: Statement, else_branch: Statement = None):
    super().__init__()
    
    self.condition = condition
    self.then_branch = then_branch
    self.else_branch = else_branch

# defines statement for while loop
class WhileStatement(Statement):
  def __init__(self, condition: Expression, body: Statement):
    super().__init__()

    self.condition = condition
    self.body = body

# defines statement for for loop
class ForStatement(Statement):
  def __init__(self, initializer: Statement, condition: Expression, increment: Expression, body: Statement):
    super().__init__()

    self.initializer = initializer
    self.condition = condition
    self.increment = increment
    self.body = body

# define break statement
class BreakStatement(Statement):
  def __init__(self):
    super().__init__()

# define continue statement
class ContinueStatement(Statement):
  def __init__(self):
    super().__init__()

# defines statement of function declaration
class FunctionDeclarationStatement(Statement):
  def __init__(self, name: Token, params: list[Expression], body: BlockStatement):
    super().__init__()

    self.name = name
    self.params = params
    self.body = body

# defines return statement
class ReturnStatement(Statement):
  def __init__(self, returns: Expression):
    super().__init__()

    self.returns = returns

# defines class statement
class ClassDeclarationStatement(Statement):
  def __init__(self, name: Token):
    super().__init__()

    self.name = name

# defines import statement 
class ImportStatement(Statement):
  def __init__(self, path: LiteralExpression, imports: list[Expression]):
    super().__init__()

    self.path = path
    self.imports = imports

# defines export statement
class ExportStatement(Statement):
  def __init__(self, exports: Statement):
    super().__init__()

    self.exports = exports


# utils to check if statement belongs to one specified classes
def is_statement_of_class(statement, *statements: Statement):
  return isinstance(statement, tuple(statements))
