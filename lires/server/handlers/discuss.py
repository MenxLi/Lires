from ._base import *
import string, markdown

class DiscussionHandler(tornado.web.RequestHandler, RequestHandlerMixin):
    def get(self, file_uid: str):
        self.checkCookieKey()
        self.setDefaultHeader()
        discussions = self.discussion_db.discussions(file_uid)
        base_html = string.Template(
        """
        <html>
        <head>
        <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no">
        <title>Comments</title>
        <style>
            img {
                max-width: 100%;
            }
            hr {
                color: #dddddd
            }
            .usr_name {
                color: #888888
            }
            .hint {
                color: #888888;
                text-align: center
            }
            .discuss_uid {
                color: #bbbbbb;
                position: relative;
                font-size: 10px;
                float: right
            }
        </style>
        </head>
        <body>
        ${content}
        </body>
        </html>
        """)

        contents = []
        if not discussions:
            contents.append(
                "<p class=\"hint\">{}</p>".format("let us discuss this paper!"))
        for line in discussions:
            comment = markdown.markdown(line["content"])
            comment = "<div class=\"comment\">{}<div>".format(comment)

            content_ = "<p class=\"discuss_uid\">{}</p>".format(line["discuss_uid"])
            content_ += "<p class=\"usr_name\">{}: </p>".format(line["usr_name"])
            content_ += comment

            contents.append("<div class=\"discuss_line\">{}</div>".format(content_))
        rendered = base_html.substitute(content = "<hr>".join(contents))
        self.write(rendered)

class DiscussionModHandler (tornado.web.RequestHandler, RequestHandlerMixin):
    """
    Modify discussions
    """
    def post(self):
        self.setDefaultHeader()
        print("Receiving discussion modify request")

        cmd = self.get_argument("cmd")
        file_uid = self.get_argument("file_uid")
        content = self.get_argument("content")
        usr_name = self.get_argument("usr_name")

        permission =  self.checkKey()
        if not permission["is_admin"]:
            dp = self.db[file_uid]
            self.checkTagPermission(dp.tags, permission["mandatory_tags"])

        if cmd == "add":
            print("Adding discussion...")
            self.discussion_db.addDiscuss(
                file_uid = file_uid, 
                usr_name = usr_name, 
                content = content, 
                access_key_hex = self.enc_key,
            )