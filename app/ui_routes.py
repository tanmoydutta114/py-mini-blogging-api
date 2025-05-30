from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import requests

ui = Blueprint("ui", __name__)

API_BASE = "http://localhost:5000/api"


def get_auth_headers():
    token = session.get("access_token")
    return {"Authorization": f"Bearer {token}"} if token else {}


@ui.route("/")
def home():
    res = requests.get(f"{API_BASE}/posts")
    posts = res.json().get("posts", []) if res.ok else []
    return render_template("index.html", posts=posts)


@ui.route("/register", methods=["GET", "POST"])
def register():
    print(11111)
    if request.method == "POST":
        data = request.form.to_dict()
        res = requests.post(f"{API_BASE}/auth/register", json=data)
        if res.ok:
            session["access_token"] = res.json()["access_token"]
            session["username"] = res.json()["user"]["username"]
            session["user"] = res.json()["user"]['id']
            return redirect(url_for("ui.home"))
        flash(res.json().get("error", "Registration failed"), "danger")
    return render_template("register.html")


@ui.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        res = requests.post(f"{API_BASE}/auth/login", json=request.form.to_dict())
        if res.ok:
            session["access_token"] = res.json()["access_token"]
            session["username"] = res.json()["user"]["username"]
            session["user"] = res.json()["user"]['id']
            return redirect(url_for("ui.home"))
        flash("Invalid credentials", "danger")
    return render_template("login.html")


@ui.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("ui.home"))


@ui.route("/posts/new", methods=["GET", "POST"])
def create_post():
    if request.method == "POST":
        data = request.form.to_dict()
        data["is_published"] = "is_published" in data
        res = requests.post(f"{API_BASE}/posts", json=data, headers=get_auth_headers())
        if res.ok:
            return redirect(url_for("ui.home"))
        flash("Post creation failed", "danger")
    return render_template("post_form.html", post=None)


@ui.route("/posts/<int:post_id>", methods=["GET", "POST"])
def post_detail(post_id):
    post_res = requests.get(f"{API_BASE}/posts/{post_id}")
    comments_res = requests.get(f"{API_BASE}/comments/posts/{post_id}")
    if request.method == "POST" and session.get("user"):
        comment_data = {
            "name": session["username"],
            "content": request.form["content"],
            "post_id": post_id,
        }
        requests.post(f"{API_BASE}/comments", json=comment_data, headers=get_auth_headers())
        return redirect(request.url)
    return render_template(
        "post_detail.html",
        post=post_res.json().get("post"),
        comments=comments_res.json().get("comments", []),
    )


@ui.route("/posts/<int:post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id):
    post_res = requests.get(f"{API_BASE}/posts/{post_id}", headers=get_auth_headers())
    post = post_res.json().get("post") if post_res.ok else None
    if not post:
        flash("Post not found", "danger")
        return redirect(url_for("ui.home"))
    if request.method == "POST":
        data = request.form.to_dict()
        data["is_published"] = "is_published" in data
        res = requests.put(f"{API_BASE}/posts/{post_id}", json=data, headers=get_auth_headers())
        if res.ok:
            return redirect(url_for("ui.post_detail", post_id=post_id))
        flash("Update failed", "danger")
    return render_template("post_form.html", post=post)

@ui.route("/posts/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    res = requests.delete(f"{API_BASE}/posts/{post_id}", headers=get_auth_headers())
    if res.ok:
        flash("Post deleted", "success")
    else:
        flash("Failed to delete post", "danger")
    return redirect(url_for("ui.home"))

@ui.route("/comments/<int:comment_id>/delete", methods=["POST"])
def delete_comment(comment_id):
    res = requests.delete(f"{API_BASE}/comments/{comment_id}", headers=get_auth_headers())
    if res.ok:
        flash("Comment deleted", "success")
    else:
        flash("Failed to delete comment", "danger")
    return redirect(request.referrer or url_for("ui.home"))

@ui.route("/comments/<int:comment_id>", methods=["PUT"])
def update_comment(comment_id):
    if not request.is_json:
        return {"error": "Invalid request format"}, 400

    data = request.get_json()
    res = requests.put(
        f"{API_BASE}/comments/{comment_id}",
        headers=get_auth_headers(),
        json=data,
    )
    if res.ok:
        return {"message": "Comment updated successfully"}, 200
    else:
        return {"error": "Failed to update comment"}, res.status_code



@ui.route("/profile")
def profile():
    res = requests.get(f"{API_BASE}/auth/me", headers=get_auth_headers())
    user = res.json().get("user") if res.ok else {}
    return render_template("profile.html", user=user)
