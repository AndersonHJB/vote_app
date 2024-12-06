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
    """首页：显示所有投票组"""
    groups = list(poll_data.keys())
    return render_template("index.html", groups=groups)


@app.route("/group/<group_name>")
def group(group_name):
    """显示某个投票组的所有类别"""
    if group_name not in poll_data:
        return "Group not found", 404
    categories = poll_data[group_name]
    return render_template("group.html", group_name=group_name, categories=categories)


@app.route("/vote/<group_name>", methods=["POST"])
def vote(group_name):
    """处理某个投票组的投票"""
    if group_name not in poll_data:
        return "Group not found", 404

    for category_name, category_data in poll_data[group_name].items():
        selected_option = request.form.get(category_name)
        if selected_option in category_data["results"]:
            poll_data[group_name][category_name]["results"][selected_option] += 1

    save_data(poll_data)  # 保存更新后的数据到 JSON
    return redirect(url_for("results", group_name=group_name))


@app.route("/results/<group_name>")
def results(group_name):
    """显示某个投票组的投票结果"""
    if group_name not in poll_data:
        return "Group not found", 404
    categories = poll_data[group_name]
    return render_template("results.html", group_name=group_name, categories=categories)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    """后台管理页面，用于添加、删除投票组和类别"""
    if request.method == "POST":
        group_name = request.form.get("group_name")
        category_name = request.form.get("category_name")
        options = request.form.get("options").split(",")

        if group_name:
            # 如果投票组不存在，则创建
            if group_name not in poll_data:
                poll_data[group_name] = {}

            # 如果提供了类别，则添加类别
            if category_name and options:
                poll_data[group_name][category_name] = {
                    "options": options,
                    "results": {option: 0 for option in options},
                }

        save_data(poll_data)
        return redirect(url_for("admin"))

    return render_template("admin.html", poll_data=poll_data)


@app.route("/delete_group/<group_name>", methods=["POST"])
def delete_group(group_name):
    """删除投票组"""
    if group_name in poll_data:
        del poll_data[group_name]
        save_data(poll_data)
    return redirect(url_for("admin"))


@app.route("/delete_category/<group_name>/<category_name>", methods=["POST"])
def delete_category(group_name, category_name):
    """删除投票组中的某个类别"""
    if group_name in poll_data and category_name in poll_data[group_name]:
        del poll_data[group_name][category_name]
        save_data(poll_data)
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True)
