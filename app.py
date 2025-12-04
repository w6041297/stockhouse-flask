import base64
from flask import Flask, render_template, request, jsonify
from uploader.drive_helper import DriveUploader
from uploader.sheet_helper import SheetWriter
from uploader.stockhouse import StockhouseClient

app = Flask(__name__)

# === CONFIG ===
SUCCESS_FOLDER = "1zb0B_0V-OBjWk0a_k3zXug41lcpDVePs"
FAILURE_FOLDER = "1wl_qpdjeCwcqRxgylzH51o_YlEwK2zoi"
SHEET_ID = "1g4E8TJIkjhhJNyDI8hFZMVPvpSKV7jXknl8exHVn32k"
LOG_SHEET = "工作表4"

stockhouse_email = "w6041297@gmail.com"
stockhouse_pass = "ABC123"
stockhouse_user = "1288"
stockhouse_session = "8271"

ERROR_MESSAGES = {
    10: '臨時/常會上傳錯誤類型',
    6: '已逾委託期限或尚未開放委託',
    3: '需要寄放身分證件實體正本',
    16: '電投圖未包含完整條碼',
    9: '電投圖未包含完整條碼',
    5: '需要寄放身分證實體正本',
    18: '無法用駕照正本',
    8: '需要先上傳身分證明圖',
    19: '元大股代需登錄身分證字號才能委託'
}

JSON_PATH = "service_account.json"

# === 初始化助手 ===
drive = DriveUploader(JSON_PATH)
sheet = SheetWriter(JSON_PATH, SHEET_ID)
sh_client = StockhouseClient(stockhouse_email, stockhouse_pass, stockhouse_user, stockhouse_session)
sh_client.login()


# === ROUTES ===

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_files():
    files = request.json.get("files", [])
    results = []

    for f in files:
        name = f["name"]
        mime = f["type"]
        data = base64.b64decode(f["data"])

        # 上傳到 Stockhouse
        resp = sh_client.upload(name, mime, data)

        code = ""
        name2 = ""
        if "stockcode" in resp and resp["stockcode"]:
            code = "".join([c for c in resp["stockcode"] if c.isdigit()])
        if "name" in resp:
            name2 = resp["name"]

        codeName = f"{code}-{name2}" if name2 else code
        new_filename = f"{codeName}.{name.split('.')[-1]}"

        ok = ("error" not in resp or resp.get("error") == 15)
        alert = ERROR_MESSAGES.get(resp.get("error"), "")

        # 存 Google Drive
        folder = SUCCESS_FOLDER if ok else FAILURE_FOLDER
        drive.upload_to_folder(folder, new_filename, data, mime)

        # 寫 Google Sheet log
        sheet.append(LOG_SHEET, [
            code,
            "已委託" if ok else "委託失敗",
            "新上傳",
            name2,
            alert,
            "否",
            "=NOW()"
        ])

        # 回傳給前端
        results.append({
            "name": name,
            "codeName": codeName,
            "success": ok,
            "alert": alert,
            "duplicated": False
        })

    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)