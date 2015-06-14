import os
from collections import OrderedDict
from queue import Queue
import re

from bears.codeclone_detection.ClangSimilarityBear import (
    counting_condition_dict,
    ClangSimilarityBear)
from coalib.collecting.Collectors import collect_files
from coalib.misc.StringConverter import StringConverter
from coalib.output.printers.ConsolePrinter import ConsolePrinter
from coalib.processes.Processing import get_file_dict
from coalib.settings.Section import Section
from coalib.settings.Setting import Setting

condition_dict = counting_condition_dict(StringConverter(
    """
used: 0.0,
third_level_loop_content: 1.0,
second_level_loop_content: 1.0,
returned: 0.0,
member_accessed: 1.0,
loop_content: 0.4,
is_param: 0.0,
is_condition: 0.8,
is_called: 0.0,
is_call_param: 1.0,
is_assigner: 0.2,
is_assignee: 0.5,
in_third_level_condition: 1.0,
in_sum: 1.8,
in_second_level_condition: 1.2,
in_product: 0.8,
in_condition: 1.0,
in_binary_operation: 1.0"""))

weighting_range = [x/5 for x in range(0, 10)]
non_excluded_functions = ["faculty(int)", "faculty1(int)", "faculty2(int)",
                          "clearScreen()", "original(int)", "sumProd(int)",
                          "scrollUp()"]

section = Section("default")
section.append(Setting("files",
                       "../coala/bears/tests/codeclone_detection"
                       "/clone_detection_samples/**/*.c",
                       origin=os.path.abspath(
    "../coala/bears/tests/codeclone_detection/clone_detection_samples/")))
log_printer = ConsolePrinter()
filename_list = collect_files(['/home/lasse/prog/coala/bears/tests/codeclone_detection/clone_detection_samples/**/*.c'], log_printer)
file_dict = get_file_dict(filename_list, log_printer)

sorted_dict = OrderedDict(reversed(sorted(condition_dict.items(),
                                 key=lambda f: f[0].__name__)))
message_queue = Queue()


def fitness(c_dict):
    differences = ClangSimilarityBear(file_dict, section, message_queue).run(
        c_dict)[0].contents

    clones_diffs = [0]
    non_clones_diffs = [1]
    clones=".*\/clones.*"
    these_nonexcluded = non_excluded_functions.copy()

    for function_1, function_2, difference in differences:
        if function_1[2] in these_nonexcluded:
            these_nonexcluded.remove(function_1[2])
        if function_2[2] in these_nonexcluded:
            these_nonexcluded.remove(function_2[2])
        if function_1[0] != function_2[0]:
            continue

        if re.match(clones, function_1[0]) is not None:
            clones_diffs.append(difference)
        else:
            non_clones_diffs.append(difference)

    if len(these_nonexcluded) > 0:
        return -1

    return min(non_clones_diffs) - max(clones_diffs)


def optimize_key(c_dict, key, old_fitness):
    best = (c_dict[key], old_fitness)
    for weighting in weighting_range:
        print("Checking", key.__name__, "with", weighting, "...")
        c_dict[key] = weighting
        fit = fitness(c_dict)
        if fit > best[1]:
            print("Better fitness found:", fit)
            best = weighting, fit

    c_dict[key] = best[0]
    return best[1]


if __name__ == '__main__':
    new_fitness = fitness(sorted_dict)
    print("Initial fitness:", new_fitness)
    for key in sorted_dict.keys():
        new_fitness = optimize_key(sorted_dict, key, new_fitness)
        print("Weightings are:")
        for key in sorted_dict.keys():
            print("  ", key.__name__+":", str(sorted_dict[key])+",")

    print("\n\nFINISHED.\n\n")
    print("Got fitness:", new_fitness)
    print("Weightings are:")
    for key in sorted_dict.keys():
        print("  ", key.__name__+":", str(sorted_dict[key])+",")
