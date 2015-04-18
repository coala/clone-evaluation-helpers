from coalib.bears.LocalBear import LocalBear
from bears.codeclone_detection.CountVector import CountVector
import clang.cindex as ci


class ClangASTBear(LocalBear):
    @staticmethod
    def is_function_declaration(cursor):
        return cursor.kind == ci.CursorKind.FUNCTION_DECL

    @staticmethod
    def is_variable_declaration(cursor):
        return (cursor.kind == ci.CursorKind.VAR_DECL or
                cursor.kind == ci.CursorKind.PARM_DECL)

    @staticmethod
    def is_variable_reference(cursor, vars):
        return (cursor.kind is ci.CursorKind.DECL_REF_EXPR and
                cursor.displayname.decode() in vars)

    def get_variables(self,
                      cursor,
                      local_vars=None,
                      conditions=None,
                      weightings=None,
                      stack=None):
        if stack is None:
            stack = []
        if local_vars is None:
            local_vars = {}

        if self.is_variable_declaration(cursor):
            self.warn("DECLARATION")
            local_vars[cursor.displayname.decode()] = CountVector(
                cursor.displayname.decode(),
                conditions,
                weightings)

        if self.is_variable_reference(cursor, local_vars):
            local_vars[cursor.displayname.decode()].count_reference(cursor,
                                                                    stack)

        self.debug(len(stack)*"|", "Got child:")
        self.debug(len(stack)*"|",
                   "SCOP:",
                   str(stack.count(ci.CursorKind.COMPOUND_STMT)))
        self.debug(len(stack)*"|", "KIND:", str(cursor.kind))
        self.debug(len(stack)*"|", "USR :", str(cursor.get_usr()))
        self.debug(len(stack)*"|", "DISP:", str(cursor.displayname.decode()))
        if cursor.is_definition():
            self.debug(len(stack)*"|", "DEFI:", str(cursor.get_definition()))

        stack.append(cursor.kind)
        for child in cursor.get_children():
            local_vars = self.get_variables(child,
                                            local_vars,
                                            conditions,
                                            weightings,
                                            stack)
        stack.pop()

        return local_vars

    def get_vectors(self,
                    cursor,
                    filename,
                    global_vars=None,
                    conditions=None,
                    weightings=None):
        if global_vars is None:
            global_vars = {}
        file = cursor.location.file
        name = None if file is None else file.name.decode()

        if self.is_variable_declaration(cursor):
            global_vars[cursor.displayname.decode()] = CountVector(
                cursor.displayname.decode(),
                conditions,
                weightings)

        if str(name) == str(filename) and self.is_function_declaration(cursor):
            global_vars = self.get_variables(cursor,
                                             global_vars,
                                             conditions,
                                             weightings)
        else:
            for child in cursor.get_children():
                global_vars = self.get_vectors(child,
                                               filename,
                                               global_vars,
                                               conditions,
                                               weightings)

        return global_vars

    def run(self, filename, file, *args):
        index = ci.Index.create()
        tree = index.parse(filename)

        self.debug(str(self.get_vectors(tree.cursor,
                                        filename,
                                        conditions=[lambda cursor, stack: True])))
