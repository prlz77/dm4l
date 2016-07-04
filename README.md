```
             ______ ___  ___   ___  _     
             |  _  \|  \/  |  /   || |    
   /__/\__\  | | | || .  . | / /| || |     /__/\__\ 
  (`-/__\-') | | | || |\/| |/ /_| || |    (`-/__\-')
   \/,'`.\/  | |/ / | |  | |\___  || |____ \/,'`.\/
             |___/  \_|  |_/    |_/\_____/
```
Dark magic for machine learning log files.

## Usage

```
usage: main.py [-h] [--logs LOGS [LOGS ...]]
               [--backends BACKEND1 [ BACKEND2 BACKEND3 ...]]
               [--from_file FROM_FILE] [--safe] [--silent] [--refresh REFRESH]
               {max,plot,report} ...

~ Dark Magic 4 Logs ~

positional arguments:
  {max,plot,report}

optional arguments:
  -h, --help            show this help message and exit
  --logs LOGS [LOGS ...]
                        [list] of log file[s]. Overrides file reading
  --backends [BACKEND1 [ BACKEND2 BACKEND3 ...]]
                        The respective backend for each log[s]
  --from_file FROM_FILE
                        Reads: log_path<space>backend[<space>id[<space>pid]]\n... from "from_file"
  --safe                Ignore erroneous logs
  --silent              Do not show warnings
  --refresh REFRESH     Seconds to refresh data. 0 = run once, >0 for "real-time" monitoring.
```
