known_tools = []


def add_tool(func):
  """
  Decorator to add a tool to the list of known tools.
  """
  known_tools.append(func)
  return func
