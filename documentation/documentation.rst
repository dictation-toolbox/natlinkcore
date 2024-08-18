
Documentation
==============================================================================

The documentation for Natlink is written in `reStructuredText format`_.
ReStructuredText is similar to the Markdown format. If you are unfamiliar
with the format, the `reStructuredText primer`_ might be a good starting
point.

The `Sphinx documentation engine`_ and `Read the Docs`_ are used to
generate documentation from the *.rst* files in the *documentation/* folder.
Docstrings in the source code are included in a semi-automatic way through use
of the `sphinx.ext.autodoc`_ extension.

To build the documentation locally, install Sphinx and any other documentation
requirements:

.. code:: shell

   $ cd documentation
   $ pip install -r requirements.txt

Then run the following command on Windows to build the documentation:

.. code:: shell

   $ make html



If there were no errors during the build process, open the
*_build/html/index.html* file in a web browser. Make changes, rebuild the
documentation and reload the doc page(s) in your browser as you go.


Python versions
--------------------------
Note that Natlink is running on a 32 bits python version.

It appears that Sphinx is not running on a 32 bits python version. So the documentation must be compiled on another (64bit) python version than you are running Natlink on!





.. Links.
.. _Read the docs: https://readthedocs.org/
.. _Sphinx documentation engine: https://www.sphinx-doc.org/en/master/
.. _reStructuredText format: http://docutils.sourceforge.net/rst.html
.. _restructuredText primer: http://docutils.sourceforge.net/docs/user/rst/quickstart.html
.. _sphinx.ext.autodoc: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

