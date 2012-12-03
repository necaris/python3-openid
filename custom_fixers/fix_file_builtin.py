from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import is_probably_builtin
from lib2to3.pgen2 import token


class FixFileBuiltin(BaseFix):

    _accept_type = token.NAME

    def match(self, node):
        if node.value == 'file' and is_probably_builtin(node):
            return True
        return False

    def transform(self, node, results):
        node.value = 'open'
        node.changed()
