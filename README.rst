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

To convert the given template file, run 

``python generator.py [options] inputfiles``

if you need help, type

``python generator.py --help``

For a more verbose example, go check the example in the ``examples`` directory.
to test it, just run

``python generator.py -d -o test example/task.yml``

It creates a new directory test that contains the evaluated files.

Contact
-------

If you have questions, please contact me at ``mikko (at) taiste.fi``
