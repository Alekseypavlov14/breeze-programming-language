# indicates position of first token symbol
class TokenPosition:
  def __init__(self, row: int, column: int):
    self.row = row
    self.column = column

  def __str__(self):
    return f"{self.row}:{self.column}"
