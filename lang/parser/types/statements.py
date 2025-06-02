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
# type is required
class VariableDeclarationStatement(Statement):
  def __init__(self, type: Expression, name: Token):
    super().__init__()

    self.type = type
    self.name = name

# defines statement for constant declaration
# type is required
class ConstantDeclarationStatement(Statement):
  def __init__(self, type: Expression, name: Token):
    super().__init__()

    self.type = type
    self.name = name

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

# defines statement of function declaration
class FunctionDeclarationStatement(Statement):
  def __init__(self, name: Token, params: list[Expression], body: BlockStatement):
    super().__init__()

    self.name = name
    self.params = params
    self.body = body

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
