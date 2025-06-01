from parser.types.statements import *
from parser.types.expressions import *
from parser.exceptions import *
from parser.operators import *
from parser.tokens import *

from lexer.token import Token

from shared.tokens import *
from shared.keywords import *

# class that parses token list to AST
class Parser:
  def __init__(self):
    # contains parsed AST
    self.root = BlockStatement()
    
    # list of tokens that are in use to build AST
    self.tokens: list[Token] = []
    # list position
    self.position = 0

  # parses token list to AST
  # entry point
  def parse(self, tokens: list[Token]):
    # reset root AST
    self.reset_root()
    # load tokens
    self.load_tokens(tokens)

  # list of methods to match different statements
  # routes to other parse methods
  def parse_statement(self):
    if self.match_condition_statement():
      return self.parse_comment()
    if self.match_block_statement():
      return self.parse_block_statement()

  # Methods to require standalone statements
  # Require tokens. Check before

  def parse_condition_statement(self):
    pass
  def parse_for_statement(self):
    pass
  def parse_while_statement(self):
    pass
  def parse_function_declaration_statement(self):
    pass
  def parse_class_declaration_statement(self):
    pass
  def parse_block_statement(self):
    # get left curly brace
    self.require_token(LEFT_CURLY_BRACE_TOKEN)
    # init list of nested statements
    statements: list[Statement] = []

    # iterate for nested statements
    # stop if end is reached
    while not self.is_end():
      # check if end is not reached
      if self.match_token(RIGHT_CURLY_BRACE_TOKEN):
        return BlockStatement(statements)
      
      # add new statement
      statements.append(self.parse_statement())
      
    raise ParserError(f'Expected token {RIGHT_CURLY_BRACE_TOKEN}')
  def parse_comment(self):
    # require comment
    self.require_token(COMMENT_TOKEN)

    # skip symbols and stop after consuming new line
    while not self.is_end():
      if self.consume_current_token() == NEWLINE_TOKEN:
        break

  # Methods to check statements (without requiring)
  # check if current statement is of type

  def match_condition_statement(self):
    return self.match_token(map_keyword_to_token(IF_KEYWORD))
  def match_for_statement(self):
    return self.match_token(map_keyword_to_token(FOR_KEYWORD))
  def match_while_statement(self):
    return self.match_token(map_keyword_to_token(WHILE_KEYWORD))
  def match_function_declaration_statement(self):
    return self.match_token(map_keyword_to_token(FUNCTION_KEYWORD))
  def match_class_declaration_statement(self):
    return self.match_token(map_keyword_to_token(CLASS_KEYWORD))
  def match_block_statement(self):
    return self.match_token(LEFT_CURLY_BRACE_TOKEN)
  def match_comment(self):
    return self.match_token(COMMENT_TOKEN)

  # Methods to parse expressions

  # parses expression node
  # base_precedence specifies the precedence of previous expression to form a hierarchy
  # specify tokens after which search stops
  # composes AST and bases on parse_expression_from_tokens method
  def parse_expression(self, base_precedence: int, *terminators: list[Token]):
    # skip space symbols
    self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

    # init node tokens
    passed_tokens: list[Token] = []

    # go until operators
    while not self.is_end() and not self.match_token(*OPERATOR_TOKENS):
      # append tokens to branch
      passed_tokens.append(self.consume_current_token())

      # check if terminators are not reached
      if self.match_token(*terminators):
        return self.parse_expression_from_tokens(passed_tokens)

    # get found operator. Consume and move position
    operator = self.consume_current_token()
    precedence = get_operator_precedence(operator)

    # handle unary operations
    # TODO: handle prefix and suffix forms
    if is_unary_operator(operator):
      # handle case if current operator has higher precedence
      if base_precedence <= precedence:
        # if no tokens - prefix operator
        if not len(passed_tokens):
          operand = self.parse_expression(precedence, *terminators)
          return UnaryOperationExpression(operator, operand)
        
        # if tokens are present - suffix operator
        operand = self.parse_expression_from_tokens(passed_tokens)
        return UnaryOperationExpression(operator, operand)
      
      # if this operator has smaller precedence, finish previous expression and analyse operator after
      self.decrement_position() # to "give operator back"
      # finish previous expression
      return self.parse_expression_from_tokens(passed_tokens)

    # handle binary operations
    if is_binary_operator(operator):
      # if found operation precedence is smaller than or equal to, current tokens is its left branch
      if base_precedence <= precedence:
        left_branch = self.parse_expression_from_tokens(passed_tokens)
        right_branch = self.parse_expression(precedence, *terminators)
        return BinaryOperationExpression(operator, left_branch, right_branch)
      
      # if found operation precedence is higher - finish previous expression first
      self.decrement_position() # to "give operator back"
      # finish previous expression
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
        # add found expression
        expressions.append(self.parse_expression(BASE_PRECEDENCE, grouping_terminators))

      # compose grouping expression
      grouping_expression = GroupingExpression(operator, expressions)

      # if grouping precedence is higher, return grouping or grouping application
      if base_precedence <= precedence:
        # if no previously passed tokens - return expression
        if not len(passed_tokens):
          return grouping_expression

        # if previous tokens are present - compute expression
        left = self.parse_expression_from_tokens(passed_tokens)
        return GroupingApplicationExpression(left, grouping_expression)
      
      # handle case when previous operation had higher precedence
      # return back all passed tokens for grouping. Parse them after
      self.position = position_before_grouping_operator
      # finish previous expression
      return self.parse_expression_from_tokens(passed_tokens)

  # parses expression from limited set of tokens
  def parse_expression_from_tokens(self, tokens: list[Token]):
    if self.match_literal_expression(tokens):
      return LiteralExpression(tokens[0])
    if self.match_identifier_expression(tokens):
      return IdentifierExpression(tokens[0])
    
  def match_literal_expression(self, tokens: list[Token]):
    return len(tokens) == 1 and tokens[0] in LITERAL_TOKENS
  def match_identifier_expression(self, tokens: list[Token]):
    return len(tokens) == 1 and tokens[0].type == IDENTIFIER_TOKEN[0] 

  # Low level methods to parse tokens

  # asserts current token. Raises error
  # receives tokens
  def require_token(self, token):
    # skip spaces
    self.skip_tokens(SPACE_TOKEN, NEWLINE_TOKEN)

    # validate token type
    if not self.match_token(token):
      raise ParserError(f'Expected token {token}')
    
  # checks current token. Returns bool
  # receives tokens
  def match_token(self, *tokens):
    for token in tokens:
      current = self.get_current_token()
      if current.type == token[0]: return True

    return False
  
  # to skip spaces until gets meaningful token
  def skip_tokens(self, *tokens: list[Token]):
    # while current token is of type SPACE_TOKEN
    while self.match_token(*tokens):
      # move position forward
      self.increment_position()

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

  # moves position forward
  def increment_position(self):
    self.position += 1 

  # moves position backwards
  def decrement_position(self):
    self.position -= 1 

  # indicates end of token list
  def is_end(self):
    return self.position > len(self.tokens)

  # Helper methods to handle data attributes

  # loader
  def load_tokens(self, tokens: list[Token]):
    self.tokens = tokens
    self.position = 0

  # resetter
  def reset_root(self):
    self.root = BlockStatement()
