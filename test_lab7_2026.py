"""
test_lab7_2026.py
------------------
Checks completion of the three scripts that live in this same folder: 
q1_3dplot.py, q2_geovis.py, q3_streamlit.py.

Run with:
    pytest test_lab7_2026.py -v

Requires: matplotlib, numpy, pandas, plotly, streamlit, pydeck, pytest
(the same packages the three scripts themselves need).

How this works
---------------
Each script is loaded as a fresh module directly from its file. If a
script isn't finished yet (a TODO left blank, causing a SyntaxError or a
runtime error), loading it fails with a clear message instead of a raw
traceback.

Two things are silenced so a script that calls a display method
(plt.show() / fig.show()) doesn't crash or hang when there's no screen or
browser available -- e.g. in a CI/grading environment:
  - matplotlib is put in headless ("Agg") mode, exactly like `plt.show()`
    in a script with no display -- it just does nothing.
  - plotly's Figure.show() is patched to a no-op for the same reason.
Neither of these affects what gets checked below; they only stop an
unrelated display step from failing the test.
"""

from pathlib import Path
import importlib.util
import sys

import matplotlib
matplotlib.use("Agg")  # headless-safe, must happen before any pyplot import
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pytest

HERE = Path(__file__).parent


@pytest.fixture(autouse=True, scope="session")
def _silence_plotly_show():
    """Make fig.show() a no-op for the whole test session (see module docstring)."""
    original_show = go.Figure.show
    go.Figure.show = lambda self, *args, **kwargs: None
    yield
    go.Figure.show = original_show


def load_module(filename):
    """Load filename (a sibling of this test file) as a fresh module,
    running its top-level code. Fails the test clearly if that raises."""
    path = HERE / filename
    if not path.exists():
        pytest.fail(f"{filename} was not found in {HERE} -- is it in the same folder as test_lab7_2026.py?")
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        pytest.fail(
            f"{filename} raised an error while running -- make sure every TODO "
            f"is completed and the script runs top-to-bottom without errors.\n"
            f"{type(exc).__name__}: {exc}"
        )
    return module


# ===========================================================================
# Question 1 -- q1_3dplot.py (3D surface + wireframe plot, Matplotlib)
# ===========================================================================

@pytest.fixture(scope="module")
def q1_figure():
    plt.close("all")
    module = load_module("q1_3dplot.py")
    fig = module.create_3d_plots()
    assert fig is not None, (
        "create_3d_plots() should return the Figure object (see the provided `return fig` line)"
    )
    yield fig
    plt.close("all")


def test_q1_has_two_subplots(q1_figure):
    assert len(q1_figure.axes) == 2, (
        f"expected exactly 2 subplots side by side, found {len(q1_figure.axes)}"
    )


def test_q1_left_plot_is_a_3d_surface_using_viridis(q1_figure):
    assert len(q1_figure.axes) >= 1, "no subplots found -- can't check the left one"
    ax1 = q1_figure.axes[0]
    assert ax1.name == "3d", "the left subplot should be 3D (projection='3d')"
    assert ax1.collections, "nothing was drawn on the left subplot -- did you call ax.plot_surface(...)?"
    surface = ax1.collections[0]
    assert "Poly3DCollection" in type(surface).__name__, (
        "the left subplot should be a surface plot (ax.plot_surface), not a wireframe"
    )
    assert surface.cmap.name == "viridis", f"expected the 'viridis' colormap, got '{surface.cmap.name}'"


