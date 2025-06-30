from shared.position import TokenPosition

# root abstract error
class Error(Exception):
  def __init__(self, position: TokenPosition, message: str):
    super().__init__()

    self.position = position
    self.message = message
