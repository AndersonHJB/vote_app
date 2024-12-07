import json
import uuid
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import random
import string

app = Flask(__name__)

# JSON 文件路径
DATA_FILE = "poll_data.json"


def load_data():
    """从 JSON 文件加载投票数据"""
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_data(data):
    """将投票数据保存到 JSON 文件"""
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def find_group_by_link_suffix(poll_data, link_suffix):
    """通过link_suffix查找group_name"""
    for g_name, g_data in poll_data.items():
        if "_meta" in g_data and g_data["_meta"].get("link_suffix") == link_suffix:
            return g_name
    return None

def generate_random_nickname():
    # 生成随机用户名并加上日期后缀
    rand_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    date_suffix = datetime.now().strftime('%Y%m%d')
    return f"User_{rand_str}_{date_suffix}"


@app.route("/")
def index():
    """首页：显示所有投票组（直接传poll_data给模板）"""
    poll_data = load_data()
    return render_template("index.html", poll_data=poll_data)


@app.route("/group/<group_name>")
def group(group_name):
    """显示某个投票组的所有类别（通过group_name）"""
    poll_data = load_data()
    if group_name not in poll_data:
        return "Group not found", 404
    categories = {k: v for k, v in poll_data[group_name].items() if k != "_meta"}
    link_suffix = poll_data[group_name]["_meta"].get("link_suffix") if "_meta" in poll_data[group_name] else None
    return render_template("group.html", group_name=group_name, categories=categories, link_suffix=link_suffix)


@app.route("/results/<group_name>")
def results(group_name):
    """显示某个投票组的投票结果（通过group_name）"""
    poll_data = load_data()
    if group_name not in poll_data:
        return "Group not found", 404
    categories = {k: v for k, v in poll_data[group_name].items() if k != "_meta"}
    link_suffix = poll_data[group_name]["_meta"].get("link_suffix") if "_meta" in poll_data[group_name] else None
    return render_template("results.html", group_name=group_name, categories=categories, link_suffix=link_suffix)


@app.route("/vote/<group_name>", methods=["POST"])
def vote(group_name):
    """处理某个投票组的投票（通过group_name）"""
    poll_data = load_data()
    if group_name not in poll_data:
        return "Group not found", 404

    nickname = request.form.get("nickname", "").strip()
    if not nickname:
        nickname = generate_random_nickname()

    # 确保user_votes字段存在
    if "user_votes" not in poll_data[group_name]["_meta"]:
        poll_data[group_name]["_meta"]["user_votes"] = {}

    user_votes = poll_data[group_name]["_meta"]["user_votes"]
    user_votes[nickname] = user_votes.get(nickname, {})

    for category_name, category_data in poll_data[group_name].items():
        if category_name == "_meta":
            continue
        selected_option = request.form.get(category_name)
        if selected_option and selected_option in category_data["results"]:
            category_data["results"][selected_option] += 1
            user_votes[nickname][category_name] = selected_option

    save_data(poll_data)  # 保存更新后的数据到 JSON
    return redirect(url_for("results", group_name=group_name))


# 新增通过link_suffix访问的路由
@app.route("/g/<link_suffix>")
def group_by_link(link_suffix):
    poll_data = load_data()
    group_name = find_group_by_link_suffix(poll_data, link_suffix)
    if not group_name:
        return "Group not found", 404
    categories = {k: v for k, v in poll_data[group_name].items() if k != "_meta"}
    return render_template("group.html", group_name=group_name, categories=categories, link_suffix=link_suffix)


@app.route("/r/<link_suffix>")
def results_by_link(link_suffix):
    poll_data = load_data()
    group_name = find_group_by_link_suffix(poll_data, link_suffix)
    if not group_name:
        return "Group not found", 404
    categories = {k: v for k, v in poll_data[group_name].items() if k != "_meta"}
    return render_template("results.html", group_name=group_name, categories=categories, link_suffix=link_suffix)


@app.route("/v/<link_suffix>", methods=["POST"])
def vote_by_link(link_suffix):
    poll_data = load_data()
    group_name = find_group_by_link_suffix(poll_data, link_suffix)
    if not group_name:
        return "Group not found", 404

    nickname = request.form.get("nickname", "").strip()
    if not nickname:
        nickname = generate_random_nickname()

    if "user_votes" not in poll_data[group_name]["_meta"]:
        poll_data[group_name]["_meta"]["user_votes"] = {}

    user_votes = poll_data[group_name]["_meta"]["user_votes"]
    user_votes[nickname] = user_votes.get(nickname, {})

    for category_name, category_data in poll_data[group_name].items():
        if category_name == "_meta":
            continue
        selected_option = request.form.get(category_name)
        if selected_option and selected_option in category_data["results"]:
            category_data["results"][selected_option] += 1
            user_votes[nickname][category_name] = selected_option

    save_data(poll_data)
    return redirect(url_for("results_by_link", link_suffix=link_suffix))


@app.route("/admin", methods=["GET", "POST"])
def admin():
    """后台管理页面，用于添加、删除投票组和类别，并设置链接后缀"""
    poll_data = load_data()
    if request.method == "POST":
        group_name = request.form.get("group_name")
        category_name = request.form.get("category_name")
        options = request.form.get("options")
        link_suffix = request.form.get("link_suffix")

        options_list = []
        if options and options.strip():
            options_list = [opt.strip() for opt in options.split(",") if opt.strip()]

        if group_name:
            # 如果投票组不存在，则创建
            if group_name not in poll_data:
                # 如果没设置link_suffix则用UUID
                if not link_suffix or not link_suffix.strip():
                    link_suffix = str(uuid.uuid4())
                poll_data[group_name] = {
                    "_meta": {
                        "link_suffix": link_suffix,
                        "user_votes": {}
                    }
                }

            # 如果提供了类别与选项，则添加类别
            if category_name and options_list:
                poll_data[group_name][category_name] = {
                    "options": options_list,
                    "results": {option: 0 for option in options_list},
                }

        save_data(poll_data)  # 保存更新
        return redirect(url_for("admin"))

    return render_template("admin.html", poll_data=poll_data)


@app.route("/delete_group/<group_name>", methods=["POST"])
def delete_group(group_name):
    """删除投票组"""
    poll_data = load_data()
    if group_name in poll_data:
        del poll_data[group_name]
        save_data(poll_data)  # 保存更新
    return redirect(url_for("admin"))


@app.route("/delete_category/<group_name>/<category_name>", methods=["POST"])
def delete_category(group_name, category_name):
    """删除投票组中的某个类别"""
    poll_data = load_data()
    if group_name in poll_data and category_name in poll_data[group_name]:
        del poll_data[group_name][category_name]
        save_data(poll_data)  # 保存更新
    return redirect(url_for("admin"))

@app.route("/category/<group_name>/<category_name>")
def single_category(group_name, category_name):
    poll_data = load_data()
    if group_name not in poll_data or category_name not in poll_data[group_name]:
        return "Category not found", 404
    options = poll_data[group_name][category_name]["options"]
    link_suffix = poll_data[group_name]["_meta"]["link_suffix"] if "_meta" in poll_data[group_name] else None
    return render_template("category.html", category_name=category_name, options=options, group_name=group_name, link_suffix=link_suffix)


@app.route("/voters/<group_name>")
def voters(group_name):
    """查看每个昵称所投选项的页面"""
    poll_data = load_data()
    if group_name not in poll_data:
        return "Group not found", 404
    user_votes = poll_data[group_name]["_meta"].get("user_votes", {})
    return render_template("voters.html", group_name=group_name, user_votes=user_votes)


if __name__ == "__main__":
    app.run(debug=True)
