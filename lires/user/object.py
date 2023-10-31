from __future__ import annotations
import os
import PIL.Image as Image
from typing import Optional, TypedDict
from .conn import RawUser, UsrDBConnection
from .encrypt import encryptKey
from ..confReader import USER_AVATAR_DIR

class UserInfo(TypedDict):
    id: int
    username: str
    enc_key: str    # encrypted username+password
    name: str
    is_admin: bool
    mandatory_tags: list[str]
    has_avatar: bool

class AvatarPath(TypedDict):
    original: str
    large: str
    small: str

class LiresUser:
    """
    Contains more information about a user.
    - Avatar image
    """

    def __init__(self, conn: UsrDBConnection, id: int) -> None:
        self._conn = conn
        self._id = id
    
    @property
    def conn(self) -> UsrDBConnection:
        return self._conn
    
    @property
    def raw(self) -> RawUser:
        """The user information in the database"""
        return self.conn.getUser(self._id)
    
    def info(self) -> UserInfo:
        """For json serialization"""
        raw = self.raw
        enc_key = encryptKey(raw["username"], raw["password"])
        return {
            "id": raw["id"],
            "username": raw["username"],
            "enc_key": enc_key,
            "name": raw["name"],
            "is_admin": raw["is_admin"],
            "mandatory_tags": raw["mandatory_tags"],
            "has_avatar": self.avatar_image_path is not None
        }
    
    def __str__(self) -> str:
        info = self.info()
        out = f"[{info['id']}] {info['username']} ({info['name']}), {info['enc_key']}"
        if info["is_admin"]:
            out += ", admin"
        return out
    
    def __repr__(self) -> str:
        return f"<LiresUser: {str(self)}>"
    
    @property
    def avatar_image_path(self) -> Optional[AvatarPath]:
        a_pth: AvatarPath = {
            "original": os.path.join(USER_AVATAR_DIR, f"{self._id}_original.png"),
            "large": os.path.join(USER_AVATAR_DIR, f"{self._id}_large.png"),
            "small": os.path.join(USER_AVATAR_DIR, f"{self._id}_small.png"),
        }
        if not all([os.path.exists(a_pth[k]) for k in a_pth]):
            return None
        else:
            return a_pth
    
    def setAvatar(self, image_path: Optional[str]) -> None:
        """
        Read image from image_path,
        resize, and save it to USER_AVATAR_DIR.
        Save as three different sizes: original, large, small.
        Save as png format.

        When image_path is None, remove avatar images.
        """
        if image_path is None:
            # remove avatar image
            for k in ["original", "large", "small"]:
                pth = os.path.join(USER_AVATAR_DIR, f"{self._id}_{k}.png")
                if os.path.exists(pth):
                    os.remove(pth)
            return
        img = Image.open(image_path)
        # save original
        img.save(os.path.join(USER_AVATAR_DIR, f"{self._id}_original.png"))

        # crop to square
        if img.width > img.height:
            crop_left = (img.width - img.height) // 2
            crop_top = 0
        else:
            crop_left = 0
            crop_top = (img.height - img.width) // 2
        crop_len = min(img.width, img.height)
        img = img.crop((crop_left, crop_top, crop_left+crop_len, crop_top+crop_len))

        # resize to 500x500
        img_500 = img.resize((500, 500))
        img_500.save(os.path.join(USER_AVATAR_DIR, f"{self._id}_large.png"))

        # resize to 100x100
        img_100 = img.resize((100, 100))
        img_100.save(os.path.join(USER_AVATAR_DIR, f"{self._id}_small.png"))
        return 