def test_q1_right_plot_is_a_3d_wireframe_and_blue(q1_figure):
    assert len(q1_figure.axes) >= 2, "fewer than 2 subplots found -- can't check the right one"
    ax2 = q1_figure.axes[1]
    assert ax2.name == "3d", "the right subplot should be 3D (projection='3d')"
    assert ax2.collections, "nothing was drawn on the right subplot -- did you call ax.plot_wireframe(...)?"
    wireframe = ax2.collections[0]
    assert "Line3DCollection" in type(wireframe).__name__, (
        "the right subplot should be a wireframe plot (ax.plot_wireframe), not a surface"
    )
    color = np.asarray(wireframe.get_color()).reshape(-1)
    if color.dtype.kind in ("U", "S", "O"):
        assert "blue" in str(color[0]).lower(), f"expected blue, got '{color[0]}'"
    else:
        assert np.allclose(color[:3], [0, 0, 1]), f"expected blue (R=0, G=0, B=1), got {color}"


# ===========================================================================
# Question 2 -- q2_geovis.py (choropleth map, Plotly)
# ===========================================================================

@pytest.fixture(scope="module")
def q2_module():
    return load_module("q2_geovis.py")
 
 
def _get_colorscale(fig):
    """Get the continuous colorscale actually applied to fig. Plotly Express
    puts it on the shared color axis (fig.layout.coloraxis.colorscale) by
    default for a continuous `color` column; fall back to the trace's own
    .colorscale in case it ended up there instead."""
    coloraxis_scale = getattr(getattr(fig.layout, "coloraxis", None), "colorscale", None)
    if coloraxis_scale:
        return coloraxis_scale
    return fig.data[0].colorscale
 
 
def _colorscale_colors(colorscale):
    """A plotly colorscale is a sequence of (position, color) pairs -- pull
    out just the color values, in order."""
    return [color for _position, color in colorscale]
 
def test_q2_colors_by_lifeexp(q2_module):
    assert hasattr(q2_module, "q2_fig"), "expected a variable named q2_fig holding the choropleth figure"
    assert hasattr(q2_module, "df_2007"), "expected a variable named df_2007 with the 2007 gapminder rows"
    actual = np.asarray(q2_module.q2_fig.data[0].z, dtype=float)
    expected = q2_module.df_2007["lifeExp"].to_numpy(dtype=float)
    assert actual.shape == expected.shape and np.allclose(actual, expected), (
        "the map's colors should come from the lifeExp column (pass color=\"lifeExp\")"
    )


def test_q2_uses_blues_r_color_scale(q2_module):
    colorscale = _get_colorscale(q2_module.q2_fig)
    assert colorscale is not None, "no continuous color scale found on the figure"
    actual_colors = _colorscale_colors(colorscale)
    expected_colors = list(px.colors.sequential.Blues_r)
    assert actual_colors == expected_colors, (
        f"expected color_continuous_scale=px.colors.sequential.Blues_r\n"
        f"  {expected_colors}\n"
        f"got:\n  {actual_colors}"
    )

def test_q2_title_is_correct(q2_module):
    assert q2_module.q2_fig.layout.title.text == "2007 Life Expectancy"


# ===========================================================================
# Question 3 -- q3_streamlit.py (Streamlit dashboard)
# ===========================================================================
# Uses Streamlit's own testing framework (streamlit.testing.v1.AppTest) to
# run the app headlessly and inspect the widgets/elements it produced --
# no `streamlit run` or browser needed.

from streamlit.testing.v1 import AppTest


@pytest.fixture(scope="module")
def q3_app():
    at = AppTest.from_file(str(HERE / "q3_streamlit.py"))
    at.run(timeout=30)
    if at.exception:
        messages = "\n".join(str(e) for e in at.exception)
        pytest.fail(
            f"q3_streamlit.py raised an error while running -- make sure every "
            f"TODO is completed.\n{messages}"
        )
    return at


def test_q3_has_at_least_two_multiselect_widgets(q3_app):
    assert len(q3_app.multiselect) >= 2, (
        f"expected at least 2 st.multiselect(...) widgets (e.g. airline and "
        f"destination country), found {len(q3_app.multiselect)}"
    )


def test_q3_displays_a_dataframe(q3_app):
    assert len(q3_app.dataframe) >= 1, "expected the filtered flights to be shown with st.dataframe(...)"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
