from pydantic import BaseModel

class SidebarLink(BaseModel):
    name: str
    href: str
    description: str
    active: bool
