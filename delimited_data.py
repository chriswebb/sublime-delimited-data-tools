# The MIT License (MIT)

# Copyright (c) 2016 Chris Webb

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from sublime import set_timeout
from .config import ConfigBaseTextCommand, set_status
from threading import Thread
from io import StringIO


class CSVStreamReader:

    delimiter = '\t'
    textfieldIdentifier = '"'

    def __init__(self, delimiter, textfieldIdentifier):
        self.delimiter = delimiter
        self.textfieldIdentifier = textfieldIdentifier

    def getTotalColumns(self, delimiter, textfieldIdentifier, stream, enc):

        curPosition = 0
        if stream.seekable():
            curPosition = stream.tell()
        else:
            return False

        textfieldDelimiterCount = 0
        columnCount = 0
        curChar = stream.read(1)

        while curChar != 0:
            
            if curChar == textfieldIdentifier:
                textfieldDelimiterCount += 1
            elif (textfieldDelimiterCount == 0) or (textfieldDelimiterCount % 2 == 0):
                if curChar == delimiter:
                    columnCount += 1
                elif curChar == '\n':
                    break
            curChar = stream.read(1)

        columnCount += 1
        if stream.seekable():
            stream.seek(curPosition)
        return columnCount

    def readLine (self, stream, startPosition):

        if not startPosition:
            startPosition = 0
        if startPosition >= stream.length:
            return None

        textfieldDelimiterCount = 0
        record = []
        curChar = None
        column = 0
        output = []
        endPosition = startPosition
        curChar = stream.read(1)


        while curChar != 0:
            endPosition += 1

            if curChar == textfieldIdentifier:
                if lastChar == curChar:
                    record.append(curChar)
                textfieldDelimiterCount += 1
                continue

            elif (textfieldDelimiterCount == 0) or (textfieldDelimiterCount % 2 == 0):
                if curChar == delimiter:
                    curColumn = column
                    output.push(record.join(""))
                    column += 1
                    record = []
                    continue

                elif curChar == '\r':
                    continue
                elif curChar == '\n':
                    break
            record.push(curChar)
            lastChar = curChar
            curChar = stream.read(1)

        output.push(record.join(""))
        return { "output": output, "endPosition": endPosition }

    def readLines(self, stream):

        pos = 0
        output = []
        returnObj = self.readLine(input, pos)

        while returnObj:
            pos = returnObj.endPosition + 1
            output.push(returnObj.output)

        return output

