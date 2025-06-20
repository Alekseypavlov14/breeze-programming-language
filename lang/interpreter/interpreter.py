from interpreter.stack import *
from interpreter.exports import *
from interpreter.exceptions import *
from interpreter.types import *

from resolution.resolver import *
from resolution.module import *

from stdlib.builtin.declarations import *

from parser.types.expressions import *
from parser.types.statements import *

from lexer.token import *

from shared.keywords import *
from shared.tokens import *

# statements will have depth to prevent their execution in wrong places
BASE_DEPTH = 0

# executes modules consecutively
# contains list of Stacks that save values created during execution
# handles imports and exports
class Interpreter:
  def __init__(self, resolver: Resolver):
    # resolver instance
    self.resolver = resolver
    # builtins scope
    self.builtins = Scope()

    # modules of application
    self.modules: list[Module] = []
    # list of stacks for each module
    self.stacks: list[Stack] = []
    # list of Exports for each module
    self.exports: list[Exports] = []

    # alias for current executing module
    # order of execution is defined by Resolver
    self.current_module: Module | None = None
    # represents the index of current module
    # equals -1 if no current module
    self.current_module_index = -1
    
    # alias for current stack
    # using imported functions requires switching the stack
    self.current_stack: Stack | None = None

    # alias for current exports
    # exported declarations will be added to this instance
    self.current_exports: Exports | None = None

  # Step 1) Load application modules
  # method to load app modules to application (sorted)
  # creates stack and exports for each module
  def load_modules(self, modules: list[Module]):
    # set modules list
    self.modules = modules
    # create stacks for each module
    self.stacks = [Stack() for _ in modules]
    # create exports for each module
    self.exports = [Exports() for _ in modules]

  # Step 2) Register builtins 
  def register_builtins(self, builtins: list[BuiltInDeclaration]):
    for builtin in builtins:
      # insert builtin in scope
      self.execute_builtin_declaration(builtin)

    for stack in self.stacks:
      # insert builtins scope to all stacks
      stack.insert_scope(self.builtins)

  # Step 3) Execute application
  # method that executes the list of modules
  def execute(self):
    # initialize pointer
    self.current_module_index = 0

    # execute each module
    for module in self.modules:
      # define aliases
      self.current_module = self.modules[self.current_module_index]
      self.current_stack = self.stacks[self.current_module_index]
      self.current_exports = self.exports[self.current_module_index]

      # create initial scope for current stack
      self.current_stack.add_scope()

      # execute statements in module root
      for statement in module.content.statements:
        self.execute_statement(statement, BASE_DEPTH)

      # go to next module
      self.current_module_index += 1

  # execute statements

  def execute_statement(self, statement: Statement, depth: int):
    if is_statement_of_class(statement, BlockStatement):
      return self.execute_block_statement(statement, depth)
    if is_statement_of_class(statement, VariableDeclarationStatement):
      return self.execute_variable_declaration_statement(statement)
    if is_statement_of_class(statement, ConstantDeclarationStatement):
      return self.execute_constant_declaration_statement(statement)
    if is_statement_of_class(statement, ConditionStatement):
      return self.execute_condition_statement(statement, depth)
    if is_statement_of_class(statement, WhileStatement):
      return self.execute_while_statement(statement, depth)
    if is_statement_of_class(statement, ForStatement):
      return self.execute_for_statement(statement, depth)
    if is_statement_of_class(statement, BreakStatement):
      return self.execute_break_statement(statement)
    if is_statement_of_class(statement, ConditionStatement):
      return self.execute_continue_statement(statement)
    if is_statement_of_class(statement, FunctionDeclarationStatement):
      return self.execute_function_declaration_statement(statement, depth)
    if is_statement_of_class(statement, ReturnStatement):
      return self.execute_return_statement(statement)
    if is_statement_of_class(statement, ImportStatement):
      return self.execute_import_statement(statement, depth)
    if is_statement_of_class(statement, ExportStatement):
      return self.execute_export_statement(statement, depth)
    if is_statement_of_class(statement, ExpressionStatement):
      return self.execute_expression_statement(statement)
  
    raise StatementError(f'Invalid statement is used')

  def execute_block_statement(self, statement: BlockStatement, depth: int):
    # block of statements has new scope
    self.current_stack.add_scope()

    for stat in statement.statements:
      # increment depth
      self.execute_statement(stat, depth + 1)

    # remove scope afterwards
    self.current_stack.remove_scope()

  def execute_variable_declaration_statement(self, statement: VariableDeclarationStatement):
    # default variable value
    initialization = TransformContainer('', None)

    if statement.initialization:
      initialization: ReadableContainer = self.evaluate_expression(statement.initialization)
      if not is_container_of_type(initialization, ReadableContainer):
        raise ValueError('Variable initializer is not readable')

    variable_container = TransformContainer(statement.name.code, initialization.read())
    self.current_stack.add_container(variable_container)

    return variable_container

  def execute_constant_declaration_statement(self, statement: ConstantDeclarationStatement):
    initialization: ReadableContainer = self.evaluate_expression(statement.initialization)
    if not is_container_of_type(initialization, ReadableContainer):
      raise ValueError('Constant initializer is not readable')
    
    constant_container = ReadableContainer(statement.name.code, initialization.read())
    self.current_stack.add_container(constant_container)

    return constant_container

  def execute_condition_statement(self, statement: ConditionStatement, depth: int):
    condition: ReadableContainer = self.evaluate_expression(statement.condition)
    if not is_container_of_type(condition, ReadableContainer):
      raise ExpressionError('Condition is not a readable container')

    if condition.read():
      self.execute_statement(statement.then_branch, depth + 1)

    elif statement.else_branch:
      self.execute_statement(statement.else_branch, depth + 1)

  def execute_while_statement(self, statement: WhileStatement, depth: int):
    while True:
      condition: ReadableContainer = self.evaluate_expression(statement.condition)
      if not is_container_of_type(condition, ReadableContainer):
        raise ExpressionError('Condition is not readable')
      
      if not condition.read():
        break

      # handle breaks and continues
      try:
        self.execute_statement(statement.body, depth + 1)

      except BreakException:
        break
      except ContinueException:
        continue

  def execute_for_statement(self, statement: ForStatement, depth: int):
    self.current_stack.add_scope()

    self.execute_statement(statement.initializer, depth + 1)

    while True:
      condition: ReadableContainer = self.evaluate_expression(statement.condition)
      if not is_container_of_type(condition, ReadableContainer):
        raise ExpressionError('Condition is not readable')
      
      if not condition.read():
        break

      # handle breaks and continues
      try:
        self.execute_statement(statement.body, depth + 1)

      except BreakException:
        break
      except ContinueException:
        self.evaluate_expression(statement.increment)
        continue

      self.evaluate_expression(statement.increment)

    self.current_stack.remove_scope()

  def execute_break_statement(self, statement: BreakStatement):
    raise BreakException() # will be handled in loop
  
  def execute_continue_statement(self, statement: ContinueStatement):
    raise ContinueException() # will be handled in loop

  def execute_function_declaration_statement(self, statement: FunctionDeclarationStatement, depth: int):
    # remember current stack as reference
    closure = self.current_stack.copy()

    # create function callable
    def declared_function(*arguments: ReadableContainer):
      # validate arguments containers
      for argument in arguments:
        if not is_container_of_type(argument, ReadableContainer):
          raise ExpressionError('Argument is not readable')

      parameters_amount = len(statement.params)
      required_parameters_amount = parameters_amount
      passed_arguments = len(arguments)

      # flag that indicates that all next parameters are optional
      optional_argument_found = False

      # mention that parameters with default values are optional
      for param in statement.params:
        # prevent required parameter follow optional
        if not param.defaultValue and optional_argument_found:
          raise ParameterError('Required argument cannot follow optional one')

        if param.defaultValue:  
          required_parameters_amount -= 1
          optional_argument_found = True
        
      # check if arguments are less than enough
      if passed_arguments < required_parameters_amount:
        raise ValueError(f'{required_parameters_amount} parameters are required but {passed_arguments} are received')

      # check if arguments are more than possible 
      if passed_arguments > parameters_amount:
        raise ValueError(f'{parameters_amount} can be passed but {passed_arguments} are received')
      
      # remember origin stack where function was called
      origin_stack = self.current_stack

      # switch scope to function closure
      self.current_stack = closure
      # create scope for function
      self.current_stack.add_scope()

      # initialize parameters
      for param_index in range(len(statement.params)):
        param = statement.params[param_index]

        # compute argument value
        if param_index < passed_arguments:
          # assign passed value
          value: ReadableContainer = arguments[param_index]
        else:
          # evaluate default value
          value: ReadableContainer = self.evaluate_expression(statement.params[param_index].defaultValue)
          if not is_container_of_type(value, ReadableContainer):
            raise ExpressionError('Default value is not readable')
          
        # compose parameter as variable
        parameter_container = TransformContainer(param.name.code, value.read())

        # save variable
        self.current_stack.add_container(parameter_container)

      # initialize returned value
      returned_value = self.create_readable_container(None)

      # execute function
      try:
        self.execute_statement(statement.body, depth + 1)
      except ReturnException as returned:
        # read function return value
        returned_value = returned.value

        if not is_container_of_type(returned_value, ReadableContainer):
          raise ExpressionError('Returned value is not readable')

      # clear function scope
      self.current_stack.remove_scope()
      # switch scope back to origin
      self.current_stack = origin_stack

      return returned_value

    # create container
    function_value: FunctionValue = FunctionValue(declared_function, closure)
    function_container = TransformContainer(statement.name.code, function_value)

    # save function
    self.current_stack.add_container(function_container)

    return function_container

  def execute_return_statement(self, statement: ReturnStatement):
    returned_container = self.evaluate_expression(statement.returns)
    raise ReturnException(returned_container) # will be caught by function

  def execute_import_statement(self, statement: ImportStatement, depth: int):
    # check statement depth
    if depth > 0:
      raise ExpressionError('Imports are only allowed on global level')

    # resolve dependency absolute path
    dependency_path = self.resolver.resolve_absolute_path(self.current_module.path, statement.path.code)

    # search module by ABSOLUTE path among resolved modules
    for index in range(len(self.modules)):
      if self.modules[index].path == dependency_path:
        dependency_module_index = index

        break
      
    # get dependency exports registry
    exports = self.exports[dependency_module_index]

    # load all imports
    for import_item in statement.imports:
      # check if asterisk import is used
      if is_token_of_type(import_item, MULTIPLICATION_TOKEN):
        # import everything
        for container in exports.containers:
          # check container
          if not is_container_of_type(container, ReadableContainer):
            raise ImportError(f'Symbol {import_item} is not exported by module {dependency_path}')

          # make constant container copy
          readable = ReadableContainer(container.name, container.read())
          # add constant to stack
          self.current_stack.add_container(readable)

        # do not check other imports if asterisk is in list
        break

      # resolve named import item
      container = exports.get_container_by_name(import_item.code)
      if not container:
        raise ImportError(f'Symbol {import_item} is not exported by module {dependency_path}')
      
      # make constant container copy
      readable = ReadableContainer(container.name, container.read())
      # add constant to stack
      self.current_stack.add_container(readable)

  def execute_export_statement(self, statement: ExportStatement, depth: int):
    # validate depth
    if depth > 0:
      raise ExpressionError('Exports are only allowed on global level')
    
    # execute statement
    container: ReadableContainer = self.execute_statement(statement.exports, depth)
    if not is_container_of_type(container, ReadableContainer):
      raise ExpressionError('Invalid export statement')

    # add container to exports
    self.current_exports.add_container(container)

  def execute_expression_statement(self, statement: ExpressionStatement):
    return self.evaluate_expression(statement.expression)

  # evaluate expressions
  
  # this methods delegates evaluation based on expression type
  def evaluate_expression(self, expression: Expression):
    if is_expression_of_class(expression, NullExpression):
      return self.create_readable_container(None)
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
    if is_expression_of_class(expression, AssociationExpression):
      return self.evaluate_curly_braces_expression(expression)
    
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
    key: Token = expression.right.name
    
    value_container = obj.get(key.code)

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
      return self.create_readable_container(left_value + right_value)
    
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
      return self.create_readable_container(left_value - right_value)
    
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
      return self.create_readable_container(left_value * right_value)
    
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
      
      return self.create_readable_container(left_value / right_value)
    
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
      
      return self.create_readable_container(left_value ** right_value)
    
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
      return self.create_readable_container(left_value % right_value)
    
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
    
    left_value: FunctionValue = left.read()
    if not self.is_value_of_type(left_value, FUNCTION_TYPE):
      raise ValueError(f'{left_value} is not callable')
    
    right: ReadableContainer = self.evaluate_expression(expression.right)
    if not is_container_of_type(left, ReadableContainer):
      raise ExpressionError('Right value is not readable')
    
    right_value: list[ReadableContainer] = right.read()
    if not self.is_value_of_type(right_value, TUPLE_TYPE):
      raise SyntaxError('Invalid composition')
    
    for argument in list(right_value):
      if not is_container_of_type(argument, ReadableContainer):
        raise ExpressionError('Argument is not readable')

    # execute function
    return_value: ReadableContainer = left_value.callable(*list(right_value))
    if not is_container_of_type(return_value, ReadableContainer):
      raise ExpressionError('Returned value is not readable')

    return self.create_readable_container(return_value.read())

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
        parsed_key: Token = key.name

      # handle literal keys
      elif is_expression_of_class(key, LiteralExpression):
        # validate key type
        if not self.is_value_of_type(key.value, OBJECT_KEY_TYPES):
          raise SyntaxError('Invalid key expression')
        
        parsed_key: Token = key.value
      
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

        parsed_key: Token = first_container_value
      
      # parse value
      value_container = self.evaluate_expression(value)
      if not is_container_of_type(value_container, ReadableContainer):
        raise ExpressionError('Value is not readable')
      
      # set parsed entry
      obj[parsed_key.code] = value_container

    return self.create_readable_container(obj)

  # fundamental expressions
  def evaluate_identifier_expression(self, expression: IdentifierExpression):
    return self.current_stack.get_container_by_name(expression.name.code)

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

  # builtin declarations
  def execute_builtin_declaration(self, declaration: BuiltInDeclaration):
    if is_declaration_of_type(declaration, ConstantBuiltInDeclaration):
      return self.execute_builtin_constant_declaration(declaration)
    if is_declaration_of_type(declaration, FunctionBuiltInDeclaration):
      return self.execute_builtin_function_declaration(declaration)
    
    raise ExpressionError('Builtin declaration of invalid type is executed')

  def execute_builtin_constant_declaration(self, declaration: ConstantBuiltInDeclaration):
    container = ReadableContainer(declaration.name, declaration.value)
    self.builtins.add_container(container)

  def execute_builtin_function_declaration(self, declaration: FunctionBuiltInDeclaration):
    def declared_function(*arguments):
      if len(arguments) != declaration.arguments:
        raise ValueError(f'{len(declaration.arguments)} arguments required but {len(arguments)} received')
      
      # list of unpacked values
      arguments_values = []

      for argument in arguments:
        if not is_container_of_type(argument, ReadableContainer):
          raise ExpressionError('Argument is not readable')
        
        arguments_values.append(argument.read())

      # execute builtin function are return value in container
      return self.create_readable_container(declaration.callable(*arguments_values))

    function_value = FunctionValue(declared_function, None)
    function_container = ReadableContainer(declaration.name, function_value)

    self.builtins.add_container(function_container)

  # creates anonymous readable containers for expression evaluations
  def create_readable_container(self, value):
    return ReadableContainer('', value)
  
  # check data types of values
  def is_value_of_type(self, value, *types: str):
    return get_value_type(value) in types
  