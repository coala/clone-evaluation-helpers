from itertools import combinations


from coalib.bears.GlobalBear import GlobalBear
from coalib.misc.i18n import _
from bears.codeclone_detection.ClangCountVectorCreator import \
    ClangCountVectorCreator
from bears.codeclone_detection import ClangCountingConditions
from coalib.processes.SectionExecutor import get_cpu_count
from coalib.results.RESULT_SEVERITY import RESULT_SEVERITY
from coalib.results.Result import Result
from coalib.settings.Setting import typed_dict
from bears.codeclone_detection.CloneDetectionRoutines import \
    compare_functions, \
    get_count_matrices
import multiprocessing


counting_condition_dict = typed_dict(
    lambda setting:
    ClangCountingConditions.condition_dict[str(setting).lower()],
    float,
    1)


def get_difference(args):
    function_1, function_2, count_matrices = args
    return (function_1,
            function_2,
            compare_functions(count_matrices[function_1],
                              count_matrices[function_2]))


class CloneDetectionBear(GlobalBear):
    def run(self,
            condition_list: counting_condition_dict,
            max_clone_difference: float=0.2):
        if not isinstance(condition_list, dict):
            self.err("The condition_list setting is not valid.")
            counting_condition_dict(condition_list)
            return

        self.debug("Using the following counting conditions:")
        for key, val in condition_list.items():
            self.debug(" *", key.__name__, "(weighting: {})".format(val))

        count_matrices = get_count_matrices(
            ClangCountVectorCreator(list(condition_list.keys()),
                                    list(condition_list.values())),
            self.file_dict.keys())

        self.debug("Calculating differences...")
        pool = multiprocessing.Pool(get_cpu_count())
        differences = pool.map(
            get_difference,
            [(f1, f2, count_matrices)
             for f1, f2 in combinations(count_matrices, 2)])

        results = []
        for function_1, function_2, difference in differences:
            if difference < max_clone_difference:
                results.append(Result(
                    self.__class__.__name__,
                    _("Code clone found. The other occurrence is at file "
                      "{file}, line {line}, function {function}. The "
                      "similarity is {similarity}.").format(
                        file=function_2[0],
                        line=function_2[1],
                        function=function_2[2],
                        similarity=1-difference),
                    file=function_1[0],
                    severity=RESULT_SEVERITY.MAJOR,
                    line_nr=function_1[1]))

        return results
