from pydantic import BaseModel, Field
from typing import Optional


class FilesystemSearchArgs(BaseModel):
    root: str
    glob: str = "**/*"
    contains: Optional[str] = None
    limit: int = 50


class ToolCall(BaseModel):
    tool: str = Field(..., description="Tool name, e.g., filesystem.search")
    args: dict
