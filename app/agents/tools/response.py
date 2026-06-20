from dataclasses import dataclass

@dataclass
class ToolResponse:
    @classmethod
    def ok(cls, **kwargs) -> dict:
        return {"status": "ok", **kwargs}
    
    @classmethod
    def error(cls, message: str, **kwargs) -> dict:
        return {"status": "error", "message": message, **kwargs}

    @classmethod
    def custom(cls, status: str, **kwargs) -> dict:
        return {"status": status, **kwargs}
