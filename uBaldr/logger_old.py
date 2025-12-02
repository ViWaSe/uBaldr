# Logger for Issues in the Baldr-Software

version = [2,1,0]

import NTP
import os

# Check size of the logfole. If it reaches 'max_size', delete the content
def check_and_clear_log(log_file, max_size):
    global version
    
    try:
        size = os.stat(log_file)[6] 
        if size > max_size:
            with open(log_file, 'w') as f:
                f.write(f'***   LOGGER V{str(version)} | File={str(log_file)}.log   ***')
    except OSError:
        with open(log_file, 'w') as f:
                f.write(f'***   LOGGER V{str(version)} | File={str(log_file)}.log   ***')
        
# Log-function. can be imported and used in all other programs
def Log(
        sub='Pico',
        level='N', 
        issue=None,
        dir='/log/',
        max_size=4096
        ):
    
    """
    Logging module to create logfles and log events

    Parameters:
        sub (str): Sender or Subsystem and Specifies the name of the logfile (e.g. 'MQTT' -> MQTT.log).
        level (str): Loglevel. I=INFO, E=Error, W=WARN, F=FATAL, N=N/A
        issue (str): The actual Message or issue.
        dir (str): The location of the logfile (e.g. '/log/'). The '/' must be present.
        max_size (int): Maximum size of the file. If max size is reached, the content is deleted.
    """
    
    LOG_LEVEL = {
    'I': '[  INFO  ]',
    'E': '[  ERROR ]',
    'W': '[  WARN  ]',
    'F': '[  FATAL ]',
    'N': '[  N/A   ]'
}

    # Check and / or clear logfile
    check_and_clear_log(log_file=f'{sub}.log', max_size=max_size)

    sub_file = dir + sub + '.log'
    time = NTP.timestamp()
    loglevel = LOG_LEVEL.get(level)

    try:
        with open(sub_file, 'a') as file:
            file.write(f'{str(time)} >>> {loglevel}: {str(issue)} \n')
    except FileNotFoundError:
        with open(sub_file, 'w') as file:
            file.write(f'***   LOGGER V{str(version)} | File={str(sub)}.log   *** \n {str(time)} >>> {loglevel}: {str(issue)} \n')

# return logfile content 
def get_log(sub, dir='/log'):
    try:
        with open(f'/{dir}/{sub}.log', 'r') as f:
            content = f.read()
        return content
    except OSError as e:
        return f'Extraction of logs failed! - {e}'