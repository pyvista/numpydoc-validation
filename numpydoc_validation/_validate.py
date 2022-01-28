"""Generate a numpydoc validation report."""
import importlib
import re
from copy import deepcopy
from inspect import isclass, isroutine
from textwrap import wrap

from numpydoc.validate import ERROR_MSGS, validate


def fullname(obj):
    """Return full qualified name of an object."""
    return ".".join([obj.__module__, obj.__qualname__])


def get_obj_recursive(obj):
    """Recursively return attributes matching certain types.

    Parameters
    ----------
    obj : object
        Object to inspect recursively.

    Returns
    --------
    dict
        Dictionary contianing each method, function, or class within obj.

    """
    attrs = []
    for attr_name in dir(obj):
        # ignore private
        if attr_name.startswith("_"):
            continue
        attr = getattr(obj, attr_name)

        # construct fully qualified name
        if isroutine(attr):
            attrs.append(attr)
        if isclass(attr):
            attrs.append(attr)
            attrs.extend(get_obj_recursive(attr))

    return attrs


def get_module_obj_names(module_name):
    """Return all public object names of all classes and functions in an module."""
    mymodule = importlib.import_module(module_name)

    objs = get_obj_recursive(mymodule)
    names = set()
    for obj in objs:
        try:
            name = fullname(obj)
        except (AttributeError, TypeError):  # pragma: no cover
            continue
        if module_name in name:
            names.add(name)

    names_lst = list(names)
    names_lst.sort()
    return names_lst


def validate_name(obj_name, excluder, validation_checks):
    """Validate the docstring from a fully qualified object name.

    Parameters
    ----------
    obj_name : str
        The name of the object whose docstring will be evaluated, e.g.
        'pandas.read_csv'. The string must include the full, unabbreviated
        package/module names, i.e. 'pandas.read_csv', not 'pd.read_csv' or
        'read_csv'.

    Returns
    -------
    bool
        ``True`` When the method is tested.  ``False`` when not tested.
    str
        Empty string if docstring is valid. Otherwise, the warning message.

    """
    msg = ""
    exclude_from_validation = excluder.search(obj_name) if excluder else False
    if not exclude_from_validation:
        # TODO: Currently, all validation checks are run and only those
        # selected via config are reported. It would be more efficient to
        # only run the selected checks.
        errors = validate(obj_name)["errors"]
        if {err[0] for err in errors} & validation_checks:
            msg = f"Numpydoc validation warnings for {obj_name!r}:\n"
            for err in errors:
                if err[0] in validation_checks:
                    lines = wrap(
                        f"{err[0]}: {err[1]}\n",
                        initial_indent="  ",
                        subsequent_indent="        ",
                    )
                    msg += "\n".join(lines) + "\n"
    return not exclude_from_validation, msg


def validate_recursive(module_name, checks={"all"}, exclude=None):
    r"""Run a numpydoc validation check for all public objects in a module.

    This is a recursive module check. To check a single object, use:

    .. code:: python

       >>> from numpydoc.validate import validate
       >>> vdict = validate("numpy.sum")
       >>> vdict["errors"]

    Parameters
    ----------
    module_name : str
        Installed Python module name. For example, ``"numpy"``.
    checks : set
        Set of numpydoc validation checks. See `Build-in Validation Checks
        <https://numpydoc.readthedocs.io/en/latest/validation.html#built-in-validation-checks>`_
        for available checks. Defaults to all checks.

    Returns
    -------
    int
        Number of numpydoc docstring warnings.
    str
        Numpydoc validation report.

    Examples
    --------
    Recursively check all the docstrings of the ``numpy`` module.

    >>> import numpydoc_validation
    >>> n_invalid, report = validate_recursive("numpy")
    >>> print(report)
    ...
    Numpydoc Validation warnings for 'numpy.zeros_like':
      GL02: Closing quotes should be placed in the line after the last
            text in the docstring (do not close the quotes in the same
            line as the text, or leave a blank line between the last text
            and the quotes)
      GL03: Double line break found; please use only one blank line to
            separate sections or paragraphs, and do not leave blank lines
            at the end of docstrings
      ES01: No extended summary found
      PR05: Parameter "subok" type should not finish with "."
      PR05: Parameter "shape" type should not finish with "."
      RT02: The first line of the Returns section should contain only the
            type, unless multiple values are being returned

    Recursively check all the docstrings of the ``numpy`` module but only check
    for ``"SS01"``, no summary found.  Also, exclude ``numpy.ndarray``.

    >>> import numpydoc_validation
    >>> n_invalid, report = validate_recursive(
    ...     "numpy", checks={"SS01"}, exclude={r"\.ndarray$"}
    ... )
    >>> print(report)
    Numpydoc validation warnings for 'numpy.core._multiarray_umath._fastCopyAndTranspose':
      SS01: No summary found (a short summary in a single line should be
            present at the beginning of the docstring)

    """
    if not isinstance(module_name, str):
        raise TypeError(
            f"Expected str for ``module_name``, not {type(module_name)}"
        )
    obj_names = get_module_obj_names(module_name)

    excluder = None
    if exclude:
        excluder = re.compile(r"|".join(exp for exp in exclude))

    valid_error_codes = set(ERROR_MSGS.keys())
    if "all" in checks:
        block = deepcopy(checks)
        checks = valid_error_codes - block

    # Ensure that the validation check set contains only valid error codes
    invalid_error_codes = checks - valid_error_codes
    if invalid_error_codes:
        raise ValueError(
            f"Unrecognized validation code(s) in numpydoc_validation_checks "
            f"config value: {invalid_error_codes}"
        )

    n_tested = 0
    msgs = []
    for name in obj_names:
        tested, output = validate_name(name, excluder, checks)
        n_tested += tested
        if output:
            msgs.append(output)
    n_invalid = len(msgs)

    summary = ''.join([
        f"\nThere were {n_invalid} invalid docstring(s) "
        f"out of {n_tested} tested docstring(s).\n\n"
        f"{n_invalid - n_tested} docstrings were excluded."
    ])
    msgs.append(summary)

    return n_invalid, "\n".join(msgs)
