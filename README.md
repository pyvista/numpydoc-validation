### Numpydoc Validation 

This simple module allows you to generate a numpydoc validation report of all
public method and class docstrings for a given module.

This package uses [Numpydoc
Validation](https://numpydoc.readthedocs.io/en/latest/validation.html).


### Why?

The idea for this package came from being unable to run validation checks outside of the sphinx documentation build process. While you can run it for individual methods:

```py
>>> from numpydoc.validate import validate
>>> vdict = validate("numpy.sum")
>>> vdict["errors"]
```

this doesn't scale well to full modules. Hence, this package.


### Installation

```
pip install numpydoc-validate
```


### Basic Usage

```
>>> import numpydoc_validation
>>> n_invalid, report = numpydoc_validation.validate_recursive("numpy")
>>> n_invalid
436
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
```

### Advanced Usage

```py
Recursively check all the docstrings of the ``numpy`` module but only check
for ``"SS01"``, no summary found.  Also, exclude ``numpy.ndarray``.

>>> import numpydoc_validation
>>> n_invalid, report = numpydoc_validation.validate_recursive(
...     "numpy", checks={"SS01"}, exclude={r"\.ndarray$"}
... )
>>> print(report)
Numpydoc validation warnings for 'numpy.core._multiarray_umath._fastCopyAndTranspose':
  SS01: No summary found (a short summary in a single line should be
        present at the beginning of the docstring)

```

Here is a full example taken from [pyvista](https://github.com/pyvista/pyvista)

```py

# numpydoc validation checks
checks = {
    "all",  # all but the following:
    "GL01",  # Contradicts numpydoc examples
    "GL02",  # Permit a blank line after the end of our docstring
    "GL03",  # Considering enforcing
    "SA01",  # Not all docstrings need a see also
    "SA04",  # See also section does not need descriptions
    "SS05",  # Appears to be broken.
    "ES01",  # Not all docstrings need an extend summary.
    "EX01",  # Examples: Will eventually enforce
    "YD01",  # Yields: No plan to enforce
}

# numpydoc exclude
exclude = {  # set of regex
    r'\.Plotter$',  # Issue with class parameter documentation

    r'\.from_dict$',
    r'\.__init__$',

    # parm of abstract classes
    r'\.CompositeFilters$',
    r'\.PolyDataFilters$',
    r'\.CompositeFilters$',
    r'\.PolyDataFilters$',
    r'\.UniformGridFilters$',
    r'\.DataSetFilters$',
    r'\.UnstructuredGridFilters$',
    r'\.MultiBlock$',
    r'\.DataSet$',
    r'\.DataSetFilters$',
    r'\.PolyDataFilters$',
    r'\.UnstructuredGridFilters$',
    r'\.UniformGridFilters$',
    r'\.CompositeFilters$',
    r'\.Grid$',
    r'\.RectilinearGrid$',
    r'\.UniformGrid$',
    r'\.DataObject$',
    r'\.Table.save$',
    r'\.Table$',
    r'\.Table.save$',
    r'\.UnstructuredGrid$',
    r'\.ExplicitStructuredGrid$',
    r'\.StructuredGrid$',
    r'\.PointGrid$',

    # classes inherit from BaseReader
    r'\.*Reader$',
    r'\.*Reader\.*',

    # internal
    r'\.Renderer$',

    # deprecated
    r'\.*boolean_add$',
    r'\.*boolean_cut$',
    r'\.*add_field_array$',
    r'\.*add_field_array$',

    # methods we probably should make private
    r'\.store_click_position$',
    r'\.store_mouse_position$',
    r'\.*fly_to_mouse_position$',
    r'\.*key_press_event$',
    r'\.*left_button_down$',

    # MISC
    r'\.*PlotterITK$',
    r'\.*MultiBlock.copy_meta_from$',
    r'\.DataObject.copy_meta_from$',

    # wraps
    r'\.*Plotter.enable_depth_peeling$',
    r'\.*add_scalar_bar$',

    # pending refactor
    r'\.*MultiBlock.next$',

    # called from inherited
    r'\.*Table.copy_meta_from$',

}

>>> import numpydoc_validate
>>> warnings = numpydoc_validate.validate_recursive(
        "numpy", checks, exclude
    )

```
