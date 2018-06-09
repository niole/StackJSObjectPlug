import neovim
import esprima
import re

isJSDeclarator = re.compile('var|let|const')

def safeNext(parsed, afterIndex):
    tokens = parsed[1]
    if len(tokens) > afterIndex + 1:
        return tokens[afterIndex + 1:]
    return []

def clone(l):
    return l[0:]

def appendNextParsed(prevParsed, parsedMutatingAppend, afterIndex):
    clonedParsed = clone(prevParsed[0])
    parsedMutatingAppend(clonedParsed)
    return clonedParsed, safeNext(prevParsed, afterIndex), False

def addToLast(parsed, toAdd):
    parsed[len(parsed) - 1] = parsed[len(parsed) - 1] + toAdd
    return parsed

def getFailure(parsed):
    return parsed[0], parsed[1], True

def isDeclaration(parsed):
    tokens = parsed[1]
    if len(tokens) > 2:
        if tokens[0].type == 'Keyword' and isJSDeclarator.match(tokens[0].value) != None and tokens[1].type == 'Identifier' and tokens[2].value == '=':
            mutator = lambda clonedParsed: clonedParsed.append("{0} {1} {2}".format(*[tokens[i].value for i in range(3)]))
            return appendNextParsed(parsed, mutator, 2)
    return getFailure(parsed)

def isOpenParen(parsed):
    tokens = parsed[1]
    if len(tokens) > 0 and tokens[0].value == '{':
        mutator = lambda cloned: cloned.append('{')
        return appendNextParsed(parsed, mutator, 0)

    return getFailure(parsed)

def isSingleObjectContent(parsed):
    tokens = parsed[1]
    if len(tokens) > 2:
        if tokens[0].type == 'Identifier' and tokens[1].value == ':' and tokens[2].type :
            mutator = lambda cloned: cloned.append("{0}{1} {2}".format(*[tokens[i].value for i in range(3)]))
            return appendNextParsed(parsed, mutator, 2)

    return getFailure(parsed)

def isComma(parsed):
    tokens = parsed[1]
    if len(tokens) > 0:
        if tokens[0].value == ',':
            mutator = lambda cloned: addToLast(cloned, ',')
            return appendNextParsed(parsed, mutator, 0)
    return getFailure(parsed)

def isObjectContents(parsed):
    parsedSingleObjectContent = isSingleObjectContent(parsed)
    if parsedSingleObjectContent[2]:
        return parsedSingleObjectContent

    parsedComma = isComma(parsedSingleObjectContent)
    if parsedComma[2]:
        return parsedSingleObjectContent
    return isObjectContents(parsedComma)

def isClosedParen(parsed):
    tokens = parsed[1]
    if len(tokens) > 0 and tokens[0].value == '}':
        mutator = lambda cloned: cloned.append('}')
        return appendNextParsed(parsed, mutator, 0)
    return getFailure(parsed)

def isOptionalSemicolon(parsed):
    tokens = parsed[1]
    if len(tokens) > 0 and tokens[0].value == ';':
        mutator = lambda cloned: addToLast(cloned, ';')
        return appendNextParsed(parsed, mutator, 0)
    return parsed

def isObject(parsed):
    parsedOpenParen = isOpenParen(parsed)
    if parsedOpenParen[2]:
        return parsedOpenParen
    parsedObjectContents = isObjectContents(parsedOpenParen)
    if parsedObjectContents[2]:
        return parsedObjectContents
    parsedClosedParen = isClosedParen(parsedObjectContents)
    if parsedClosedParen[2]:
        return parsedClosedParen
    return isOptionalSemicolon(parsedClosedParen)


def isDeclaredObject(parsed):
    parsedDeclaration = isDeclaration(parsed)
    if parsedDeclaration[2]:
        return parsedDeclaration
    return isObject(parsedDeclaration)

def parseObject(code):
    tokens = esprima.tokenize(code)
    return isDeclaredObject(([], tokens, False))

@neovim.plugin
class Main(object):
    def __init__(self, vim):
        self.vim = vim

    def get_current_line_number(self):
        return self.vim.current.window.cursor[0]

    @neovim.command('Sobj', range='', nargs='*', sync=True)
    def command_handler(self, args, range):
        toStack = self.vim.current.line
        tokens = esprima.tokenize(toStack)
        parsedObject = isDeclaredObject(([], tokens, False))
        if not parsedObject[2]:
            index = self.get_current_line_number()
            parsed = parsedObject[0]
            self.vim.current.line = parsed[0]
            self.vim.current.buffer.append(parsed[1:], index)
