Contribute to PyU4V
===================

Please do! Create a fork of the project into your own repository. Make all your
necessary changes and create a pull request with a description on what was 
added or removed and details explaining the changes in lines of code.

The following tests must all run cleanly:

.. code-block:: bash

    $ cd PyU4V
    $ tox -e py36
    $ tox -e py37
    $ tox -e pep8
    $ tox -e pylint

.. note::

   If you do not have all the versions of Python installed, just run tox on
   the versions you have.

Once the above tests all run clean and CI tests are run to ensure there is no
impact on existing functionality, PyU4V core reviewers will review the code
to ensure it conforms to all conventions outlined in the section below. If all
looks good we will merge it to the PyU4V master branch.

Conventions
-----------

For neatness and readability we will enforce the following conventions going
forward on all code in PyU4V.

1. Single quotes ``'`` unless double quotes ``"`` necessary.

2. Use ``.format()`` for string concatenation.

.. code-block:: text

   my_string = '{variable1}, thanks for contributing to {variable2}'.format(
       variable1=’Hello’, variable2=’PyU4V’)

3. Use the following format for doc strings, the return description uses
``:returns:`` instead of the docstring default ``:return:``.  Pep8 will
guide you with all the docstring conventions.

.. code-block:: Python

    def my_test_func(input_1, input_2):
        """The is my summary of the method with full stop.

        This is a brief description of what the method does.  Keep
        it as simple as possible.

        :param input_1: brief description of input parameter 1, if it goes over
                        one line it must be indented with the start of the
                        previous lines -- str
        :param input_2: brief description of input parameter 2, you must also
                        provide the input parameter type after the description
                        after double dash -- int
        :returns: what gets returned from method, omit if none, type must also
                  be specified, in this case it is a boolean -- bool
        :raises: Exceptions raised, omit if none
        """
        return True if input_1 or input_2 else raise Exception

5. Class names are mixed case with no underscores ``_``.

.. code-block:: Python

   class ClassFunctions(object):
       """Collection of functions ClassFunctions."""

6. Public Methods are separated by underscores ``_``.  Make the name as
meaningful as possible.

.. code-block:: Python

    def public_function_does_exactly_what_it_says_it_does(self):
        """Function does exactly what it says on the tin."""

7. Private Methods are prefixed and separated by underscores ``_``.  Make the
name as meaningful as possible.

.. code-block:: Python

    def _private_function_does_exactly_what_it_says_it_does(self):
        """Function does exactly what it says on the tin."""

8. If functions seems to big or too complicated then consider breaking them
into smaller functions.

9. If a line of code must extend over more than one line, use parenthesis
``()`` around the code instead of ``\`` at the end of the line.

.. code-block:: Python

    my_multi_line_string = ('This is an example of a string '
                            'that extends over more than one line.')

    my_multi_line_function = (
        this_is_a_very_long_function_call_that_cannot_meet_79_char_limit())

10. Each new function must be unit tested.

11. Each bug fix must be unit tested.

12. Unix and OS X format only.  If in doubt run

.. code-block:: Bash

   $ sudo apt-get install dos2unix
   $ dos2unix myfile.txt

or in PyCharm:

.. code-block:: text

   File -> Line Separators -> LF- Unix and OS X (\n)
