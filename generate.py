#!/usr/bin/env python

"""
A script that uses the django template language in conjunction with pyyaml to
generate content based on the data expressed in YAML format.

File format
===========
    The input file format is a two-part YML document that contains two parts
        1. The information used by the generator script
        2. The information that is passed to the django template files
        specified in the information in the first part.

    Please consult the example for more information.

Requirements
============
    - U{www.djangoproject.com}
    - U{www.pyyaml.org}

@author: Mikko Harju
"""

import sys
import yaml
import os
import os.path

import logging
from optparse import OptionParser

from generator import Generator, GenerationException

def init_parser():
    """Initializes the parser that is responsible for interpreting the input
    parameters for the application.
    
    @return: The parser instance that has been instantiated to contain the
    necessary options.
    """
    usage = "%prog [options] inputfiles"
    parser = OptionParser(usage=usage)
    parser.add_option('-o', '--output-dir', action="store", type="string", dest="outputdir", help="""Output the
data to the directory given as parameter. If the parameter is omitted,
the data is output to the current working directory""")
    parser.add_option('-d', '--create-dir', action="store_true", dest="createdir",
            help="""Creates the output directories if they do not exist.""")
    return parser

def main():
    """Main entry point for the script. This invokes the generator with the
    given parameters."""
    # Initialize empty django environment
    FILTERS_MODULE = 'filters'
    if os.path.exists(os.path.join(os.getcwd(), 'filters/__init__.py')):
        sys.path += [os.getcwd(),]
        __import__(FILTERS_MODULE)
        from django.template import builtins
        builtins.append(sys.modules[FILTERS_MODULE].register)

    from django.conf import settings
    settings.configure(DEBUG=True, TEMPLATE_DEBUG=True)

    logging.basicConfig(level=logging.DEBUG)

    parser = init_parser()
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        sys.exit(-1)

    try:
        Generator(createdir=options.createdir,
                outputdir=options.outputdir).generate(args)
    except GenerationException, e:
        for file, error in e.errors:
            logging.debug("Error processing %s: %s" % (file, ' '.join(str(error).strip('\t').split('\n'))))
    except Exception, e:
        logging.debug("Error: %s" % str(e))
    
if __name__ == '__main__':
    main()  

