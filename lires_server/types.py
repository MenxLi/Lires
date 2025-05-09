
from typing import TypedDict, Literal, Optional
from lires.user import UserInfo

class EventBase(TypedDict, total=False):
    session_id: str

class Event_Data(EventBase):
    type: Literal['delete_entry', 'add_entry', 'update_entry']
    uuid: str
    datapoint_summary: Optional[dict]

class Event_DataNote(Event_Data):
    type: Literal['update_note']
    note: str

class Event_Tag(EventBase):
    type: Literal['delete_tag', 'update_tag']
    src_tag: str
    dst_tag: Optional[str]

class Event_User(EventBase):
    type: Literal['delete_user', 'add_user', 'update_user', 'login', 'logout']
    username: str
    user_info: Optional[UserInfo]

Event = Event_Data | Event_DataNote | Event_Tag | Event_User


class ServerStatus(TypedDict):
    status: Literal['online', 'offline', 'maintenance']
    version: str
    uptime: float
    n_data: int
    n_connections: int
    n_connections_all: int