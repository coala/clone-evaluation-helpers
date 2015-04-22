from coalib.bears.LocalBear import LocalBear
from bears.codeclone_detection.CountVector import CountVector
from coalib.bearlib.parsing.clang import cindex as ci
from coalib.results.Result import Result


def no_condition(cursor, stack):
    return True


def is_call_argument(cursor, stack):
    return ci.CursorKind.CALL_EXPR in stack


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

        if cursor.kind == ci.CursorKind.BINARY_OPERATOR:
            self.debug(len(stack)*"|", "EXTE:", str(cursor.extent))
            ci.TokenGroup.get_tokens(cursor.translation_unit, cursor.extent)

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

        if self.is_variable_declaration(cursor) and str(name) == str(filename):
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

        count_dict = self.get_vectors(tree.cursor,
                                      filename,
                                      conditions=[no_condition,
                                                  is_call_argument])
        return [Result(self.__class__.__name__,
                       "COUNT DICT IS: " + str(count_dict),
                       filename)]
