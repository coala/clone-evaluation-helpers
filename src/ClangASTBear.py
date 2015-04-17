from coalib.bears.LocalBear import LocalBear
import clang.cindex as ci

class ClangASTBear(LocalBear):
    @staticmethod
    def is_function_declaration(cursor):
        return cursor.kind == ci.CursorKind.FUNCTION_DECL

    def get_variables(self,
                      cursor,
                      stack=None):
        if stack is None:
            stack = []

        self.debug(len(stack)*"|", "Got child:")
        self.debug(len(stack)*"|", "SCOP:", str(stack.count(ci.CursorKind.COMPOUND_STMT)))
        self.debug(len(stack)*"|", "KIND:", str(cursor.kind))
        self.debug(len(stack)*"|", "USR :", str(cursor.get_usr()))
        self.debug(len(stack)*"|", "DISP:", str(cursor.displayname))
        if cursor.is_definition():
            self.debug(len(stack)*"|", "DEFI:", str(cursor.get_definition()))

        stack.append(cursor.kind)
        for child in cursor.get_children():
            self.get_variables(child, stack)
        stack.pop()

    def get_vectors(self,
                    cursor,
                    filename):
        file = cursor.location.file
        name = None if file is None else file.name.decode()

        if str(name) == str(filename) and self.is_function_declaration(cursor):
            self.get_variables(cursor)

        for child in cursor.get_children():
            self.get_vectors(child, filename)

    def run(self, filename, file, *args):
        index = ci.Index.create()
        tree = index.parse(filename)

        self.get_vectors(tree.cursor, filename)
