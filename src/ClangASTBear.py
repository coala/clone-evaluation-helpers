from coalib.bears.LocalBear import LocalBear
import clang.cindex


class ClangASTBear(LocalBear):
    def print_clang_cursor(self, cursor, filename, indent=""):
        if cursor is None:
            return
        if len(indent) > 40:
            print("ABORTING")
            return

        file = cursor.location.file
        name = "(No location)" if file is None else file.name.decode()

        if str(name) == str(filename):
            self.debug_msg(indent + "Got child:")
            self.debug_msg(indent + "KIND:", str(cursor.kind))
            self.debug_msg(indent + "FILE:", str(name))

        for child in cursor.get_children():
            self.print_clang_cursor(child, filename, indent+"| ")

    def run(self, filename, file, *args):
        index = clang.cindex.Index.create()
        tree = index.parse(filename)

        self.print_clang_cursor(tree.cursor, filename)
