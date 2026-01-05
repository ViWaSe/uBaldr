version = [3,1,3]

import os
import time

def _timestamp():
    tm = time.localtime()
    return f"{tm[0]}-{tm[1]:02d}-{tm[2]:02d}|{tm[3]:02d}:{tm[4]:02d}:{tm[5]:02d}"

class Create:

    def __init__(
            self,
            file_name,
            dir,
            max_size=4096,
    ):
        
        """
        Parameters:
            file_name (str): Name of the Logfile without extension: 'name' -> 'name.log'
            dir (str): Location of the Logfile
            max_size (int): Max size of the Logfile. Content will be deleted when this size is reached.

        Methods:
        --------
            log(level, event): Logs an event to the logfile.
            get_log(filepath): Returns the content of a file.
            check_and_clear(): Checks the filesize and clears the logfile if max_size is exceeded.
        """

        self.file = str(f'{file_name}.log')
        self.dir = dir
        self.max_size = max_size
        self.filepath = str(f'{self.dir}/{self.file}')

        try:
            with open(self.filepath, 'r'):
                pass
        except OSError:
            with open(self.filepath, 'w') as f:
                f.write(f'***   LOGGER V{str(version)} | File={str(self.filepath)}   ***')

    def log(self, level, event):
        """
        Parameters:
            level(str): I=Info, E=Error, W=Warning, F=Fatal, N=N/A or unknown
            event(str): The issue that is logged
        """

        LOG_LEVEL = {
        'I': '[  INFO  ]',
        'E': '[  ERROR ]',
        'W': '[  WARN  ]',
        'F': '[  FATAL ]',
        'N': '[  N/A   ]'
    }
        self.check_and_clear()
        loglevel = LOG_LEVEL.get(level)

        with open(self.filepath, 'a') as file:
            file.write(f'\n{_timestamp} >>> {loglevel}: {str(event)}')
    
    def check_and_clear(self):
        global version

        size = os.stat(self.filepath)[6]
        if size > self.max_size:
            with open(self.filepath, 'w') as f:
                f.write(f'***   LOGGER V{str(version)} | File={str(self.filepath)}   ***')
    
    def get_log(self, filepath):
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            return content
        except OSError as e:
            return f'Extraction of logs failed! - {e}'

class DummyLogger:
    def log(self, *args, **kwargs):
        return None
"""
Example of usage:
test = logger.Create('test', '/log/')
test.log('I', 'This is a Test!')
"""
