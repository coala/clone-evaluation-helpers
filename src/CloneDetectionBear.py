from itertools import combinations
from bears.codeclone_detection.CountVector import CountVector
from munkres import Munkres
# Instantiate globally since this class is holding stateless public methods.
munkres = Munkres()

from coalib.bears.GlobalBear import GlobalBear
from bears.codeclone_detection.ClangCountVectorCreator import \
    ClangCountVectorCreator
from bears.codeclone_detection import ClangCountingConditions


class CloneDetectionBear(GlobalBear):
    def exclude_function(self, count_matrix):
        """
        Determines heuristically wether or not it makes sense for clone
        detection to take this function into account.

        :param count_matrix: The count dict representing the function.
        :return:             True if the function is useless for evaluation.
        """
        return all(sum(cv.count_vector) < 2 for cv in count_matrix.values())

    def get_count_matrices(self, condition_list):
        """
        Retrieves matrices holding count vectors for all variables for all
        functions in the given file.

        :param filename: The filename of the file to examine.
        :return:         A dict holding keys like "file|function" and a dict of
                         count vector objects with variable names as key as
                         content.
        """
        result = {}
        cc = ClangCountVectorCreator(
            conditions=condition_list,
            weightings=[0.5] + [1 for i in range(len(condition_list)-1)])

        for filename in self.file_dict:
            self.debug("Creating count dict for file", filename, "...")
            count_dict = cc.get_vectors_for_file(filename)
            for function in count_dict:
                if not self.exclude_function(count_dict[function]):
                    result[filename + "|" + function] = count_dict[function]
                else:
                    self.debug("Excluding function", function)


        return result

    def compare_functions(self, cm1, cm2):
        """
        Compares the functions represented by the given count matrices.

        :param cm1: Count vector dict for the first function.
        :param cm2: Count vector dict for the second function.
        :return:    The difference between these functions, 0 is identical and
                    1 is not similar at all.
        """
        assert isinstance(cm1, dict)
        assert isinstance(cm2, dict)
        if len(cm1) == 0 or len(cm2) == 0:
            return 1 if len(cm1) != len(cm2) else 0

        # The cost matrix holds the difference between the two variables i and
        # j in the i/j field. This is a representation of a bipartite weighted
        # graph with nodes representing the first function on the one side
        # (rows) and the nodes representing the second function on the other
        #  side (columns). The fields in the matrix are the weighted nodes
        # connecting each element from one side to the other.
        cost_matrix = [[cv1.difference(cv2)
                        for cv2 in cm2.values()]
                       for cv1 in cm1.values()]

        # Pad manually with ones. If we have one variable in one function and
        # no corresponding in the other this is 100% difference, so 1.
        cost_matrix = munkres.pad_matrix(cost_matrix, pad_value=1)

        # The munkres algorithm will calculate a matching such that the sum of
        # the taken fields is minimal. It thus will associate each variable
        # from one function to one on the other function.
        matching = munkres.compute(cost_matrix)

        # Sum it up, normalize it so we have a value in [0, 1]
        return sum(cost_matrix[x][y] for x, y in matching)/max(len(cm1),
                                                               len(cm2))

    def run(self,
            condition_list: ClangCountingConditions.counting_condition,
            dependency_results=None):
        self.debug("Using the following counting conditions:")
        for condition in condition_list:
            self.debug(" *", condition.__name__)

        count_matrices = self.get_count_matrices(condition_list)
        function_duplications = {}
        self.debug("Found functions:")
        for key in count_matrices.keys():
            function_duplications[key] = False
            self.debug(" *", key)

        clones = 0
        not_clones = 0
        # Check each function with each other one (combinations of 2)
        for function_1, function_2 in combinations(count_matrices, 2):
            difference = self.compare_functions(count_matrices[function_1],
                                                count_matrices[function_2])
            if difference < 0.2:
                clones += 1
                self.warn("Clone found! Difference of {} and {} is {}".format(
                    function_1[function_1.rfind("/")+1:function_1.rfind("(")],
                    function_2[function_2.rfind("/")+1:function_2.rfind("(")],
                    difference))
                self.warn("MATRICES:",
                          str(count_matrices[function_1]),
                          str(count_matrices[function_2]),
                          delimiter="\n")
                function_duplications[function_1] = True
                function_duplications[function_2] = True
            else:
                not_clones += 1
                self.debug("{} and {} are unique with difference {}.".format(
                    function_1[function_1.rfind("/")+1:function_1.rfind("(")],
                    function_2[function_2.rfind("/")+1:function_2.rfind("(")],
                    difference))

        self.err("There are {} clone combinations and {} non-clone "
                 "combinations of {} functions (others excluded "
                 "heuristically).".format(clones,
                                          not_clones,
                                          len(count_matrices)))
        self.err("{} functions are in duplication status, {} are not.".format(
            list(function_duplications.values()).count(True),
            list(function_duplications.values()).count(False)))
