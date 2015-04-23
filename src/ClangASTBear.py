from coalib.bears.LocalBear import LocalBear
from bears.codeclone_detection.ClangCountVectorCreator import \
    ClangCountVectorCreator
from coalib.bearlib.parsing.clang import cindex as ci
from coalib.results.Result import Result


def no_condition(cursor, stack):
    return True


def is_call_argument(cursor, stack):
    for elem, child_num in stack:
        if elem.kind == ci.CursorKind.CALL_EXPR:
            return True

    return False


def is_returned(cursor, stack):
    for elem, child_num in stack:
        if elem.kind == ci.CursorKind.RETURN_STMT:
            return True

    return False


def is_condition(cursor, stack):
    last_if_present = False
    for elem, child_num in stack:
        # The first child of an IF_STMT is the condition.
        if last_if_present and child_num == 0:
            return True

        if elem.kind == ci.CursorKind.IF_STMT:
            last_if_present = True
        else:
            last_if_present = False

    return False


def is_in_condition(cursor, stack):
    last_if_present = False
    for elem, child_num in stack:
        # The second child of an if is its body, the third is the else branch
        if last_if_present and child_num in [1, 2]:
            return True

        if elem.kind == ci.CursorKind.IF_STMT:
            last_if_present = True
        else:
            last_if_present = False

    return False


class ClangASTBear(LocalBear):
    def run(self, filename, file, *args):
        cc = ClangCountVectorCreator(conditions=[no_condition,
                                                 is_call_argument,
                                                 is_returned,
                                                 is_condition,
                                                 is_in_condition])
        count_dict = cc.get_vectors_for_file(filename)
        return [Result(self.__class__.__name__,
                       "COUNT DICT IS: " + str(count_dict),
                       filename)]
