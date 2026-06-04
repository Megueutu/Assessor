from enum import Enum

class Flow(str, Enum):
    DIRECT = "direct"
    SPECIALIST = "specialist"
    REFER = "refer"