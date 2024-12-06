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
        json.dump(data, file)


# 初始化投票数据
poll_data = load_data()


@app.route("/")
def index():
    """首页：显示所有投票类别"""
    categories = list(poll_data.keys())
    return render_template("index.html", categories=categories)


@app.route("/category/<category_name>")
def category(category_name):
    """显示单个类别的投票选项"""
    if category_name not in poll_data:
        return "Category not found", 404
    options = poll_data[category_name]["options"]
    return render_template("category.html", category_name=category_name, options=options)


@app.route("/vote/<category_name>", methods=["POST"])
def vote(category_name):
    """处理投票"""
    if category_name not in poll_data:
        return "Category not found", 404

    selected_option = request.form.get("option")
    if selected_option in poll_data[category_name]["results"]:
        poll_data[category_name]["results"][selected_option] += 1
        save_data(poll_data)  # 保存更新后的数据到 JSON
    return redirect(url_for("results", category_name=category_name))


@app.route("/results/<category_name>")
def results(category_name):
    """显示某个类别的投票结果"""
    if category_name not in poll_data:
        return "Category not found", 404

    results = poll_data[category_name]["results"]
    return render_template("results.html", category_name=category_name, results=results)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    """后台管理页面，用于添加或编辑类别"""
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


if __name__ == "__main__":
    app.run(debug=True)
