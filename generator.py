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
@version: 0.1
"""
#!/usr/bin/python

import sys
import yaml
import os
import os.path
from optparse import OptionParser

from django.template import Template, Context
from datetime import datetime

GENERATOR_DATA = { 'date': datetime.now() }

class GenerationException(Exception):
    def __init__(self, errors):
        self.errors = errors
    
def init_parser():
    """Initializes the parser that is responsible for interpreting the input
    parameters for the application.
    
    @return: The parser instance that has been instantiated to contain the
    necessary options.
    """
    usage = "%prog [options] inputfiles"
    parser = OptionParser(usage=usage)
    parser.add_option('-o', '--ouput-dir', action="store", type="string", dest="outputdir", help="""Output the
data to the directory given as parameter. If the parameter is omitted,
the data is output to the current working directory""")
    parser.add_option('-d', '--create-dir', action="store_true", dest="createdir",
            help="""Creates the output directories if they do not exist.""")
    return parser

def render_template(template, data):
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

def write_to_file(rendered_content, out_file):
    """Writes the given rendered content to the output file."""
    try:
        rendered_output = open(out_file, 'w')
        rendered_output.write( rendered_content )
    finally:
        try:
            rendered_output.close()
        except: pass

def generate_inputs(input_files, *args, **kwargs):
    """Enumerates the list of input files given as parameter and produces the
    output it specifies."""
    errors = []
    output_directory = kwargs['outputdir']
    createdir = kwargs['createdir']
    
    if kwargs['outputdir'] is None:
        output_directory = os.getcwd()

    if kwargs['createdir'] is None:
        createdir = False 

    print "Using %s as the output directory" % (output_directory,)
    for input in input_files:
        print "Processing input file %s" % (input,)
        try:
            stream = open(input)
            (info, data) = yaml.load_all(stream)
            data.update(GENERATOR_DATA)

            for template in info['templates']:
                try:
                    rendered_content = render_template(template, data)
                    
                    dirpart, filepart = os.path.split(template)
                    out_file = os.path.join(output_directory, template)
                    if createdir:
                        os.makedirs( os.path.join(output_directory, dirpart) )
                    
                    write_to_file(rendered_content, out_file)
                except Exception, e:
                    errors.append((template,e))

        except Exception, e:
            errors.append((input, e))
        finally:
            stream.close()

    if len(errors) > 0:
        raise GenerationException(errors) 

def main():
    """Main entry point for the script. This invokes the generator with the
    given parameters."""
    # Initialize empty django environment
    from django.conf import settings
    settings.configure(DEBUG=True, TEMPLATE_DEBUG=True)

    parser = init_parser()
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        sys.exit(-1)

    try:
        generate_inputs(args, createdir=options.createdir, outputdir=options.outputdir)
    except GenerationException, e:
        for file, error in e.errors:
            print "\tError processing %s: %s" % (file, ' '.join(str(error).strip('\t').split('\n')))
    except Exception, e:
        print "Error: %s" % str(e)
    
if __name__ == '__main__':
    main()  
