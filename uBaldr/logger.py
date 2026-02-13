version = [3,3,1]

import os
import time

class Create:

    def __init__(
            self,
            file_name,
            dir,
            max_size=4096,
            max_files=3,
            loglevel='0'
    ):
        
        """
        Parameters:
            file_name (str): Name of the Logfile without extension: 'name' -> 'name.log'
            dir (str): Location of the Logfile
            max_size (int): Max size of the Logfile. Content will be deleted when this size is reached.
            max_files (int): Number of rotated files to keep
            loglevel (int): 0=F/E, 1=F/E/W, 2=F/E/W/I

        Methods:
        --------
            log(level, event): Logs an event to the logfile.
            get_log(filepath): Returns the content of a file.
            check_and_clear(): Checks the filesize and clears the logfile if max_size is exceeded.
        """

        self.file_name = file_name
        self.dir = dir.rstrip('/')
        self.max_size = max_size
        self.max_files = max_files
        self.loglevel = loglevel

        self.file = f'{file_name}.log'
        self.filepath = str(f'{self.dir}/{self.file}')

        self._ensure_file()

    # --------------------------------------------------------------------------------------------------

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
        event_level = LOG_LEVEL.get(level)

        if self.loglevel == 0:
            if level == 'E' or level == 'F':
                with open(self.filepath, 'a') as file:
                    file.write(f'\n{self._timestamp()} >>> {event_level}: {str(event)}')
            else: pass
        elif self.loglevel == 1:
            if level == 'E' or level == 'F' or level == 'W':
                with open(self.filepath, 'a') as file:
                    file.write(f'\n{self._timestamp()} >>> {event_level}: {str(event)}')
            else: pass
        elif self.loglevel == 2:
            with open(self.filepath, 'a') as file:
                file.write(f'\n{self._timestamp()} >>> {event_level}: {str(event)}')

        self._rotate()

    # internals-----------------------------------------------------------------------------------------
    
    def _ensure_file(self):
        try:
            os.stat(self.filepath)
        except OSError:
            with open(self.filepath, 'w') as f:
                f.write(f"*** LOGGER V{version} | {self.filepath} ***")
    
    def _rotate(self):
        try:
            size = os.stat(self.filepath)[6]
        except OSError:
            return
        
        if size < self.max_size:
            return
        
        # delete oldest
        oldest = f'{self.filepath}.{self.max_files}'
        try:
            os.remove(oldest)
        except OSError:
            pass
        
        # shift files
        for i in range(self.max_files -1, 0, -1):
            src = f'{self.filepath}.{i}'
            dst = f'{self.filepath}.{i + 1}'
            try:
                os.rename(src, dst)
            except OSError:
                pass

        # rotate current
        try: 
            os.rename(self.filepath, f'{self.filepath}.1')
        except OSError:
            pass

        # create new base file
        with open(self.filepath, 'w') as f:
            f.write(f'*** LOGGER V{version} | {self.filepath} ***')

# TODO: return the wanted logfile or merge all
    def get_log(self, filepath):
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            return content
        except OSError as e:
            return f'Extraction of logs failed! - {e}'
    
    def _timestamp(self):
        tm = time.localtime()
        return f"{tm[0]}-{tm[1]:02d}-{tm[2]:02d}|{tm[3]:02d}:{tm[4]:02d}:{tm[5]:02d}"

class DummyLogger:
    def log(self, *args, **kwargs):
        return None
"""
Example of usage:
test = logger.Create('test', '/log/')
test.log('I', 'This is a Test!')
"""
