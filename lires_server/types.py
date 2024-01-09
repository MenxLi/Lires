


from typing import TypedDict, Literal, Optional
from lires.types.dataT import DataPointSummary
from lires.user import UserInfo

class EventBase(TypedDict, total=False):
    session_id: str

class Event_Data(EventBase):
    type: Literal['delete_entry', 'add_entry', 'update_entry']
    uuid: str
    datapoint_summary: Optional[DataPointSummary]

class Event_Tag(EventBase):
    type: Literal['delete_tag', 'update_tag']
    src_tag: str
    dst_tag: Optional[str]

class Event_User(EventBase):
    type: Literal['delete_user', 'add_user', 'update_user', 'login', 'logout']
    username: str
    user_info: Optional[UserInfo]

Event = Event_Data | Event_Tag | Event_User

