
# * IMPORT DEPENDENCIES
import os
import logging
from datetime import datetime
import shutil
from decouple import config
import mimetypes

# * INITIALIZE VARIABLES
DOWNLOADS_DIRECTORY = config("DOWNLOADS_DIRECTORY", "")
folders_directory = os.path.join(DOWNLOADS_DIRECTORY, "01. Folder")

# Add custom file types
mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("project/vnd.adobe.photoshop", ".psd")
mimetypes.add_type("project/vnd.adobe.premiere", ".prproj")
mimetypes.add_type("compressed/x-rar-compressed", ".rar")
mimetypes.add_type("application/x-msi", ".msi")
mimetypes.add_type("compressed/x-7z-compressed", ".7z")
mimetypes.add_type("application/vnd.debian.binary-package", ".deb")
mimetypes.add_type("application/x-iso9660-image", ".iso")
mimetypes.add_type("application/rdf+xml", ".xmp")
mimetypes.add_type("file/x-chrome-download", ".crdownload")


# Create a logger
current_time = datetime.now().strftime("%d%m%y_%H%M%S")
log_filename = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "logs", f"logfile_{current_time}.log")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
l_handler = logging.FileHandler(log_filename)
l_format = logging.Formatter(
    "%(asctime)s - %(name)s -%(levelname)s - %(message)s")
l_handler.setFormatter(l_format)
logger.addHandler(l_handler)


# * Main Function.
def main():
    try:
        iterate_others(DOWNLOADS_DIRECTORY)
    except Exception as e:
        logger.exception(f"Exception in main function: {str(e)}")


# * Function to create directories.
def create_directories(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except PermissionError as pe:
        logger.warning(
            f"Permission denied. Cannot create directory '{directory}'.")
        logger.error(f"Permission denied. Error: '{pe}'")
    except Exception as e:
        logger.exception(f"Exception in create_directories function: {str(e)}")


# * Function to iterate files and directories inside 'Others' folder.
def iterate_others(directory):
    # Create the directory called '01. Folders'
    create_directories(folders_directory)

    # Check and move all other folders and files.
    try:
        for entry in os.scandir(directory):
            if entry.is_dir():
                move_directories(entry, directory)
            elif entry.is_file():
                move_files(entry, directory)
    except OSError as oe:
        logger.error(f"Error processing {entry.name}: {str(e)}")
    except Exception as e:
        logger.exception(f"Exception in iterate_others function: {str(e)}")


# * Function to move directories to '01. Folders'
def move_directories(entry, directory):

    # Check if the directory is a main directory.
    is_numeric = False
    try:
        value = entry.name.split(". ")[0]
        is_numeric = isinstance(int(value), int)
    except:
        pass

    # Check and move other folders to the Folders directory.
    if entry.path != folders_directory and not is_numeric:
        src_path = os.path.join(directory, entry.name)
        dest_path = os.path.join(folders_directory, entry.name)

        try:
            # Move folders inside to Folders directory.
            shutil.move(src_path, dest_path)
            print(f"Moved directory: {entry.name}")
        except (shutil.Error, OSError, IOError) as e:
            logger.error(f"Error moving directory {entry.name}: {str(e)}")
        except Exception as e:
            logger.exception(f"Exception in move_directories: {str(e)}")
            raise


# * Function to convert 0-9 to two digits.
def convert_num_to_two_digits(num):
    try:
        n = int(num)
        if 0 <= n < 10:
            return str(num).zfill(2)
        else:
            return str(num)
    except ValueError as ve:
        logger.error(f"Invalid number: {num}. Error: {str(ve)}")
    except Exception as e:
        logger.exception(
            f"Exception in convert_num_to_two_digits function: {str(e)}")


# * Function to move files to respective directories.
def move_files(entry, directory):

    try:

        # Retrieve the extension and find the type of the extension.
        mime_type, _ = mimetypes.guess_type(entry)
        file_type, sub_type = mime_type.split('/', 1)

        sub_type_mapping = {
            "pdf": "document",
            "vnd.openxmlformats-officedocument.spreadsheetml.sheet": "document",
            "vnd.openxmlformats-officedocument.spreadsheetml.template": "document",
            "vnd.openxmlformats-officedocument.wordprocessingml.document": "document",
            "vnd.openxmlformats-officedocument.presentationml.presentation": "document",
            "msword": "document",
            "vnd.ms-excel": "document",
            "vnd.ms-publisher": "document",
            "msaccess": "database",
            "svg+xml": "graphics",
            "json": "data",
            "x-zip-compressed": "compressed",
            None: "other"
        }

        # Get the file type based on sub type.
        file_type = sub_type_mapping.get(sub_type, file_type).capitalize()

        # Find the directory number and name.
        dir_nums, dir_names = find_all_dirs(directory)

        if file_type in dir_names:
            index = dir_names.index(file_type)
            check_and_move_files(
                entry, directory, dir_nums[index], dir_names[index])
        else:
            next_num = int(dir_nums[-1]) + 1 if dir_nums else 1
            check_and_move_files(
                entry, directory, next_num, file_type)
    except ValueError as ve:
        logger.error(f"Value Error: {str(ve)}")
    except Exception as e:
        logger.exception(f"Exception in move_files: {str(e)}")


def find_all_dirs(directory):
    dir_nums, dir_names = [], []

    # Get the list of all directories.
    for cur_dir in os.scandir(directory):
        if cur_dir.is_dir():
            try:
                num = cur_dir.name.split(". ")[0].strip()
                is_numeric = isinstance(int(num), int)
                name = cur_dir.name.split(". ")[1].strip()
            except (ValueError, IndexError):
                is_numeric = False

            if is_numeric:
                dir_nums.append(int(num))
                dir_names.append(name)

    return dir_nums, dir_names


def check_and_move_files(entry, directory, dir_num, dir_name):
    dir_num = convert_num_to_two_digits(dir_num)

    folder_name = f"{dir_num}. {dir_name}"

    src_path = os.path.join(directory, entry.name)
    dest_path = os.path.join(directory, folder_name)

    create_directories(dest_path)

    try:
        shutil.move(src_path, dest_path)
        print("Moved directory:", entry.name)
    except (shutil.Error, IOError, OSError) as e:
        logger.error(
            f"Error moving file {entry.name} from {src_path} to {dest_path}: {str(e)}")
    except Exception as e:
        logger.exception(f"Exception in check_and_move_files: {str(e)}")
        raise


if __name__ == "__main__":
    main()
