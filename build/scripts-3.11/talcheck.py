#!python

import urllib.request
import requests
import json
import os
import ctypes
import dateparser
import datetime
import argparse
import re


# HTTP Header
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
}


# Cmd arguments
parser = argparse.ArgumentParser(description="Check and download new versions of your favorite Togu Audio Line (TAL) plugins.")
# Option for checking for a specified plugin
parser.add_argument("-p", "--plugin")
# Option for checking for a specified OS
parser.add_argument("-o", "--os")
# Option for using a specified download directory
parser.add_argument("-dd", "--downloaddir")
# Option to download after checking
parser.add_argument("-d", "--download", action="store_true")
# Option to download even if a new version hasn"t been found
parser.add_argument("-fd", "--forcedownload", action="store_true")
# Options to print a list of all the plugins
parser.add_argument("-l", "--list", action="store_true")
# Option for printing a list of only plugins marked as favorites
parser.add_argument("-lf", "--listfavorites", action="store_true")
# Options for checking all plugins
parser.add_argument("-a", "--all", action="store_true")
# Option for marking a comma separated list of plugins as favorites
parser.add_argument("-F", "--addfavorites")
# Option for adding an OS type to preferences
parser.add_argument("-O", "--addos")
# Option for adding a download directory to preferences
parser.add_argument("-D", "--adddownloaddir")
args = parser.parse_args()


# Path for data.json
data_path = "./data/data.json"


# The JSON data
# TODO : init this with default data from the JSON file so that in case 
#        data.json is lost, it can be recreated.
data = {}


# Reads JSON data
def read_json():
    if not os.path.exists(data_path):
        raise FileNotFoundError("data.json does not exist.")
        
    # Open and return the data
    with open(data_path, "r") as infile:
        a = infile.read()
        return json.loads(a)


# Writes JSON data
def write_json(data):
    json_o = json.dumps(data, indent = 4)

    # If not os.path.exists("./data.json"):
    with open(data_path, "w") as outfile:
        outfile.write(json_o)


# Turns the date string to a timestamp
def to_ts(date):
    parsed = dateparser.parse(date)
    return parsed.timestamp()


# Get the OS key from args, or return "win" by default
def get_os(data):
    if not args.os:
        return data["preferences"]["os"] if data["preferences"]["os"] else "win"
    return args.os


# Splits a comma separated string into a list
def get_pref_list(pref_str):
    return pref_str.split(",")


# Get the zip file name from the URL
def parse_filename(url):
    return re.search("(.*\/\/.*\/.*\/)(.*\.zip)", url).group(2)


def download_dir(data):
    # User passed directory takes priority
    if args.downloaddir:
        if not os.path.exists(args.downloaddir):
            raise FileNotFoundError(f"Directory {args.downloaddir} does not exist. Choose a different directory.")
        return args.downloaddir
    
    # Use preferences if set
    dl_dir = os.path.expanduser(data["preferences"]["downloadDir"])
    if dl_dir:
        if not os.path.exists(dl_dir):
            raise FileNotFoundError(f"Directory {dl_dir} does not exist. Choose a different directory.")
        return dl_dir
    
    # Otherwise, guess the system download directory per OS
    if os.name == "nt":
        # Define necessary constants from Shell32.dll
        # Folder ID for Downloads
        csidl_downloads = 0x00dc
        buf = ctypes.create_unicode_buffer(MAX_PATH=1024)

        # Load the Shell32 library
        windll = ctypes.windll.shell32

        # Call SHGetKnownFolderPath function to retrieve path
        result = windll.SHGetKnownFolderPath(csidl_downloads, 0, None, ctypes.byref(buf))

        # Check for success and print the path
        if result == 0:
            return buf.value
        else:
            raise Exception("No download directory found. Please add one in preferences.")
    else:
        dl_dir = os.path.expanduser("~/Downloads")
        if os.path.exists(dl_dir):
            return dl_dir
        else:
            raise FileNotFoundError("No download directory found. Please add one in preferences.")


# Downloads the installer
def download(url, dl_dir, file_name):
    # file_path = f"{os.environ["HOME"]}/Downloads/{file_name}"
    file_path = f"{dl_dir}/{file_name}"

    r = requests.get(url, stream = True)

    with open(file_path, "wb") as file:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)


def get_curr_datetime():
    now = datetime.datetime.now()

    # Define the desired format string
    format_str = "%a, %d %b %Y %H:%M:%S"

    # Format the datetime object and print
    return now.strftime(format_str)


# Perform the check and optional download
def check(data):
    # Iterate through the data
    for plug in filter(lambda x: args.all or x["isFavorite"] or args.plugin, data["plugins"]):
        # Flag to know if updates have been found
        update_found = False

        name = plug["name"]

        # Only check if a plugin has been passed as an option (-p)
        if args.plugin and not args.plugin == name:
            continue

        url = plug["urls"][get_os(data)]
        saved_last_mod = plug["lastModified"]
        req = urllib.request.Request(url, headers = HEADERS, method = "HEAD")
        res = urllib.request.urlopen(req)
        last_mod = res.getheader("Last-Modified")

        # If this is the first time a plugin is checked for updates, or an update is found, 
        # do stuff...
        if args.forcedownload or saved_last_mod == "" or to_ts(saved_last_mod) < to_ts(last_mod):
            if not update_found:
                update_found = True
            
            print(f"{name}: new version available.\n    {url}\n")

            # Download if requested and save last-modified data (-d)
            if args.download or args.forcedownload:
                fn = parse_filename(url)
                # An exception will be raised here if a download directory is not found
                dl_dir = download_dir(data)
                download(url, dl_dir, fn)
                plug["lastModified"] = last_mod

        # If no updates found, notify
        if not update_found:
            print(f"{name}: no new version.\n")

        data["lastCheck"] = get_curr_datetime()


# Main
def main(): 
    data = read_json()
    # TODO : handle missing data.json better
    if not bool(data):
        return
    
    plugins = data["plugins"]

    # Add favorites
    if args.addfavorites:
        af = get_pref_list(args.addfavorites)
        for p in plugins:
            if p["name"] in af:
                p["isFavorite"] = True
        write_json(data)
        return
    
    # Add OS to preferences
    if args.addos:
        data["preferences"]["os"] = args.addos
        write_json(data)
        return
    
    # Add OS to preferences
    if args.adddownloaddir:
        data["preferences"]["downloadDir"] = args.adddownloaddir
        write_json(data)
        return
    
    # List all plugins (-l)
    if args.list:
        for p in plugins:
            print(f'{p["name"]} {"("+p["lastModified"]+")" if p["lastModified"] != "" else ""}')
        return
    
    # List all favorite plugins (-lf)
    if args.listfavorites:
        for p in plugins:
            if p["isFavorite"]:
                print(f'{p["name"]} {"("+p["lastModified"]+")" if p["lastModified"] != "" else ""}')
        return

    check(data)
    write_json(data)


# ...
if __name__ == "__main__":
    main()
