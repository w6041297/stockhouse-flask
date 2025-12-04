import requests

class StockhouseClient:
    def __init__(self, email, password, user_id, session):
        self.email = email
        self.password = password
        self.user_id = user_id
        self.session = session
        self.base = "https://www.stockhouse.com.tw/"
        self.s = requests.Session()

    def login(self):
        # 拿 cookie
        self.s.get(self.base + "login.php")

        # 登入
        payload = {
            "email": self.email,
            "password": self.password
        }
        self.s.post(self.base + "login.php", data=payload)

    def upload(self, filename, mime, raw_bytes):
        files = {
            "files[]": (filename, raw_bytes, mime)
        }
        data = {
            "user_id": self.user_id,
            "s": self.session,
            "buy": "0",
            "candantou": "4"
        }

        resp = self.s.post(self.base + "filer/ajax_upload_file.php", data=data, files=files)
        try:
            return resp.json()
        except:
            return {"error": 999, "msg": "JSON parse error"}