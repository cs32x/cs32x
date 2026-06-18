### cs32x-dev/utils/grab32.py - VERSION 20260618rm 
"""
This script simplifies the work a CS32x learner must do to grab
the files needed for a course unit, which are stored in a public
GitHub repository.

If a learner wants the files for `m04b`, they'd run this script in
the `cs32x` codespace as follows:

$ python3 grab32.py m04b

The input parameter (i.e., `m04b` in this example) should match the
name of a public `cs32x` GitHub repo.  The script will place this unit's
files in the `m04` subdirectory of the user's codespace, where `m04`
stands for the course's Module 4.

If a subdirectory of the same name already exists, this script assumes
that the user wants a new clean copy of the repo's files.  It will name
the clean copy `REPO_clean` (e.g., `m04_clean`).

Author: Mike Smith (with an AI copilot)
Date: June 2026
"""

import os
import subprocess
import sys
import zipfile

# Global constants and configuration parameters
ORG_URL = 'https://github.com/cs32x/'
MAIN_ZIP_PATH = '/archive/refs/heads/main.zip'
CODESPACES_ROOT = '/workspaces/cs32x'

VALID_REPOS = ['m01'] \
    + [f'm02{p}' for p in 'abcdefg'] \
    + [f'm03{p}' for p in 'abcdefg'] \
    + [f'm04{p}' for p in 'abcde'] \
    + ['m05'] \
    + [f'm07{p}' for p in 'abcdefghi']


def validate_working_dir():
    """Validates and returns the root directory of the user's codespace"""
    # Grab the current directory path
    cwd = os.getcwd()

    # If cwd is the codespace root directory, use it
    if cwd == CODESPACES_ROOT:
        return cwd

    # If we get here, we're not in the codespace root directory, and we
    # need to check that CODESPACES_ROOT exists.
    if not os.path.exists(CODESPACES_ROOT) or not os.path.isdir(CODESPACES_ROOT):
        sys.exit(f"ERROR: {CODESPACES_ROOT} doesn't exist")

    # It exists. Jump to CODESPACES_ROOT and return that path.
    try:
        os.chdir(CODESPACES_ROOT)
    except Exception as e:
        sys.exit(f"ERROR changing directory: {e}")

    return CODESPACES_ROOT


def my_rename(frompath, topath):
    """Rename a file or directory path from `frompath` to `topath`"""
    try:
        os.rename(frompath, topath)
    except FileNotFoundError:
        sys.exit(f"ERROR: the directory `{frompath}` does not exist")
    except FileExistsError:
        sys.exit(f"ERROR: a directory or file named `{topath}` already exists")
    except Exception as e:
        sys.exit(f"ERROR: {e}")


def process_zipfile(repo):
    """Downlads, extracts, and deletes the zipfile for the specified repo"""
    # Create URL to a zipfile of the specified github repo
    url = ORG_URL + repo + MAIN_ZIP_PATH
    zip_fname = os.path.basename(url)

    # Download the repo's files (quietly)
    try:
        command = ['wget', url]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception as e:
        sys.exit(f"ERROR executing wget command: {e}")
    print(f"... Zip file downloaded from: {url}")

    # Unzip the downloaded file
    try:
        # Open the zip file
        with zipfile.ZipFile(zip_fname, 'r') as zip_ref:
            # Extract contents to the current directory
            zip_ref.extractall()
    except zipfile.BadZipFile:
        sys.exit(f"ERROR: {zip_fname} is not a valid ZIP file")
    except Exception as e:
        sys.exit(f"Error unzipping {zip_fname}: {e}")
    print(f"... Unzipped {zip_fname} into {repo}-main")

    # Remove the downloaded zip file
    try:
        os.remove(zip_fname)
    except Exception as e:
        sys.exit(f"ERROR removing file {zip_fname}: {e}")
    print(f"... Removed {zip_fname}")


def move_files(repo, module):
    """Moves the files from repo-main to the appropriate location(s)"""
    # Create the directory names we'll possibly need
    zip_dir = repo + '-main'
    clean_dir = module + '_clean'

    # Set flag indicating whether clean_dir exists
    clean_exists = os.path.exists(clean_dir)

    # Flag indicating whether we need to rename zip_dir as clean_dir after processing all files
    clean_needed = False

    # Process the unzipped files in zip_dir. If module doesn't yet
    # exist, we rename zip_dir as module. If it does exist, we 
    # process each file in zip_dir. We move a file to module if it
    # doesn't already exist there. If it does exist in module, we
    # move it to clean_dir (if this directory exists) or mark that
    # we need to rename zip_dir as clean_dir.
    if not os.path.exists(module):
        # Module doesn't exist. Rename the zip_dir and be done.
        my_rename(zip_dir, module)
        print(f"... Renamed {zip_dir} to {module}")
    else:
        # Module exists. We must process each file.
        for item in os.listdir(zip_dir):
            src = os.path.join(zip_dir, item)
            dst = os.path.join(module, item)

            if not os.path.exists(dst):
                # No pre-existing src file in module. Move src to module.
                my_rename(src, dst)
                print(f"... Moved {src} to {dst}")

            elif clean_exists:
                # If dst already exists and clean_dir exists, move src to clean_dir
                dst_clean = os.path.join(clean_dir, item)
                my_rename(src, dst_clean)
                print(f"... Moved {src} to {dst_clean}")

            else:
                # Remember to move whatever remains in zip_dir to clean_dir after processing all files
                clean_needed = True
                print(f"... Not moving {src}")

        if clean_needed:
            # Move the remaining files in zip_dir to clean_dir
            my_rename(zip_dir, clean_dir)
            print(f"... Renamed {zip_dir} to {clean_dir}")
        else:
            # Remove the now-empty zip_dir
            try:
                os.rmdir(zip_dir)
                print(f"... Removed empty directory {zip_dir}")
            except Exception as e:
                sys.exit(f"ERROR removing directory {zip_dir}: {e}")


def main():
    # Check usage and grab the repo name
    if len(sys.argv) != 2:
        sys.exit("Usage: python3 grab32.py REPO")

    repo = sys.argv[1]

    # Check validity of input parameter and gracefully handle bad parameters
    if repo not in VALID_REPOS:
        sys.exit(f"ERROR: {repo} is not valid; did you mistype it?")

    # Start alerting the user to our progress
    print(f"STARTING grab32.py ...")

    # Make sure the script is in CODESPACES_ROOT
    codespace_path = validate_working_dir()
    print(f"... Working in directory: {codespace_path}")

    # Download the repo as a zipfile and process it
    process_zipfile(repo)

    # Determine module name (e.g., m04) from repo name (e.g., m04b)
    # and then move the files to the right places.
    module = repo[0:3]
    move_files(repo, module)

    # Alert the user that we're done
    print(f"grab32.py COMPLETE")
    print()
    print(f"To run a script in {module}, make sure to put yourself")
    print(f"in that directory by executing: cd {module}")
    print()

if __name__ == '__main__':
    main()
