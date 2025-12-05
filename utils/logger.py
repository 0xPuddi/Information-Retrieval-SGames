import datetime


class Logger:
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    RESET = "\033[0m"

    LOG_FILE = "./utils/out.log"

    def __init__(self):
        # overwrite log file
        with open(self.LOG_FILE, "w") as f:
            f.write("")

        self.tags = ["INFO", "WARN", "ERROR", "OK"]
        self.tag_width = max(len(tag) for tag in self.tags)

        self.colored_tags = {
            "INFO":  self._color(f"[INFO]",  self.BLUE),
            "WARN":  self._color(f"[WARN]",  self.YELLOW),
            "ERROR": self._color(f"[ERROR]", self.RED),
            "OK":    self._color(f"[OK]",    self.GREEN),
        }

        self.ts_width = len(self._timestamp())

    def _color(self, tag: str, color: str) -> str:
        # inside tag
        inner = tag[1:-1]
        # color
        colored_inner = f"{color}{inner}{self.RESET}"
        result = f"[{colored_inner}]"
        # pad
        padding_needed = self.tag_width + 2 - len(inner) - 2
        return result + " " * padding_needed

    def _timestamp(self) -> str:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _log(self, tag: str, message: str):
        ts = self._timestamp()
        padded_ts = ts.ljust(self.ts_width)

        # with colors
        print(f"{self.colored_tags[tag]} {padded_ts} - {message}")

        # without colors
        line = f"[{tag}]".ljust(self.tag_width + 2) + \
            f" {padded_ts} - {message}"
        with open(self.LOG_FILE, "a") as f:
            f.write(line + "\n")

    def info(self, message: str):
        self._log("INFO", message)

    def warn(self, message: str):
        self._log("WARN", message)

    def error(self, message: str):
        self._log("ERROR", message)

    def ok(self, message: str):
        self._log("OK", message)


LOGGER = Logger()
