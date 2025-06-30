from lexer.exceptions import LexerError
from lexer.token import *
from shared.tokens import *
from shared.keywords import *
from shared.position import *

# standard modules
import re

# class that parses code to tokens
class Lexer:
  def __init__(self):
    # input
    self.code = ""
    self.position = 0

    # output
    self.tokens: list[Token] = []

  # for code loading 
  # resets position and tokens
  def load_code(self, code):
    self.code = code
    self.position = 0
    self.tokens = []

  # for moving pointer by delta
  def move_position_by_delta(self, delta):
    self.position += delta

  # parses code (module) to tokens
  def parse(self, code: str):
    self.load_code(code)

    # iterate through code
    while self.position < len(self.code):
      # flag that indicates if token found for current position
      current_position_match = False

      # check every token from specification
      for type, regex in TOKEN_SPECIFICATION:
        # check if token is matched
        match = re.search(f"^{regex}", self.code[self.position:])
      
        if match:
          # get whole match value
          token = match.group()
          
          # move position
          self.move_position_by_delta(len(token))

          # handle extracting part of token for .code field
          # used to extract string content from string literal
          if match.groups():
            for group in match.groups():
              if group:
                token = group
                break

          # handle keywords
          if type == IDENTIFIER_TOKEN[0] and token in KEYWORDS:
            # type is a keyword itself
            type = token

          # escape special symbols in token
          token = token.encode("utf-8").decode("unicode_escape")

          # add token
          position = self.compute_current_token_position()
          self.tokens.append(Token(position, type, token))

          # update flag to set current position matched
          current_position_match = True
          
          # continue with new token
          break
        
      if not current_position_match:
        raise LexerError(self.compute_current_token_position(), 'Invalid token found')

    # return list of found tokens      
    return self.tokens.copy()
  
  # method that computes token position based on current pont position pointer
  def compute_current_token_position(self):
    lines = self.code[0:self.position].split('\n')
    
    # rows are counted from 1
    row = len(lines)
    # columns are counted from 1 and target position next to pointer
    column = len(lines[-1]) + 1

    return TokenPosition(row, column)
