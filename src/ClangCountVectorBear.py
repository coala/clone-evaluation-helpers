from coalib.bears.LocalBear import LocalBear
from bears.codeclone_detection.ClangCountVectorCreator import \
    ClangCountVectorCreator
from bears.codeclone_detection import ClangCountingConditions
from coalib.results.Result import Result


class ClangCountVectorBear(LocalBear):
    def run(self,
            filename,
            file,
            condition_list: ClangCountingConditions.counting_condition):
        """
        Creates a count vector for each function in the given file(s).

        :param condition_list: A list of counting conditions. Possible values
                               are used, returned, is_condition, in_condition,
                               is_assignee, is_assigner, loop_content.
        """
        cc = ClangCountVectorCreator(conditions=condition_list)
        count_dict = cc.get_vectors_for_file(filename)
        return [Result(self.__class__.__name__,
                       "COUNT DICT IS: " + str(count_dict),
                       filename)]
