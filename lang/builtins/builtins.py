import builtins.modules.types as types
import builtins.modules.console as console

# compose list of all builtin declarations
builtins = [
  *types.declarations,
  *console.declarations,
]
