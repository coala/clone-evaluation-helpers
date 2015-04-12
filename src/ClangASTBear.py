from coalib.bears.LocalBear import LocalBear
import clang.cindex as ci


class ClangASTBear(LocalBear):
    def print_clang_cursor(self,
                           cursor,
                           filename,
                           indent="",
                           stack=None,
                           max_recursion=20):
        if stack is None:
            stack = []

        if len(indent) > max_recursion*2:
            print("ABORTING")
            return

        file = cursor.location.file
        name = None if file is None else file.name.decode()

        if str(name) == str(filename):
            self.debug_msg(indent + "Got child:")
            self.debug_msg(indent + "KIND:", str(cursor.kind))
            self.debug_msg(indent + "FILE:", str(name))
            self.debug_msg(indent + "USR :", str(cursor.get_usr()))
            self.debug_msg(indent + "DISP:", str(cursor.displayname))
            if cursor.is_definition():
                self.debug_msg(indent + "DEFI:", str(cursor.get_definition()))

        for child in cursor.get_children():
            self.print_clang_cursor(child, filename, indent+"| ")

    def run(self, filename, file, *args):
        index = ci.Index.create()
        tree = index.parse(filename)

        self.print_clang_cursor(tree.cursor, filename)
