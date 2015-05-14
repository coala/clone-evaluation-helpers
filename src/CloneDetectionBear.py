from itertools import combinations


from coalib.bears.GlobalBear import GlobalBear
from bears.codeclone_detection.ClangCountVectorCreator import \
    ClangCountVectorCreator
from bears.codeclone_detection import ClangCountingConditions
from coalib.processes.SectionExecutor import get_cpu_count
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

        self.debug("Outputting clones:")
        function_duplications = {}
        clones = 0
        not_clones = 0
        for function_1, function_2, difference in differences:
            if difference < max_clone_difference:
                clones += 1
                self.warn("Clone found! Difference of {} and {} is {}".format(
                    function_1[1][1], function_2[1][1], difference))
                self.debug("Count Matrices:",
                           str(count_matrices[function_1]),
                           str(count_matrices[function_2]),
                           delimiter="\n")
                function_duplications[function_1] = True
                function_duplications[function_2] = True
            else:
                not_clones += 1
                self.debug("{} and {} are unique with difference {}.".format(
                    function_1[1][1], function_2[1][1], difference))

        self.err("There are {} clone combinations and {} non-clone "
                 "combinations of {} functions (others excluded "
                 "heuristically).".format(clones,
                                          not_clones,
                                          len(count_matrices)))
        self.err("{} functions are in duplication status, {} are not.".format(
            list(function_duplications.values()).count(True),
            list(function_duplications.values()).count(False)))
