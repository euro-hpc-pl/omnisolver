import numpy as np
import pandas as pd

from omnisolver.cmd import main

SMALL_QUBO = """
2 3 -1
0 1 2
3 0 -0.5
"""


def test_command_line_interface_accepts_common_and_solver_arguments(tmp_path):
    output_file = tmp_path / "output.txt"
    input_file = tmp_path / "input.txt"

    input_file.write_text(SMALL_QUBO.strip())

    argv = [
        "random",
        str(input_file),
        "--prob",
        "0.3",
        "--output",
        str(output_file),
        "--num_reads",
        "13",
    ]
    main(argv)

    df = pd.read_csv(output_file)
    print(df)
    assert df.shape == (13, 6)  # 6 = 4 vars + one column for energy and one for num_occurrences
    np.testing.assert_array_equal(df.columns, ["0", "1", "2", "3", "energy", "num_occurrences"])
