import yaml
import os
import os.path
import logging

from django.template import Template, Context
from datetime import datetime

GENERATOR_DATA = { 'date': datetime.now() }
TEMPLATE_DIR = os.path.join(os.getcwd(), 'templates')

class GenerationException(Exception):
    def __init__(self, errors):
        self.errors = errors
    
class Generator(object):
    def __init__(self, *args, **kwargs):
        self.createdir = kwargs['createdir']
        self.errors = []

        self.output_directory = os.path.abspath(kwargs.get('outputdir', os.path.join(os.getcwd(), 'build')))
        self.createdir = kwargs.get('createdir', True)
    
    def render_template(self, template, data):
        """Processes a single template file, providing it the data given in the
        YAML file."""
        try:
            template_file_name = os.path.join(TEMPLATE_DIR, template)
            if not os.path.exists(template_file_name):
                  raise IOError("Specified template %s was not found!" % (template_file_name,))

            template_stream = open(template_file_name)
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
        rendered_content = self.render_template(template, data)
        
        dirpart, filepart = os.path.split(template)
        out_file = os.path.join(self.output_directory, template)
        if self.createdir and not os.path.exists(os.path.join(self.output_directory, dirpart)):
            os.makedirs( os.path.join(self.output_directory, dirpart) )
        
        self.write_to_file(rendered_content, out_file)

    def generate_inputfile(self, input):
        (info, data) = yaml.load_all(input)
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

