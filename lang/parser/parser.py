from parser.types.statements import *
from parser.types.expressions import *
from parser.exceptions import *
from parser.constants import *
from parser.operators import *
from parser.tokens import *

from lexer.token import Token

from shared.tokens import *
from shared.keywords import *

# class that parses token list to AST
# AST is built with Statements and Expressions
class Parser:
  def __init__(self):
    # list of tokens that are in use to build AST
    self.tokens: list[Token] = []
    # list position
    self.position = 0

  # parses token list to AST
  # entry point
  def parse(self, tokens: list[Token]):
    # load tokens
    self.load_tokens(tokens)

    # init statements
    statements = []

    # parse module 
    while not self.is_end():
      statements.append(self.parse_statement())

    # return block of statements
    return BlockStatement(statements)

  # list of methods to match different statements
  # routes to other parse methods
  def parse_statement(self, *terminators: Token):
    # skip space symbols
    self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

    if self.match_comment():
      return self.parse_comment()
    if self.match_variable_declaration():
      return self.parse_variable_declaration(*terminators)
    if self.match_constant_declaration():
      return self.parse_constant_declaration(*terminators)
    if self.match_condition_statement():
      return self.parse_condition_statement(*terminators)
    if self.match_for_statement():
      return self.parse_for_statement(*terminators)
    if self.match_while_statement():
      return self.parse_while_statement(*terminators)
    if self.match_function_declaration_statement():
      return self.parse_function_declaration_statement()
    if self.match_return_statement():
      return self.parse_return_statement()
    if self.match_import_statement():
      return self.parse_import_statement()
    if self.match_export_statement():
      return self.parse_export_statement(*terminators)
    if self.match_block_statement():
      return self.parse_block_statement()
    
    # by default, parse as expression
    return self.parse_expression_statement(*terminators)

  # Methods to require standalone statements
  # Require tokens. Check before

  def parse_variable_declaration(self, *terminators: Token):
    # require VAR keyword
    self.require_token(map_keyword_to_token(VAR_KEYWORD))
    self.consume_current_token()

    self.skip_tokens(SPACE_TOKEN)

    # get VAR name
    self.require_token(IDENTIFIER_TOKEN)
    identifier = self.consume_current_token()

    self.skip_tokens(SPACE_TOKEN)

    # if no assignment on this line - return uninitialized
    if self.match_token(NEWLINE_TOKEN):
      return VariableDeclarationStatement(identifier, NullExpression())
    
    # if ASSIGN is present - parse expression
    if self.match_token(ASSIGN_TOKEN):
      # consume assign token
      self.consume_current_token()

      self.skip_tokens(SPACE_TOKEN)

      expression = self.parse_expression(None, BASE_PRECEDENCE, NEWLINE_TOKEN, *terminators)
      if is_expression_of_class(expression, NullExpression):
        raise ParserError(self.get_current_token_position(), f'Variable {identifier} has invalid initialization')
      
      return VariableDeclarationStatement(identifier, expression)
    
    # if other symbol - raise error
    raise ParserError(self.get_current_token_position(), 'Invalid variable declaration')
  def parse_constant_declaration(self, *terminators: Token):
     # require CONST keyword
    self.require_token(map_keyword_to_token(CONST_KEYWORD))
    self.consume_current_token()

    self.skip_tokens(SPACE_TOKEN)

    # get CONST name
    self.require_token(IDENTIFIER_TOKEN)
    identifier = self.consume_current_token()

    self.skip_tokens(SPACE_TOKEN)

    # require ASSIGNMENT
    if not self.match_token(ASSIGN_TOKEN):
      raise ParserError(self.get_current_token_position(), 'Constant declaration without initialization')
    
    # consume ASSIGNMENT
    self.require_token(ASSIGN_TOKEN)
    self.consume_current_token()

    self.skip_tokens(SPACE_TOKEN)

    initialization = self.parse_expression(None, BASE_PRECEDENCE, NEWLINE_TOKEN, *terminators)
    if is_expression_of_class(initialization, NullExpression):
      raise ParserError(self.get_current_token_position(), f'Constant {identifier} has invalid initialization')

    return ConstantDeclarationStatement(identifier, initialization)
  def parse_condition_statement(self, *terminators: Token):
    # start with IF keyword
    self.require_token(map_keyword_to_token(IF_KEYWORD))
    self.consume_current_token()

    # skip space tokens
    # new line is not allowed here!
    self.skip_tokens(SPACE_TOKEN)

    # require parentheses
    self.require_token(LEFT_PARENTHESES_TOKEN)
    self.consume_current_token()

    # parse parentheses expression
    condition = self.parse_expression(None, BASE_PRECEDENCE, RIGHT_PARENTHESES_TOKEN)

    if is_expression_of_class(condition, NullExpression):
      raise ParserError(self.get_current_token_position(), 'Condition statement has invalid expression in parentheses')

    self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

    # require close parentheses
    self.require_token(RIGHT_PARENTHESES_TOKEN)
    self.consume_current_token()

    self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

    # get THEN statement
    then_branch = self.parse_statement(*terminators)

    self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

    # init ELSE statement
    else_branch = ExpressionStatement(NullExpression())

    # init ELSE statement
    if self.match_token(map_keyword_to_token(ELSE_KEYWORD)):
      # consume else keyword
      self.consume_current_token()

      self.skip_tokens(SPACE_TOKEN)

      # get ELSE statement
      else_branch = self.parse_statement(*terminators)

    # require newline
    self.require_newline_for_next_statements()

    # return condition statement
    return ConditionStatement(condition, then_branch, else_branch)
  def parse_for_statement(self, *terminators: Token):
    # get FOR keyword
    self.require_token(map_keyword_to_token(FOR_KEYWORD))
    self.consume_current_token()

    # newlines are not allowed
    self.skip_tokens(SPACE_TOKEN)

    # require parentheses
    self.require_token(LEFT_PARENTHESES_TOKEN)
    self.consume_current_token()

    # skip spaces and newlines
    self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

    # get initialization statement
    initialization = self.parse_statement(RIGHT_PARENTHESES_TOKEN, SEMICOLON_TOKEN)

    # consume semicolon
    self.require_token(SEMICOLON_TOKEN)
    self.consume_current_token()

    # skip spaces and newlines
    self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

    # get condition expression
    condition = self.parse_expression(None, BASE_PRECEDENCE, RIGHT_PARENTHESES_TOKEN, SEMICOLON_TOKEN)

    # consume semicolon
    self.require_token(SEMICOLON_TOKEN)
    self.consume_current_token()

    # skip spaces and newlines
    self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

    # get increment expression
    increment = self.parse_expression(None, BASE_PRECEDENCE, RIGHT_PARENTHESES_TOKEN, SEMICOLON_TOKEN)

    # skip spaces
    self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

    # consume right parentheses
    self.require_token(RIGHT_PARENTHESES_TOKEN)
    self.consume_current_token()

    # skip spaces and newlines
    self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

    # get loop body
    body = self.parse_statement(*terminators)

    # require newline
    self.require_newline_for_next_statements()

    return ForStatement(initialization, condition, increment, body)
  def parse_while_statement(self, *terminators: Token):
    # start with WHILE keyword
    self.require_token(map_keyword_to_token(WHILE_KEYWORD))
    self.consume_current_token()

    # skip space tokens
    # new line is not allowed here!
    self.skip_tokens(SPACE_TOKEN)

    # require parentheses
    self.require_token(LEFT_PARENTHESES_TOKEN)
    self.consume_current_token()

    # parse parentheses expression
    while not self.is_end() and not self.match_token(RIGHT_PARENTHESES_TOKEN):
      condition = self.parse_expression(None, BASE_PRECEDENCE, RIGHT_PARENTHESES_TOKEN)

    self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

    # require close parentheses
    self.require_token(RIGHT_PARENTHESES_TOKEN)
    self.consume_current_token()

    self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

    # get body statement
    body = self.parse_statement(*terminators)

    # require newline
    self.require_newline_for_next_statements()

    return WhileStatement(condition, body)
  def parse_break_statement(self):
    # require break keyword
    self.require_token(map_keyword_to_token(BREAK_KEYWORD))
    self.consume_current_token()

    # require newline
    self.require_newline_for_next_statements()

    return BreakStatement()
  def parse_continue_statement(self):
    # require continue keyword
    self.require_token(map_keyword_to_token(CONTINUE_KEYWORD))
    self.consume_current_token()

    # require newline
    self.require_newline_for_next_statements()

    return ContinueStatement()
  def parse_function_declaration_statement(self):
    # start with function keyword
    self.require_token(map_keyword_to_token(FUNCTION_KEYWORD))
    self.consume_current_token()

    # skip space tokens
    # new line is not allowed here!
    self.skip_tokens(SPACE_TOKEN)

    # get name
    self.require_token(IDENTIFIER_TOKEN)
    name = self.consume_current_token()

    # require parentheses
    self.require_token(LEFT_PARENTHESES_TOKEN)
    self.consume_current_token()

    # get parameters
    parameters: list[FunctionParameterExpression] = []

    # parse parentheses expression
    while not self.is_end() and not self.match_token(RIGHT_PARENTHESES_TOKEN):
      if (len(parameters)):
        self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

        self.require_token(COMMA_TOKEN)
        self.consume_current_token()

        self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

      parameter = self.parse_function_parameter_expression()
      parameters.append(parameter)

      # skip spaces
      self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

    # skip spaces
    self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

    # require close parentheses
    self.require_token(RIGHT_PARENTHESES_TOKEN)
    self.consume_current_token()

    self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

    # get body statement
    body = self.parse_block_statement()

    # require newline
    self.require_newline_for_next_statements()

    return FunctionDeclarationStatement(name, parameters, body)
  def parse_function_parameter_expression(self):
    self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

    # consume parameter name
    self.require_token(IDENTIFIER_TOKEN)
    parameter = self.consume_current_token()

    self.skip_tokens(SPACE_TOKEN)

    # init default value
    defaultValue = None

    # handle default value
    if self.match_token(ASSIGN_TOKEN):
      self.consume_current_token()
      self.skip_tokens(SPACE_TOKEN)

      # parse expression until comma or closing parentheses
      defaultValue = self.parse_expression(None, BASE_PRECEDENCE, COMMA_TOKEN, RIGHT_PARENTHESES_TOKEN)
    
    return FunctionParameterExpression(parameter, defaultValue)
  def parse_return_statement(self, *terminators: Token):
    # require return
    self.require_token(map_keyword_to_token(RETURN_KEYWORD))
    self.consume_current_token()

    self.skip_tokens(SPACE_TOKEN)

    # compose return statement
    expression = self.parse_expression(None, BASE_PRECEDENCE, NEWLINE_TOKEN, *terminators)

    return ReturnStatement(expression)
  def parse_class_declaration_statement(self):
    pass
  def parse_import_statement(self):
    # get IMPORT token
    self.require_token(map_keyword_to_token(IMPORT_KEYWORD))
    self.consume_current_token()

    # skip spaces
    self.skip_tokens(SPACE_TOKEN)

    # initialize imports
    imports: list[Token] = []

    # parse curly brace imports
    if self.match_token(LEFT_CURLY_BRACE_TOKEN):
      # consume curly brace
      self.consume_current_token()

      # skip tokens
      self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

      while not self.match_token(RIGHT_CURLY_BRACE_TOKEN):
        # require comma separator
        if (len(imports)):
          self.require_token(COMMA_TOKEN)
          self.consume_current_token()

        self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN) 

        # allow trailing comma
        if self.match_token(RIGHT_CURLY_BRACE_TOKEN):
          break

        # expect named import in curly braces
        self.require_token(IDENTIFIER_TOKEN)
        
        # get named import
        import_item = self.consume_current_token()

        # append named import
        imports.append(import_item)

        self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

      # consume closing curly brace
      self.require_token(RIGHT_CURLY_BRACE_TOKEN)
      self.consume_current_token()

    # parse asterisk (*) import
    elif self.match_token(MULTIPLICATION_TOKEN):
      asterisk = self.consume_current_token()
      imports.append(asterisk)

    # skip spaces
    self.skip_tokens(SPACE_TOKEN)

    # get FROM keyword
    self.require_token(map_keyword_to_token(FROM_KEYWORD))
    self.consume_current_token()

    self.skip_tokens(SPACE_TOKEN)

    # parse path
    self.require_token(STRING_TOKEN)
    path = self.consume_current_token()

    # require newline
    self.require_newline_for_next_statements()

    # return import statement
    return ImportStatement(path, imports)
  def parse_export_statement(self, *terminators: Token):
    # require EXPORT keyword
    self.require_token(map_keyword_to_token(EXPORT_KEYWORD))
    self.consume_current_token()

    self.skip_tokens(SPACE_TOKEN)

    # get export statement
    exports = self.parse_statement(NEWLINE_TOKEN, *terminators)

    # allowed exports
    allowed_exports = [
      ConstantDeclarationStatement,
      FunctionDeclarationStatement,
      ClassDeclarationStatement,
    ]

    # validate export statement
    if not is_statement_of_class(exports, *allowed_exports):
      raise ParserError(self.get_current_token_position(), 'Invalid export statement')
    
    return ExportStatement(exports)
  def parse_block_statement(self):
    # get left curly brace
    self.require_token(LEFT_CURLY_BRACE_TOKEN)
    self.consume_current_token()

    # init list of nested statements
    statements: list[Statement] = []

    # iterate for nested statements
    # stop if end is reached
    while not self.is_end():
      # check if end is not reached
      if self.match_token(RIGHT_CURLY_BRACE_TOKEN):
        # pass closing token
        self.consume_current_token()

        return BlockStatement(statements)
      
      # add new statement
      statements.append(self.parse_statement(RIGHT_CURLY_BRACE_TOKEN))

    raise ParserError(self.get_current_token_position(), f'Expected token {RIGHT_CURLY_BRACE_TOKEN}')
  def parse_expression_statement(self, *terminators: Token):
    expression = self.parse_expression(None, BASE_PRECEDENCE, NEWLINE_TOKEN, *terminators)

    return ExpressionStatement(expression)
  def parse_comment(self):
    # require comment
    self.require_token(COMMENT_TOKEN)

    # consume tokens until NEWLINE is not found
    while not self.is_end():
      # consume token
      self.consume_current_token()

      # if next one is NEWLINE - stop
      if self.match_token(NEWLINE_TOKEN):
        break

    # consume NEWLINE
    self.consume_current_token()
    
    return ExpressionStatement(NullExpression())

  # reusable utilities

  def require_newline_for_next_statements(self):
    self.skip_tokens(SPACE_TOKEN)

    if self.is_end():
      return
    
    self.require_token(NEWLINE_TOKEN)
    self.consume_current_token()

  # Methods to check statements (without requiring)
  # check if current statement is of type

  def match_variable_declaration(self):
    return self.match_token(map_keyword_to_token(VAR_KEYWORD))
  def match_constant_declaration(self):
    return self.match_token(map_keyword_to_token(CONST_KEYWORD))
  def match_condition_statement(self):
    return self.match_token(map_keyword_to_token(IF_KEYWORD))
  def match_for_statement(self):
    return self.match_token(map_keyword_to_token(FOR_KEYWORD))
  def match_while_statement(self):
    return self.match_token(map_keyword_to_token(WHILE_KEYWORD))
  def match_break_statement(self):
    return self.match_token(map_keyword_to_token(BREAK_KEYWORD))
  def match_continue_statement(self):
    return self.match_token(map_keyword_to_token(CONTINUE_KEYWORD))
  def match_function_declaration_statement(self):
    return self.match_token(map_keyword_to_token(FUNCTION_KEYWORD))
  def match_return_statement(self):
    return self.match_token(map_keyword_to_token(RETURN_KEYWORD))
  def match_class_declaration_statement(self):
    return self.match_token(map_keyword_to_token(CLASS_KEYWORD))
  def match_import_statement(self):
    return self.match_token(map_keyword_to_token(IMPORT_KEYWORD))
  def match_export_statement(self):
    return self.match_token(map_keyword_to_token(EXPORT_KEYWORD))
  def match_block_statement(self):
    return self.match_token(LEFT_CURLY_BRACE_TOKEN)
  def match_comment(self):
    return self.match_token(COMMENT_TOKEN)

  # Methods to parse expressions

  # parses expression node
  # base_expression is used to continue parsing after UNARY operations and GROUPINGS
  # base_precedence specifies the precedence of previous expression to form a hierarchy
  # specify tokens after which search stops
  # composes AST and bases on parse_expression_from_tokens method
  def parse_expression(
    self, 
    base_expression: Expression | None, # contains node of currently parsing expression
    base_precedence: int, # contains precedence of previous operator to handle hierarchy
    *terminators: list[Token] # list of tokens that end expression if it is ready
  ):
    # handle if base expression is finished
    if base_expression:
      # skip only spaces
      self.skip_tokens(SPACE_TOKEN)

      # if new line or terminator - finish
      if self.is_end() or self.match_token(NEWLINE_TOKEN, *terminators):
        return base_expression
    
    # skip spaces and newlines (expressions can take several lines if needed)
    self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

    # init node tokens
    passed_tokens: list[Token] = []
    
    # go until operators
    while not self.is_end() and not self.match_token(*OPERATOR_TOKENS):
      # if base_expression is followed by non-operator tokens - error in composition
      if base_expression:
        print(base_expression, self.get_current_token())
        raise ParserError(self.get_current_token_position(), 'Invalid expression')
      
      # check if terminators or end of module are not reached
      # when reach terminator or end of module, finish expression parsing
      if self.match_token(*terminators) or self.is_end():
        return self.parse_expression_from_tokens(passed_tokens)
      
      # append tokens to list
      passed_tokens.append(self.consume_current_token())

      # skip spaces again
      self.skip_tokens(SPACE_TOKEN)

    # stop if end or terminator is reached
    if self.is_end() or self.match_token(*terminators):
      return self.parse_expression_from_tokens(passed_tokens)

    # get found operator. Consume and move position
    operator = self.consume_current_token()
    precedence = get_operator_precedence(operator)

    # handle unary operations
    if is_unary_operator(operator):
      # handle case if current operator has higher precedence
      # higher precedence - work with this expression
      if base_precedence <= precedence:
        # if passed_tokens are present - suffix operator
        if base_expression or len(passed_tokens):
          # if there are tokens - suffix operator
          if not is_suffix_unary_operator(operator) and not is_affix_unary_operator(operator):
            raise ParserError(self.get_current_token_position(), 'Prefix operator is used in suffix form')
        
          # if operand is base_expression
          operand = base_expression
          # if operand is made of passed tokens
          if len(passed_tokens):
            operand = self.parse_expression_from_tokens(passed_tokens)

          # validate operand
          if is_expression_of_class(operand, NullExpression):
            raise ParserError(self.get_current_token_position(), f'Unary operator {operator.code} requires operand')
          
          # compose expression
          expression = SuffixUnaryOperationExpression(operator, operand)
          
          # pass this expression for further parsing
          return self.parse_expression(expression, precedence, *terminators)

        # if no tokens and no base expression - prefix operator
        # validate operator
        if not is_prefix_unary_operator(operator) and not is_affix_unary_operator(operator):
          raise ParserError(self.get_current_token_position(), 'Suffix operator is used in prefix form')
        
        # no base expression because no tokens, started with operator
        operand = self.parse_expression(None, precedence, *terminators)
        
        # validate operand
        if is_expression_of_class(operand, NullExpression):
          raise ParserError(self.get_current_token_position(), f'Unary operator {operator.code} requires operand')

        expression = PrefixUnaryOperationExpression(operator, operand)

        # use this expression as base and continue parsing
        return self.parse_expression(expression, precedence, *terminators)
      
      # if this operator has smaller precedence:
      # finish previous expression and analyse operator after
      
      # to "give operator back"
      self.decrement_position()

      # parse based on base_expression
      if base_expression: 
        return self.parse_expression(base_expression, BASE_PRECEDENCE, *terminators)
      
      # finish previous expression with passed tokens
      return self.parse_expression_from_tokens(passed_tokens)

    # handle binary operations
    if is_binary_operator(operator):
      # if found operation precedence is smaller than or equal to, current tokens is its left branch
      if base_precedence < precedence:
        # if left_branch is base_expression
        left_branch = base_expression
        # override with passed tokens if needed
        if len(passed_tokens):
          left_branch = self.parse_expression_from_tokens(passed_tokens)

        # validate operand
        if is_expression_of_class(left_branch, NullExpression):
          raise ParserError(self.get_current_token_position(), f'Binary operator {operator.code} requires left operand')

        right_branch = self.parse_expression(None, precedence, *terminators)

        # validate operand
        if is_expression_of_class(right_branch, NullExpression):
          raise ParserError(self.get_current_token_position(), f'Binary operator {operator.code} requires right operand')
        
        # compose expression
        expression = BinaryOperationExpression(operator, left_branch, right_branch)

        # use this expression as base one
        return self.parse_expression(expression, precedence, *terminators)
      
      # if found operation precedence is higher:
      # finish previous expression first
      
      # to "give operator back"
      self.decrement_position()

      # parse based on base_expression 
      if base_expression: 
        return self.parse_expression(base_expression, BASE_PRECEDENCE, *terminators)
      
      # finish previous expression with passed tokens
      return self.parse_expression_from_tokens(passed_tokens)
    
    # handle grouping operations
    if is_grouping_operator(operator):
      # remember position before parsing group
      position_before_grouping_operator = self.position - 1
      
      # get closing token - terminator
      closing_operator = get_grouping_operator_closing_token(operator)
      # add new terminators
      grouping_terminators = [*terminators, COMMA_TOKEN, closing_operator]

      # start list of grouped expressions
      expressions: list[Expression] = []

      # parse expressions until reach closing operator
      while not self.match_token(closing_operator):
        # require comma separator
        if len(expressions):
          self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

          self.require_token(COMMA_TOKEN)
          self.consume_current_token()

          self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

          if self.match_token(closing_operator):
            self.consume_current_token()
            break

        # add found expression
        expressions.append(self.parse_expression(None, BASE_PRECEDENCE, *grouping_terminators))

        self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

      # validate expressions
      if len(expressions):
        # do not check last expression (trailing commas are allowed)
        for i in range(len(expressions) - 1):
          if is_expression_of_class(expressions[i], NullExpression):
            raise ParserError(self.get_current_token_position(), 'Incorrect expression in group')
          
        # remove last NullExpression (trailing comma case)
        if is_expression_of_class(expressions[-1], NullExpression):
          expressions.pop()

      # consume closing token
      self.consume_current_token()

      # compose grouping expression
      grouping_expression = GroupingExpression(operator, expressions)

      # if grouping precedence is higher, return grouping or grouping application
      if base_precedence < precedence:
        # if no previously passed tokens or base_expression - return expression
        if not base_expression and not len(passed_tokens):
          return grouping_expression

        # use base expression as left by default
        left = base_expression
        # if previous tokens are present - compute expression
        if len(passed_tokens):
          left = self.parse_expression_from_tokens(passed_tokens)

        # validate left expression
        if is_expression_of_class(left, NullExpression):
          return self.parse_expression(grouping_expression, BASE_PRECEDENCE, *terminators)
        
        # compose expression
        expression = GroupingApplicationExpression(left, grouping_expression)
        
        # use expression as base for further parsing 
        return self.parse_expression(expression, precedence, *terminators)
      
      # if found operation precedence is higher:
      # finish previous expression first
      
      # to "give operator back"
      self.position = position_before_grouping_operator

      # continue parsing operations with base_expression
      if base_expression: 
        return self.parse_expression(base_expression, BASE_PRECEDENCE, *terminators)
      
      # finish previous expression with passed tokens
      return self.parse_expression_from_tokens(passed_tokens)

    # handle association operations
    if is_association_operator(operator):
      # initialize entries
      entries: list[tuple[Expression, Expression]] = []

      while not self.match_token(RIGHT_CURLY_BRACE_TOKEN):
        # require comma separator
        if len(entries):
          self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

          self.require_token(COMMA_TOKEN)
          self.consume_current_token()
          
        self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

        if self.match_token(RIGHT_CURLY_BRACE_TOKEN):
          self.consume_current_token()
          break

        # parse key expression
        # search until association closing or colon
        key_expression = self.parse_expression(None, BASE_PRECEDENCE, RIGHT_CURLY_BRACE_TOKEN, COLON_TOKEN)

        if is_expression_of_class(key_expression, NullExpression):
          raise ParserError(self.get_current_token_position(), 'Invalid key expression')

        # require and consume colon
        self.require_token(COLON_TOKEN)
        self.consume_current_token()

        # parse value expression
        # search until association closing or comma
        value_expression = self.parse_expression(None, BASE_PRECEDENCE, RIGHT_CURLY_BRACE_TOKEN, COMMA_TOKEN)

        if is_expression_of_class(value_expression, NullExpression):
          raise ParserError(self.get_current_token_position(), 'Invalid value expression')

        # append entry
        entries.append((key_expression, value_expression))

        self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

      # validate expressions
      if len(entries):
        # do not check last expression (trailing commas are allowed)
        for i in range(len(entries) - 1):
          if is_expression_of_class(entries[i], NullExpression):
            raise ParserError(self.get_current_token_position(), 'Incorrect expression in group')
          
        # remove last NullExpression (trailing comma case)
        if is_expression_of_class(entries[-1], NullExpression):
          entries.pop()
      
      # compose association
      expression = AssociationExpression(entries)

      # continue parsing
      return self.parse_expression(expression, precedence, *terminators)

  # parses expression from limited set of tokens
  def parse_expression_from_tokens(self, tokens: list[Token]):
    if not len(tokens):
      return NullExpression()

    if self.match_literal_expression(tokens):
      return LiteralExpression(tokens[0])
    if self.match_identifier_expression(tokens):
      return IdentifierExpression(tokens[0])
    
    for token in tokens:
      print(token)
    
    raise ParserError(self.get_current_token_position(), f'Invalid expression starting with token: {tokens[0]}')
    
  def match_literal_expression(self, tokens: list[Token]):
    return len(tokens) == LITERAL_TOKENS_LENGTH and is_literal_token(tokens[0])
  def match_identifier_expression(self, tokens: list[Token]):
    return len(tokens) == IDENTIFIER_TOKENS_LENGTH and is_token_of_type(tokens[0], IDENTIFIER_TOKEN)

  # Low level methods to parse tokens

  # asserts current token. Raises error
  # receives tokens
  def require_token(self, token):
    current = self.get_current_token()

    # validate token type
    if not self.match_token(token):
      raise ParserError(self.get_current_token_position(), f'Expected token {token}. Received {current}')
    
  # checks current token. Returns bool
  # receives tokens
  def match_token(self, *tokens):
    # handle end of module case
    if self.is_end():
      return False

    # receive current token
    current = self.get_current_token()

    for token in tokens:
      if is_token_of_type(current, token): 
        return True

    return False
  
  # to skip spaces until gets meaningful token
  def skip_tokens(self, *tokens: Token):
    # while current token is in tokens list
    while self.match_token(*tokens):
      # move position forward
      self.increment_position()

      # stop if end is reached
      if self.is_end():
        return

  # Methods to iterate through tokens list

  # consumes current token
  # returns current token
  # moves position forward 
  def consume_current_token(self):
    self.increment_position()
    return self.get_previous_token()
  
  # returns current token
  def get_current_token(self):
    return self.tokens[self.position]
  
  # returns previous token
  def get_previous_token(self):
    return self.tokens[self.position - 1]

  # get position
  def get_current_token_position(self):
    return self.get_current_token().position
  
  # moves position forward
  def increment_position(self):
    self.position += 1 

  # moves position backwards
  def decrement_position(self):
    self.position -= 1 

  # indicates end of token list
  def is_end(self):
    return self.position >= len(self.tokens)

  # Helper methods to handle data attributes

  # loader
  def load_tokens(self, tokens: list[Token]):
    self.tokens = tokens
    self.position = 0
