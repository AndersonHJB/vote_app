from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 存储投票选项和结果
poll_options = ["黄婉棠", "Option 2", "Option 3"]
poll_results = {option: 0 for option in poll_options}


@app.route("/")
def index():
    return render_template("index.html", options=poll_options)


@app.route("/vote", methods=["POST"])
def vote():
    selected_option = request.form.get("option")
    if selected_option in poll_results:
        poll_results[selected_option] += 1
    return redirect(url_for("results"))


@app.route("/results")
def results():
    return render_template("results.html", results=poll_results)


if __name__ == "__main__":
    app.run(debug=True)
