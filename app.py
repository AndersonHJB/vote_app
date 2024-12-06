import json
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# JSON 文件路径
DATA_FILE = "poll_data.json"

# 加载投票数据
def load_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


# 保存投票数据
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


# 初始化投票数据
poll_data = load_data()


@app.route("/")
def index():
    """首页：展示所有类别并支持每个类别投票"""
    return render_template("index.html", poll_data=poll_data)


@app.route("/vote", methods=["POST"])
def vote():
    """处理所有类别的投票"""
    for category_name, category_data in poll_data.items():
        selected_option = request.form.get(category_name)
        if selected_option in category_data["results"]:
            poll_data[category_name]["results"][selected_option] += 1

    save_data(poll_data)  # 保存更新后的数据到 JSON
    return redirect(url_for("results"))


@app.route("/results")
def results():
    """显示所有类别的投票结果"""
    return render_template("results.html", poll_data=poll_data)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    """后台管理页面，用于添加、删除类别"""
    if request.method == "POST":
        category_name = request.form.get("category_name")
        options = request.form.get("options").split(",")

        if category_name and options:
            poll_data[category_name] = {
                "options": options,
                "results": {option: 0 for option in options},
            }
            save_data(poll_data)

        return redirect(url_for("admin"))

    return render_template("admin.html", poll_data=poll_data)


@app.route("/delete/<category_name>", methods=["POST"])
def delete_category(category_name):
    """删除指定的投票类别"""
    if category_name in poll_data:
        del poll_data[category_name]
        save_data(poll_data)
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True)
