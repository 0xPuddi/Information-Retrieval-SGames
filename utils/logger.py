import datetime


class Logger:
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    RESET = "\033[0m"

    def __init__(self):
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
        stripped = tag
        padded = stripped.ljust(self.tag_width + 2)
        return f"{color}{padded}{self.RESET}"

    def _timestamp(self) -> str:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _log(self, tag: str, message: str):
        ts = self._timestamp()
        padded_ts = ts.ljust(self.ts_width)

        print(f"{self.colored_tags[tag]} {padded_ts} - {message}")

    def info(self, message: str):
        self._log("INFO", message)

    def warn(self, message: str):
        self._log("WARN", message)

    def error(self, message: str):
        self._log("ERROR", message)

    def ok(self, message: str):
        self._log("OK", message)


LOGGER = Logger()
