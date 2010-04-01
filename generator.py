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
    
    # We have no options for now :)
    return parser

def generate_inputs(input_files, output_directory):
    """Enumerates the list of input files given as parameter and produces the
    output it specifies.

    @type input_files: list
    @param input_files: The input files that are processed. The input file is
    expected to be a valid YAML document with the format specified in the
    generator documentation, L{generator}.
    @type output_directory: string
    @param output_direstory: The output directory to be used to output the
    result. The directories are created by the script, and they should not
    exist beforehand.
    """
    errors = []
    if output_directory is None:
        output_directory = os.getcwd()

    print "Using %s as the output directory" % (output_directory,)
    for input in input_files:
        print "Processing input file %s" % (input,)
        try:
            stream = open(input)
            (info, data) = yaml.load_all(stream)
            data.update(GENERATOR_DATA)

            for template in info['templates']:
                try:
                    if not os.path.exists(template):
                        raise IOError("Specified template %s was not found!" % (template,))
            
                    template_stream = open(template)
                    content = template_stream.read()

                    t = Template(content)
                    c = Context(data)
                    rendered_content = t.render(c)
                    
                    dirpart, filepart = os.path.split(template)
                    out_file = os.path.join(output_directory, template)
                    
                    os.makedirs( os.path.join(output_directory, dirpart) )
                    rendered_output = open(out_file, 'w')
                    rendered_output.write( rendered_content )
                finally:
                    try:
                        template_stream.close()
                        rendered_output.close()
                    except: pass

        except Exception, e:
            print "\tError: %s" % (' '.join(str(e).strip('\t').split('\n')))
            errors.append(e)
        finally:
            stream.close()

    return errors

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
        errors = generate_inputs(args, options.outputdir)
        if len(errors) > 0:
            print "There were %d errors." % (len(errors),)
    except Exception, e:
        print "Error: %s" % str(e)
    
if __name__ == '__main__':
    main()  
