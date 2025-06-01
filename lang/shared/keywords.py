# constants and variables
VAR_KEYWORD = 'var'
CONST_KEYWORD = 'const'

# conditions
IF_KEYWORD = 'if'
# else branch of condition
ELSE_KEYWORD = 'else'

# loops
FOR_KEYWORD = 'for'
# for while loops
WHILE_KEYWORD = 'while'
# to finish current loop iteration 
CONTINUE_KEYWORD = 'continue'
# to finish loop
BREAK_KEYWORD = 'break'

# to declare function
FUNCTION_KEYWORD = 'function'
# returns value of string
RETURN_KEYWORD = 'return'

# for importing modules
IMPORT_KEYWORD = 'import'
# supports imports
FROM_KEYWORD = 'from'
# for exporting modules
EXPORT_KEYWORD = 'export'

# for classes
NEW_KEYWORD = 'new'

# list of keywords used in language
KEYWORDS = [
  VAR_KEYWORD,
  CONST_KEYWORD,
  
  IF_KEYWORD,
  ELSE_KEYWORD,
  
  FOR_KEYWORD,
  WHILE_KEYWORD,
  CONTINUE_KEYWORD,
  BREAK_KEYWORD,
  
  FUNCTION_KEYWORD,
  RETURN_KEYWORD,

  IMPORT_KEYWORD,
  FROM_KEYWORD,
  EXPORT_KEYWORD,

  NEW_KEYWORD,
]

# map keyword to token tuple
def map_keyword_to_token(keyword: str):
  # tokens are tuples (name, regex)
  return (keyword, keyword)

