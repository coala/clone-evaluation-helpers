from coalib.bears.LocalBear import LocalBear
import clang.cindex as ci


class ClangASTBear(LocalBear):
    @staticmethod
    def is_function_declaration(cursor):
        return cursor.kind == ci.CursorKind.FUNCTION_DECL

    def get_vectors(self,
                    cursor,
                    filename,
                    stack=None):
        if stack is None:
            stack = []
        file = cursor.location.file
        name = None if file is None else file.name.decode()

        if str(name) == str(filename):
            if self.is_function_declaration(cursor):
                self.warn("THIS IS A FUNCTION DECL")
            self.debug(len(stack)*"|", "Got child:")
            self.debug(len(stack)*"|", "STACK:", *stack)
            self.debug(len(stack)*"|", "KIND:", str(cursor.kind))
            self.debug(len(stack)*"|", "FILE:", str(name))
            self.debug(len(stack)*"|", "USR :", str(cursor.get_usr()))
            self.debug(len(stack)*"|", "DISP:", str(cursor.displayname))
            if cursor.is_definition():
                self.debug(len(stack)*"|", "DEFI:", str(cursor.get_definition()))

        stack.append(str(cursor.kind))
        for child in cursor.get_children():
            self.get_vectors(child, filename, stack=stack)
        stack.pop()

    def run(self, filename, file, *args):
        index = ci.Index.create()
        tree = index.parse(filename)

        self.get_vectors(tree.cursor, filename)
