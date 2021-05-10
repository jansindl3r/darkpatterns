from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import time

def update(event):
    print(event)
    import darkpatterns

if __name__ == "__main__":
    patterns = ["./templates/*", "./data/*", "./darkpatterns.py"]
    ignore_patterns = None
    ignore_directories = False
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
    my_event_handler.on_created = update
    my_event_handler.on_deleted = update
    my_event_handler.on_modified = update
    my_event_handler.on_moved = update
    path = "."
    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)
    my_observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()