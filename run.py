import datetime

from synchronization.sync import Sync
import os
import json
import time
from apscheduler.schedulers.background import BackgroundScheduler


def main(src_folder, dist_folder, log_folder):
    check_paths_validity(src_folder)

    if not check_paths_validity(src_folder) or len(os.listdir(src_folder)) == 0:
        print("Source folder is empty")

    if not check_paths_validity(dist_folder):
        return

    obj = Sync()
    sync_data = obj.sync(src_folder, dist_folder)

    console_output(sync_data)

    if check_paths_validity(log_folder):
        log_file(sync_data, log_folder)


def log_file(sync_data, logfile_path):
    with open(os.path.join(logfile_path, f"{datetime.datetime.now()}.json"), 'w') as fjson:
        json.dump(sync_data, fjson)


def console_output(sync_data):
    if sync_data.get("created"):
        for key, values in sync_data.get('created').items():
            out = f"CREATED: \"{values['name']}\" file has been created and its path is \"{key}\" on {values['date']}"
            print(out)
        print()

    if sync_data.get("modified"):
        for key, values in sync_data.get('modified').items():
            out = f"MODIFIED: \"{values['name']}\" file has been modified and its path is \"{key}\" on {values['date']}"
            print(out)
        print()

    if sync_data.get("removed"):
        for key, values in sync_data.get('removed').items():
            out = f"REMOVED: \"{values['name']}\" {values['type']} has been removed and its path is \"{key}\""
            print(out)
        print()


def check_paths_validity(path):
    if not os.path.isdir(path) and not os.path.isfile(path):
        create_dir = input("\nThe path you entered does not exist, Do you want to creat it?, type y/n:\t")
        if create_dir == "y":
            os.mkdir(path)
            return

    elif os.path.isfile(path):
        retry_path = input("It is not a folder path, Please enter a directory path: \t")
        check_paths_validity(retry_path)
    else:
        return True


if __name__ == "__main__":
    print(f'{"*" * 5} Welcome in Sync-Folders Program {"*" * 5}'.center(200))
    print("Please insert folder paths (source then replica)")

    src_dir = input("Source Folder path: \t").strip()
    repl_dir = input('Replica Folder path: \t').strip()
    log_path = input('Please insert a dir path to save Log files: \t').strip()

    sync_intervals = float(input("Please input the sync intervals in minutes: "))

    main(src_dir, repl_dir, log_path)

    scheduler = BackgroundScheduler()
    scheduler.add_job(main, 'interval', minutes=sync_intervals, args=[src_dir, repl_dir, log_path])
    scheduler.start()

    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()
