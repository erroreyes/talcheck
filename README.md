# TAL Check

This Python script checks for new versions of TAL (Togu Audio Line) plugins and download them if a user chooses to. 

**NOTE**: This script currently only supports the latest commercial plugins: TAL-Drum, TAL-Sampler, TAL-Bassline-101, TAL-DAC, TAL-Pha, TAL-U-NO-LX, TAL-J-8, TAL-Mod, and TAL-Dub-X.

## Requirement

Before running, make sure your Python installation has the necessary packages:

```bash
pip install dateparser urllib3
```

## Running the script

Simply run it like this:

```bash
# Check for new versions of favorite TAL plugins. At least one (1) plugin must be marked as a 
# favorite or this will print nothing.
python3 talchecker.py
```

That said, when one first runs it, nothing will happen. That's because it needs to know what TAL plugins you are interested in. To add your favorite TAL plugins:

```bash
# Favorite plugins can be configured by passing a comma-separated list
python3 talchecker.py -F 'TAL-Drum,TAL-Sampler,TAL-DAC'
```

After adding your favorite plugins, running this again
```bash
python3 talchecker.py
```
will check for new versions of these plugins.

```bash
# This will check for all plugins, whether they were marked as favorites or not
python3 talchecker.py -a

# While this will check for a specific plugin
python3 talchecker.py -p TAL-Drum

# This checks for new versions of favorite Windows plugins.
python3 talchecker.py -o win
# Use 'win', 'macos', or 'linux'

# The -o option can be combined with -a and -p, so this
python3 talchecker.py -p TAL-Drum -o macos
# will check for the MacOS version of TAL-Drum,
# while this will check for all Linux plugins
python3 talchecker.py -a -o linux

# For any of the above, use -d to download the files, i.e.
# to check and download all favorite plugins
python3 talchecker.py -d
# and to check and download TAL-Drum only
python3 talchecker.py -p TAL-Drum -d

# Note that files are only downloaded if a new version is found after a check.

# When downloading, the script will first check if there is a 
# directory in data.json, and download files there. If there isn't one, 
# the script will attempt to use a default system configured 'Downloads' directory. 

# This will download the Linux installer for TAL-Drum to '~/Downloads' if it exists, 
# which is the Linux default
python3 talchecker.py -p TAL-Drum -o linux -d 

# To add a directory to data.json
python3 talchecker.py -D '/path/to/some/download/directory/'

# After that, this
python3 talchecker.py -p TAL-Drum -o linux -d 
# will download the Linux installer for TAL-Drum to '/path/to/some/download/directory/'

# This will use the path provided just this once
python3 talchecker.py -dd '/some/other/path/to/another/download/directory/'
# and ignore any path system path, or directory in data.json

# Instead of passing the -o option to specify an OS, use -O to save that OS to 
# data.json. For example, after this
python3 talchecker.py -O macos
# these will always check for new MacOS installers for all favorites and download them (-d)
python3 talchecker.py -d

# To see the list of all TAL plugins, especially to get their names to use with this script
python3 talchecker.py -l

# To see the list of favorite plugins
python3 talchecker.py -lf
```

When the script checks for new versions for the first time, it will assume that there are versions available for all plugins. This is because there is no data stored about when a new file has been made available in the TAL server. After that first run, consequent runs will check the current date of the file in the server against the date stored in the previous run to determine if a new version is available. 

_(Note: this could probably be smarter and a lot more convenient.)_

## `data.json`

This file stores all data needed to run the script. It contains all paid plugins currently available as of 04/15/2024. A user can add additional plugins to the list by following the same format:

```json
// (Description of each field)
{
    "name": "The name of the plugin",
    "urls": {
        "win": "URL for the Windows installer",
        "macos": "URL for the MacOS installer",
        "linux": "URL for the Linux installer"
    },
    "lastModified": "The date that this plugins was last modified. Leave blank when adding a plugin; it will be populated by the script.",
    "isFavorite": "Flags a plugin as a favorite. By default, the script will only check for favorites. Values are 'true' or 'false'"
}
```

```json
// Example
{   // TAL-Pha is added, so "lastModified" is left blank. 
    "name": "TAL-Pha",
    "urls": {
        "win": "https://tal-software.com//downloads/plugins/install_TAL-Pha.zip",
        "macos": "https://tal-software.com//downloads/plugins/TAL-Pha-installer_macos.zip",
        "linux": "https://tal-software.com/downloads/plugins/TAL-Pha_64_linux.zip"
    },
    "lastModified": "",
    "isFavorite": true
},
{
    "name": "TAL-U-NO-LX",
    "urls": {
        "win": "https://tal-software.com/downloads/plugins/install_TAL-U-NO-LX-V2.zip",
        "macos": "https://tal-software.com/downloads/plugins/TAL-U-NO-LX-V2-installer_macos.zip",
        "linux": "https://tal-software.com/downloads/plugins/TAL-U-NO-LX-V2_64_linux.zip"
    },
    "lastModified": "Fri, 19 Apr 2024 08:11:50 GMT",
    "isFavorite": false
}
```

### `preferences`

* `os`: The OS to download plugins for, i.e. `win`, `macos`, or `linux`
* `downloadDir`: The directory to download plugin installers to.