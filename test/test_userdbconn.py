
from lires.user.conn import UsrDBConnection
from lires.user import LiresUser

conn = UsrDBConnection(db_dir=".")
conn.insertUser("bbxaty", "123456", "bbxaty", False, ["he"])
conn.insertUser("admin", "123456", "admin", True, [])
conn.insertUser("test", "123456", "test", False, [])

conn.updateUser(
    conn.getUser("test")["id"], # type: ignore
    username = "test_new", password = "654321", name = "test_new", 
    is_admin = True, mandatory_tags = ["he", "she"]
    )
conn.deleteUser("bbxaty")

print(conn.getUser(2))
print(conn.getUser("bbxaty"))

user = LiresUser(conn, 3)
print(user.raw)
user.setAvatar("api_examples/.TempDir/avt.png")
print(user.avatar_image_path)
print(user.info())

conn.close()
