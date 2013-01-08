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
"
@author: Mikko Harju
@version: 0.1
"""
#!/usr/bin/python

import sys
import yaml
import os
import os.path
import logging
from optparse import OptionParser

from django.template import Template, Context
from datetime import datetime

GENERATOR_DATA = { 'date': datetime.now() }


class GenerationException(Exception):
    def __init__(self, errors):
        self.errors = errors
    
class Generator(object):
    def __init__(self, *args, **kwargs):
        self.createdir = kwargs['createdir']
        self.errors = []

        if kwargs['outputdir'] is None:
            self.output_directory = os.path.join(os.getcwd(), 'build')

        if kwargs['createdir'] is None:
            self.createdir = True
    
        self.output_directory = os.path.abspath(self.output_directory)

    def render_template(self, template, data):
        """Processes a single template file, providing it the data given in the
        YAML file."""
        try:
            if not os.path.exists(template):
                  raise IOError("Specified template %s was not found!" % (template,))

            template_stream = open(template)
            content = template_stream.read()

            t = Template(content)
            c = Context(data)

            rendered_content = t.render(c)

            return rendered_content 
        finally:
            try:
                template_stream.close()
            except: pass

    def write_to_file(self, rendered_content, out_file):
        """Writes the given rendered content to the output file."""
        try:
            rendered_output = open(out_file, 'w')
            rendered_output.write( rendered_content )
        finally:
            try:
                rendered_output.close()
            except: pass

    def generate_template(self, template_dir, template, data):
        """Renders a single template and writes it to a file. A directory will
        be created for the file, if the C{self.createdir} is set to C{True}"""
        rendered_content = self.render_template(os.path.join(os.path.abspath(template_dir), template), data)
        
        dirpart, filepart = os.path.split(template)
        out_file = os.path.join(self.output_directory, template)
        if self.createdir and not os.path.exists(os.path.join(self.output_directory, dirpart)):
            os.makedirs( os.path.join(self.output_directory, dirpart) )
        
        self.write_to_file(rendered_content, out_file)

    def generate_inputfile(self, input):
        stream = open(input)
        (info, data) = yaml.load_all(stream)
        stream.close()

        data.update(GENERATOR_DATA)

        try:
            dirpart, _ = os.path.split(input)
            for template in info['templates']:
                self.generate_template(dirpart, template, data)
        except Exception, e:
            self.errors.append((template, e))
        
    def generate(self, input_files):
        """Enumerates the list of input files given as parameter and produces the
        output it specifies."""
        self.errors = []

        logging.debug("Using %s as the output directory" % (self.output_directory,))
        for input in input_files:
            logging.debug("Processing input file %s" % (input,))
            try:
                self.generate_inputfile(input)
            except Exception, e:
                self.errors.append((input, e))

        if len(self.errors) > 0:
            raise GenerationException(self.errors) 

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
    from django.conf import settings
    settings.configure(DEBUG=True, TEMPLATE_DEBUG=True, INSTALLED_APPS = ['filters',])

    import filters

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
