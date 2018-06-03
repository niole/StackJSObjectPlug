import neovim
import re

containsObjectPattern = re.compile('{\s*.+:\s*.+,')

@neovim.plugin
class Main(object):
    def __init__(self, vim):
        self.vim = vim

    def get_current_line_number(self):
        return self.vim.current.window.cursor[0]

    @neovim.command('Sobj', range='', nargs='*', sync=True)
    def command_handler(self, args, range):
        toStack = self.vim.current.line
        #if containsObjectPattern.match(toStack):
        splitStackable = toStack.split(',')
        index = self.get_current_line_number()
        self.vim.current.line = splitStackable[0]
        self.vim.current.buffer.append(splitStackable[1:], index)
