import os
import string
import re

def showFiles(path:str, type:str="audio") -> dict:
    file_types = {
        "audio": ["mp3","wav","flac", "opus"], 
        "text": ["txt", "csv"], 
        "dir": None
    }
    files_dict = {}
    print("\n")
    for idx, file in enumerate(os.listdir(path)):
        if file.split(".")[-1] in file_types[type]:
            files_dict[idx] = file
            print(f"{idx}: {file}")
    print(f"-1: All files")

    return files_dict

def showDir(base_dir:str):
    directories = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

    print("\nPlease select a directory:")
    for i, directory in enumerate(directories):
        print(f"{i+1}. {directory}")

    choice = int(input("Enter the number of your choice: ")) - 1
    audioPath = os.path.join(base_dir, directories[choice])
    return audioPath

def normalizeNaming(nameStr:str):
    special_chars = ['%', '$', '&', '"', '!', "@"]
    for char in special_chars:
        nameStr = nameStr.replace(char, ' ')
    nameStr = nameStr.translate(str.maketrans('', '', string.punctuation))
    nameStr = re.sub(' +', ' ', nameStr).replace(' ', '_')
    return nameStr