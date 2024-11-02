class Logger:
    def __init__(self, verbose, process_id):
        self.process_id = process_id
        self.verbose = verbose
        self.log("Logger initialized")

    def log(self, *args):
        if self.verbose:
            print(f"[{self.process_id:02d}]", *args)
