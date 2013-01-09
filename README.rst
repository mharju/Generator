========================================================================
Generator - A YAML / Django Templates based text file generation tool.
========================================================================

Overview
--------

This project was initiated as I realized that I needed to have some kind of
simple code generation tool to use with our projects. I know there are lots of
tools out there, but after taking a short look of what's available I thought it
would be better to just use a few hours to make one myself.

Usage
-----

Run ``python setup.py install``

Create a new directory to host your YAML files and templates.

Optionally, create a directory ``filters`` to enable custom django filters to be applied. They are imported from the
register you provide (as in Django in general). See the example for clarification.

To convert the given template file, run 

``generator [options] inputfiles``

if you need help, type

``generator --help``

For a more verbose example, go check the example in the ``examples`` directory.
to test it, just run

``cd example; generator -o test task.yml``

It creates a new directory test that contains the evaluated files.

Contact
-------

If you have questions, please contact me at ``mikko (at) taiste.fi``
