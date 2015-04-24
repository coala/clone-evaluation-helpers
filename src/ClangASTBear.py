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


def is_nth_child_of_kind(stack, allowed_nums, kind):
    """
    Checks if the stack contains a cursor with is of the given kind and the
    stack also has a child of this element which number is in the allowed_nums
    list.

    :param stack:        The stack holding a tuple holding the parent cursors
                         and the child number.
    :param allowed_nums: List of child numbers allowed.
    :param kind:         The kind of the parent element.
    :return:             True if the described situation matches.
    """
    is_kind_child = False
    for elem, child_num in stack:
        if is_kind_child and child_num in allowed_nums:
            return True

        if elem.kind == kind:
            is_kind_child = True
        else:
            is_kind_child = False

    return False


def is_condition(cursor, stack):
    return is_nth_child_of_kind(stack, [0], ci.CursorKind.IF_STMT)


def is_in_condition(cursor, stack):
    return is_nth_child_of_kind(stack, [1, 2], ci.CursorKind.IF_STMT)


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
