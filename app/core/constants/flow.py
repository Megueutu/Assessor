from enum import Enum

class Flow(str, Enum):
    DIRECT = "DIRECT"
    SPECIALIST = "SPECIALIST"
    REFER = "REFER"