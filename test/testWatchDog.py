import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import os


if __name__ == "__main__":
    patterns = "*"
    ignore_patterns = ""
    ignore_directories = False
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

    def on_created(event):
        print(f"{event.src_path} has been created")

    def on_deleted(event):
        print(f"Delete {event.src_path}!")

    def on_modified(event):
        print(f"{event.src_path} has been modified")

    my_event_handler.on_created = on_created
    my_event_handler.on_deleted = on_deleted
    my_event_handler.on_modified = on_modified

    path = "./test"
    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)
    my_observer.start()
    try:
        while True:
            time.sleep(5)
    except:
        my_observer.stop()
    my_observer.join()
