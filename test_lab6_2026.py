"""
pytest test suite for Lab 6 (2026) - Data Visualization assignment.

USAGE
-----
Point the suite at a single submitted notebook:

    NOTEBOOK_PATH=/path/to/student_submission.ipynb pytest test_lab6_2026.py -v --tb=short

Or point it at a folder full of submissions to grade the whole class in one
run (every question is tested against every *.ipynb file found):

    NOTEBOOK_PATH=/path/to/submissions_folder pytest test_lab6_2026.py -v --tb=short

If NOTEBOOK_PATH isn't set, the suite looks for a "submissions/" folder next
to this test file, and falls back to any *.ipynb file in the current
directory.

WHAT EACH QUESTION CHECKS
---------------------------
Q1 (plot_one_stock): the function returns a dict with the right axis labels
and exactly one line plotted.
Q2 (plot_all_stocks): six lines plotted, and a legend is present.
Q3 (test_result_g1, sns.relplot): two subplots ("time = Lunch" /
"time = Dinner").
Q4 (test_result_g2, px.line): six lines.
Q5 (test_result_g3, px.scatter facets): both facet titles present.

Execution failures (e.g. a student's cell raising an exception) are caught
and reported as one short line.
"""

import contextlib
import glob
import os

import pytest

# Aliased on import: pytest's default test-discovery prefix is the bare
# string "test" (not "test_"), so an unaliased `testbook` name at module
# level risks being mistaken for a test item by pytest depending on how
# the installed testbook version defines it. Aliasing sidesteps that
# entirely.
from testbook import testbook as _open_notebook


# ---------------------------------------------------------------------------
# Notebook discovery
# ---------------------------------------------------------------------------

def _discover_notebooks():
    """Return a sorted list of notebook paths to test, based on the
    NOTEBOOK_PATH environment variable (a single .ipynb file OR a folder of
    them), falling back to a local 'submissions/' folder or any *.ipynb in
    the current directory."""
    env_path = os.environ.get("NOTEBOOK_PATH")

    if env_path:
        if os.path.isdir(env_path):
            return sorted(glob.glob(os.path.join(env_path, "*.ipynb")))
        return [env_path]

    if os.path.isdir("submissions"):
        return sorted(glob.glob(os.path.join("submissions", "*.ipynb")))

    return sorted(glob.glob("*.ipynb"))


def pytest_generate_tests(metafunc):
    if "notebook_path" in metafunc.fixturenames:
        paths = _discover_notebooks()
        if not paths:
            paths = [None]  # yields one clearly-failing test instead of "no tests collected"
        ids = [os.path.basename(p) if p else "NO_NOTEBOOK_FOUND" for p in paths]
        metafunc.parametrize("notebook_path", paths, ids=ids)


# ---------------------------------------------------------------------------
# Execute each discovered notebook's kernel exactly once, keeping it
# alive so all 5 question tests for that notebook can query the same live
# kernel via tb.ref(...). 
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def _tb_cache():
    stack = contextlib.ExitStack()
    cache = {}

    def _get(path):
        if path is None:
            pytest.fail(
                "No notebook found to test. Set the NOTEBOOK_PATH environment "
                "variable to a student's .ipynb file (or a folder of them), "
                "e.g.: NOTEBOOK_PATH=submission.ipynb pytest test_lab6_2026.py -v",
                pytrace=False,
            )
        if not os.path.exists(path):
            pytest.fail(f"Notebook not found: {path}", pytrace=False)
        if path not in cache:
            exec_error = None
            try:
                cache[path] = stack.enter_context(_open_notebook(path, execute=True))
            except Exception as e:  # noqa: BLE001 - deliberately broad
                # nbclient raises with the full remote traceback embedded in
                # the exception text, which can be huge. Save just a short
                # message and fail *outside* the except block below --
                # calling pytest.fail() while still inside `except` would
                # chain this exception in as context, printing its full
                # (possibly huge) traceback despite pytrace=False.
                exec_error = f"{os.path.basename(path)} failed to execute: {type(e).__name__}: {e}"
            if exec_error is not None:
                pytest.fail(exec_error, pytrace=False)
        return cache[path]

    yield _get
    stack.close()


@pytest.fixture
def tb(_tb_cache, notebook_path):
    return _tb_cache(notebook_path)


# ---------------------------------------------------------------------------
# Tests -- one per question, parametrized over every discovered notebook
# ---------------------------------------------------------------------------

# Q1 test the plot_one_stock function
def test_plot_one_stock(tb, notebook_path):
    plot_one_stock = tb.ref("plot_one_stock")
    result = plot_one_stock()
    assert result["xlabel"] == "Date", "Error: x-axis label is incorrect"
    assert result["ylabel"] == "Stock Value", "Error: y-axis label is incorrect"
    assert result["num_lines"] == 1, "Error: There should be one line plotted"


# Q2 test the plot_all_stocks function
def test_plot_all_stocks(tb, notebook_path):
    plot_all_stocks = tb.ref("plot_all_stocks")
    result = plot_all_stocks()
    assert result["num_lines"] == 6, "Error: There should be six lines plotted"
    assert result['legend_exists'], "Error: Legend does not exist."


# Q3: test the sns.relplot function
def test_sns_relplot(tb, notebook_path):
    # Reference the relplot function in the notebook
    result = tb.ref("test_result_g1")

    # Assertions
    assert result["num_axes"] == 2, "Error: There should be 2 subplots (one for each time)."
    assert "time = Lunch" in result["col_titles"], "Error: Missing title for Lunch subplot."
    assert "time = Dinner" in result["col_titles"], "Error: Missing title for Dinner subplot."


# Q4: test plotly express line plot
def test_px_line(tb, notebook_path):
    result = tb.ref("test_result_g2")
    assert result["num_lines"] == 6, "Error: There should be six lines plotted"


# Q5: test plotly express scatter plot with facets
def test_px_scatter(tb, notebook_path):
    result = tb.ref("test_result_g3")
    expected_facets = ["time=Lunch", "time=Dinner"]
    assert all(facet in result["facet_titles"] for facet in expected_facets), "Error: Facet titles are incorrect."
