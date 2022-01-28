import pytest
import numpydoc_validation


def test_validate_recursive():
    with pytest.raises(TypeError):
        numpydoc_validation.validate_recursive(numpydoc_validation)

    with pytest.raises(ValueError):
        numpydoc_validation.validate_recursive("numpydoc_validation", checks={"123"})

    n_bad, out = numpydoc_validation.validate_recursive("numpydoc_validation")
    assert n_bad == 1
    assert "There were 1 invalid docstring(s) out of 1" in out

    n_bad, out = numpydoc_validation.validate_recursive(
        "numpydoc_validation", exclude="validate_recursive"
    )
    assert n_bad == 0
    assert "There were 0 invalid docstring(s) out of 0" in out

    n_bad, out = numpydoc_validation.validate_recursive("numpydoc_validation._")
    assert n_bad == 3
    assert "There were 3 invalid docstring(s) out of 3 tested docstring(s)" in out
