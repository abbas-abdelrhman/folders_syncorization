import os
import shutil
import datetime
import hashlib
import mmap
import time


class Sync:
    def __init__(self):
        self.recap = {
            "removed": {},
            "modified": {},
            "created": {},
        }

    def sync(self, src_folder, replica_folder):

        if not os.path.exists(replica_folder):
            self.copying_files(set(os.listdir(src_folder)), src_folder, replica_folder)
            return

        elif set(os.listdir(src_folder)) - set(os.listdir(replica_folder)):
            self.copying_files(set(os.listdir(src_folder)) - set(os.listdir(replica_folder)), src_folder,
                               replica_folder)

        if set(os.listdir(replica_folder)) - set(os.listdir(src_folder)):
            self.removing_files(set(os.listdir(replica_folder)) - set(os.listdir(src_folder)), replica_folder)

        if set(os.listdir(src_folder)) & set(os.listdir(replica_folder)):
            self.modified(set(os.listdir(src_folder)) & set(os.listdir(replica_folder)), src_folder, replica_folder)

        return self.recap

    def copying_files(self, src_contents: set, src, replica):

        if not os.path.exists(replica):
            os.mkdir(replica)

        for file in src_contents:
            file_path = os.path.join(src, file)

            if not os.path.isdir(file_path):
                shutil.copy2(os.path.join(src, file), replica)
                created = {
                    os.path.join(replica, file): {
                        "name": file,
                        "date": time.ctime()
                    }
                }
                self.recap['created'].update(created)

            elif os.path.isdir(file_path):
                self.copying_files(set(os.listdir(file_path)), file_path, os.path.join(replica, file))

    def removing_files(self, src_contents: set, replica):

        for item in src_contents:
            item_path = os.path.join(replica, item)

            if os.path.exists(item_path):
                if os.path.isfile(item_path):
                    removed = {
                        item_path: {
                            "name": item,
                            "type": "File"
                        }
                    }
                    os.remove(item_path)
                    self.recap['removed'].update(removed)
                elif os.path.isdir(item_path):
                    removed = {
                        item_path: {
                            "name": item,
                            "type": "Directory"
                        }
                    }
                    shutil.rmtree(item_path)
                    self.recap['removed'].update(removed)
            else:
                continue

    def modified(self, src_contents: set, src_folder, replica_folder):
        for item in src_contents:
            # Get the full paths of the items
            item1_path = os.path.join(src_folder, item)
            item2_path = os.path.join(replica_folder, item)

            # Compare the attributes of the items
            if os.path.isfile(item1_path) and os.path.isfile(item2_path):
                # If both items are files, compare their modification times and sizes
                if self.get_file_hash(item1_path) != self.get_file_hash(item2_path) or self.get_modification_time(
                        item1_path) != self.get_modification_time(item2_path):
                    # If the modification times or sizes are different, copy the file from one folder to the other
                    shutil.copy2(item1_path, item2_path)
                    modified = {
                        item2_path: {
                            "name": item,
                            "date": self.get_modification_time(item1_path)
                        }
                    }
                    self.recap['modified'].update(modified)

            elif os.path.isdir(item1_path) and os.path.isdir(item2_path):
                # If both items are directories, recursively compare their contents
                self.sync(item1_path, item2_path)

    @staticmethod
    def get_modification_time(item_path):
        if os.path.exists(item_path):
            last_modification_time = os.path.getmtime(item_path)
            human_readable_time = datetime.datetime.fromtimestamp(last_modification_time).strftime("%Y-%m-%d %H:%M:%S")
            return human_readable_time

    @staticmethod
    def get_file_hash(file_path):
        if not os.path.getsize(file_path):
            return 0
        else:
            with open(file_path, 'rb') as file, mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as file_contents:
                file_hash = hashlib.sha256(file_contents).hexdigest()
                return file_hash
