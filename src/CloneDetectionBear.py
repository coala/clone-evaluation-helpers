from itertools import combinations
from munkres import Munkres
# Instantiate globally since this class is holding stateless public methods.
munkres = Munkres()

from coalib.bears.GlobalBear import GlobalBear
from bears.codeclone_detection.ClangCountVectorCreator import \
    ClangCountVectorCreator
from bears.codeclone_detection import ClangCountingConditions


class CloneDetectionBear(GlobalBear):
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
        cc = ClangCountVectorCreator(conditions=condition_list)

        for filename in self.file_dict:
            self.debug("Creating count dict for file", filename, "...")
            count_dict = cc.get_vectors_for_file(filename)
            for function in count_dict:
                result[filename + "|" + function] = count_dict[function]

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
        self.debug("Found functions:")
        for key in count_matrices.keys():
            self.debug(" *", key)

        # Check each function with each other one (combinations of 2)
        for function_1, function_2 in combinations(count_matrices, 2):
            difference = self.compare_functions(count_matrices[function_1],
                                                count_matrices[function_2])
            if difference < 0.2:
                self.warn("Clone found! Difference of {} and {} is {}".format(
                    function_1[function_1.rfind("/"):],
                    function_2[function_2.rfind("/"):],
                    difference))
            else:
                self.debug("{} and {} are identified as unique "
                           "with difference {}.".format(
                    function_1[function_1.rfind("/"):],
                    function_2[function_2.rfind("/"):],
                    difference))
