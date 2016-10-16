import sys
sys.path.insert(0, "../boardgamebot")

from tools import input_parser

print(input_parser.parseCommand("/bb heyho    "))
print(input_parser.parseCommand("/bb@BoardGameTestBot heyho"))
print(input_parser.parseCommand("/bb@BoardGamBot heyho"))
print(input_parser.parseCommand("bb@BoardGamBot heyho"))
print(input_parser.parseCommand("/start"))
print("\n")
print(input_parser.parseInlineCommand("/bb heyho"))
print(input_parser.parseInlineCommand("/bb@BoardGameTestBot heyho"))
print(input_parser.parseInlineCommand("/bb@BoardGamBot heyho  "))
print(input_parser.parseInlineCommand("  i 145654"))
print(input_parser.parseInlineCommand("/start"))
