class Logger:
    def __init__(self, verbose, process_id):
        self.process_id = process_id
        self.verbose = verbose
        self.log("Logger initialized")

    def log(self, *args, **kwargs):
        if self.verbose:
            print(f"[{self.process_id:02d}]", *args, **kwargs)


class FileLogger:
    def __init__(self, verbose, process_id):
        self.filename = f"{process_id}.txt"
        self.file = open(self.filename, "a")  # Open the file in append mode

    def log(self, *args):
        self.file.write(" ".join([str(a) for a in args]) + "\n")

    def __del__(self):
        self.file.close()  # Close the file when the object is garbage collected