class FormatDelimitedDataCommand(ConfigBaseTextCommand):  
    def description(self):
        return 'Parses delimited text data directly from the editor'

    def run(self, edit, *args, **kwargs):  
        self.edit = edit
        kwargs['window'] = self.window
        self.settings = kwargs
        self.encoding = self.view.encoding()
        if self.encoding == 'Undefined':
            self.encoding = 'UTF-8'

        self.delimiter = None
        if 'textfieldIdentifier' in self.settings:
            self.textfieldIdentifier = self.settings['textfieldIdentifier']

        if 'delimiter' in self.settings:
            self.delimiter = self.settings['delimiter']
        else:
            self.window.show_input_panel('Enter delimiter:', '', self.__run_with_delimiter, None, None)
            return
        self.__run_with_delimiter(delimiter)

    def __run_with_delimiter(self, delimiter):

        if not self.is_output_to_newfile():
            self.output_panel = self.window.create_output_panel('delimited_format')
            self.output_panel.set_scratch(True)
            self.output_panel.run_command('erase_view')
            self.output_panel.set_encoding(self.encoding)

        self.set_status('Parsing delimited data...')
        thread_infos = []
        thread_num = 0

        if 'files' in self.settings:
            for fileobj in self.settings['files']:  
                if isfile(fileobj):
                    thread_num += 1
                    thread = self.__ParseDelimitedData(self, file=fileobj)
                    thread_infos.append({'thread': thread, 'file': fileobj})

        else:
            noSelections = True
            for sel in self.view.sel():  
                if not sel.empty():
                    thread_num += 1
                    noSelections = False
                    # Get the selected text  
                    data = self.view.substr(sel)
                    thread = self.__ParseDelimitedData(self, data=data)
                    thread_infos.append({"thread": thread, "thread_num": thread_num})

            if noSelections:
                thread_num += 1
                # Get all the text  
                data = self.view.substr(Region(0, self.view.size()))
                thread = self.__ParseDelimitedData(self, data=data)
                thread_infos.append({"thread": thread, "thread_num": thread_num})

        for thread_info in thread_infos:
            thread_info['start_time'] = time()
            thread_info['thread'].start()

        self.__DelimitedDataHandleParsing.execute(thread_infos, thread_num)

    class __DelimitedDataHandleParsing(Thread):
        def __init__(self, thread_infos, thread_total):
            self.thread_infos = thread_infos
            self.thread_total = thread_total
            Thread.__init__(self)

        def run(self):
            new_thread_infos = []
            for thread_info in self.thread_infos:
                if thread_info['thread'].is_alive():
                    new_thread_infos.append(thread_info)
                    continue
                else:
                    completion_time = (time() - thread_info['start_time']) * 1000
                    if 'file' in thread_info:
                        dirpath, filename = split(thread_info['file'])
                        query_id = ('file ' + filename)
                    else:
                        query_id = ('data '+ thread_info['thread_num'] + '/' + self.thread_total) if thread_info['thread_num'] != 1 and self.thread_total != 1 else 'data '
                    self.set_status('Format of delimited ' + query_id + ' completed in '+ str(completion_time) +' ms.')

            if len(new_thread_infos) > 0:
                self.execute(new_thread_infos, self.thread_total)

        @classmethod
        def execute(cls, thread_infos, thread_total):
            thread = cls(thread_infos, thread_total)
            thread.start()

    class __ParseDelimitedData(Thread):
        def __init__(self, parent, data=None, file=None):
            self.parent = parent
            self.data = data
            self.file = file
            Thread.__init__(self)

        def __output(self, return_code, output_text):
            if self.parent.is_output_to_newfile():
                view = self.parent.window.new_file()
                view.set_scratch(True)
                view.set_encoding(self.parent.encoding)
                view.run_command('append', {'characters': output_text})
                self.parent.window.focus_view(view)
            else:
                self.parent.settings.output_lock.acquire()
                self.parent.output_panel.run_command('append', {'characters': output_text})
                self.parent.window.run_command('show_panel', {'panel': 'output.delimited_format'})
                self.parent.settings.output_lock.release()




        def run(self):
            errored = False

            try:


                CSVStreamReader(self.parent.delimiter, self.parent.textfieldIdentifier)



                cmd = [self.__get_parameter('psql_path', '/usr/bin/psql'), '--no-password'] 
                environment = environ.copy()

                for name in self.parent.settings.postgres_variables:
                    if name in self.parent.settings and self.parent.settings[name]:
                        self.__try_add_parameter_name_to_environment(environment, name, self.parent.settings.postgres_variables[name])

                client_encoding_name = self.parent.settings.postgres_variables['client_encoding']
                if client_encoding_name not in environment:
                    environment[client_encoding_name] = self.parent.encoding

                
                if (self.file): 
                    with open(self.file) as inputfile:
                        psqlprocess = Popen(cmd, stdin=inputfile, stdout=PIPE, stderr=STDOUT, env=environment)
                        stdout, stderr = psqlprocess.communicate()
                else:
                    psqlprocess = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, env=environment)
                    stdout, stderr = psqlprocess.communicate(bytes(self.query, self.parent.encoding))

                output_text = stdout.decode(self.parent.encoding)
                retcode = psqlprocess.poll()

            except BaseException as e:
                errored = True
                output_text = format_exc()
                retcode = 1


            set_timeout(lambda:self.__output(retcode, output_text), 0)
        
