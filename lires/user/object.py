from __future__ import annotations
import os
from io import BytesIO
import PIL.Image as Image
import aiofiles
from typing import Optional, TypedDict
from .conn import RawUser, UsrDBConnection
from .encrypt import encryptKey

class UserInfo(TypedDict):
    id: int
    username: str
    enc_key: str    # encrypted username+password
    name: str
    is_admin: bool
    mandatory_tags: list[str]
    has_avatar: bool
    max_storage: int

class AvatarPath(TypedDict):
    original: str
    square: str

class LiresUser:
    """
    Contains more information about a user.
    - Avatar image
    """

    def __init__(self, conn: UsrDBConnection, id: int) -> None:
        self._conn = conn
        self._id = id

        user_database = os.path.dirname(conn.db_path)
        self.USER_AVATAR_DIR = os.path.join(user_database, "avatar")
        if not os.path.exists(self.USER_AVATAR_DIR):
            os.mkdir(self.USER_AVATAR_DIR)
    
    @property
    def conn(self) -> UsrDBConnection: return self._conn
    @property
    def id(self) -> int: return self._id
    
    async def raw(self) -> RawUser:
        """The user information in the database"""
        return await self.conn.getUser(self._id)
    
    async def info(self) -> UserInfo:
        """For json serialization"""
        raw = await self.raw()
        enc_key = encryptKey(raw["username"], raw["password"])
        return {
            "id": raw["id"],
            "username": raw["username"],
            "enc_key": enc_key,
            "name": raw["name"],
            "is_admin": raw["is_admin"],
            "mandatory_tags": raw["mandatory_tags"],
            "has_avatar": self.avatar_image_path is not None,
            "max_storage": raw["max_storage"],
        }
    
    async def info_desensitized(self) -> UserInfo:
        """For json serialization"""
        ret = await self.info()
        ret["enc_key"] = "__HIDDEN__"
        return ret
    
    async def toString(self) -> str:
        info = await self.info()
        out = f"[{info['id']}] {info['username']} ({info['name']}), {info['enc_key']}, max: {info['max_storage']/1024/1024}MB"
        if info["is_admin"]:
            out += ", admin"
        return out
    
    async def equal(self, o: object) -> bool:
        if not isinstance(o, LiresUser):
            return False
        return await self.info() == await o.info()
    
    @property
    def avatar_image_path(self) -> Optional[AvatarPath]:
        a_pth: AvatarPath = {
            "original": os.path.join(self.USER_AVATAR_DIR, f"{self._id}_original.png"),
            "square": os.path.join(self.USER_AVATAR_DIR, f"{self._id}_square.png"),
        }
        if not all([os.path.exists(a_pth[k]) for k in a_pth]):
            for k in a_pth:
                # remove all if not all exist
                if os.path.exists(a_pth[k]):
                    os.remove(a_pth[k])
            return None
        else:
            return a_pth
    
    async def setAvatar(self, image: Optional[str | Image.Image]) -> None:
        """
        Read image from image_path,
        resize, and save it to USER_AVATAR_DIR.
        Save as three different sizes: original, large, small.
        Save as png format.

        When image_path is None, remove avatar images.
        """
        if image is None:
            # remove avatar image
            for k in ["original", "large", "small"]:
                pth = os.path.join(self.USER_AVATAR_DIR, f"{self._id}_{k}.png")
                if os.path.exists(pth):
                    os.remove(pth)
            return
        if isinstance(image, str):
            img = Image.open(image)
        elif isinstance(image, Image.Image):
            img = image
        else:
            raise TypeError("image must be str or PIL.Image.Image")

        # save original
        # img.save(os.path.join(self.USER_AVATAR_DIR, f"{self._id}_original.png"))
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        async with aiofiles.open(os.path.join(self.USER_AVATAR_DIR, f"{self._id}_original.png"), "wb") as fp:
            await fp.write(buffer.getbuffer())

        # crop to square
        if img.width > img.height:
            crop_left = (img.width - img.height) // 2
            crop_top = 0
        else:
            crop_left = 0
            crop_top = (img.height - img.width) // 2
        crop_len = min(img.width, img.height)
        img = img.crop((crop_left, crop_top, crop_left+crop_len, crop_top+crop_len))

        # resize to 512x512
        img_sq = img.resize((512, 512))
        # img_sq.save(os.path.join(self.USER_AVATAR_DIR, f"{self._id}_square.png"))
        buffer = BytesIO()
        img_sq.save(buffer, format="PNG")
        async with aiofiles.open(os.path.join(self.USER_AVATAR_DIR, f"{self._id}_square.png"), "wb") as fp:
            await fp.write(buffer.getbuffer())
        return 
