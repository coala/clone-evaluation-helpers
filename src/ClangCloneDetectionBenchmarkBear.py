import re
from matplotlib import pyplot as plt
import numpy as np

from coalib.bears.GlobalBear import GlobalBear
from bears.codeclone_detection.ClangFunctionDifferenceBear import ClangFunctionDifferenceBear


class ClangCloneDetectionBenchmarkBear(GlobalBear):
    def run(self,
            dependency_results: dict,
            clones: str=".*\/clones.*",
            plot: bool=False):
        '''
        Checks the quality of the code clone detection on the given test files.

        :param clones:     A regex matching paths of files that contain known
                           clones. All others are considered non-clones.
        :param plot:       Wether or not to plot the clone/non-clone graph.
        '''
        differences = dependency_results["ClangFunctionDifferenceBear"][0].contents

        clones_diffs = {0: None}
        non_clones_diffs = {1: None}

        seen_functions = []
        must_have = list(self.file_dict.keys())
        for function_1, function_2, difference in differences:
            if function_1[0] not in seen_functions:
                seen_functions.append(function_1[0])
            if function_2[0] not in seen_functions:
                seen_functions.append(function_2[0])

            if function_1[0] != function_2[0]:
                continue

            if function_1[0] in must_have:
                must_have.remove(function_1[0])

            if re.match(clones, function_1[0]) is not None:
                app_to = clones_diffs
            else:
                app_to = non_clones_diffs

            val = app_to.get(difference, None)
            if val is None:
                app_to[difference] = [(function_1[2], function_2[2])]
            else:
                val.append((function_1[2], function_2[2]))

        for filename in must_have:
            if not re.match(clones, filename):
                must_have.remove(filename)

        self.warn(" CD:", str(sorted(clones_diffs.keys())))
        self.warn("NCD:", str(sorted(non_clones_diffs.keys())))
        if must_have:
            self.err("The following clone samples were ignored:", must_have)

        self.warn("Maximum clone difference:", str(max(clones_diffs)))
        self.warn("Minimum non-clone difference:", str(min(non_clones_diffs)))
        self.warn("Fitness:", str(min(non_clones_diffs)-max(clones_diffs)))
        if max(clones_diffs) > min(non_clones_diffs) or must_have:
            self.err("Code clone detection failed!")

        self.warn("Defining clone pairs are:\n Clone : {}\n NClone: {}".format(
            clones_diffs[max(clones_diffs)],
            non_clones_diffs[min(non_clones_diffs)]))

        if plot:
            clones_diffs = list(clones_diffs.keys())
            non_clones_diffs = list(non_clones_diffs.keys())
            plt.xlim(0, 1)
            plt.ylim(0.5, 1.5)

            y = np.ones(np.shape(clones_diffs))
            plt.plot(clones_diffs, y, '|', ms=40, color='r', label="Clones")
            y = np.ones(np.shape(non_clones_diffs))
            plt.plot(non_clones_diffs, y, '|', ms=40, color='g',
                     label="Non-Clones")
            plt.grid()
            plt.show()

    @staticmethod
    def get_dependencies():
        return [ClangFunctionDifferenceBear]
