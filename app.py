"""
🌟 SocialSpark - Social Media DBMS Project
Backend: Python + SQLite (NO JavaScript framework)
"""

import sqlite3
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse, unquote
import json

DB_PATH = "socialmedia.db"

# ─────────────────────────────────────────────
# DATABASE HELPERS
# ─────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db()
    with open("schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("✅ Database initialized!")

def get_all_posts(current_user_id=1):
    conn = get_db()
    rows = conn.execute("""
        SELECT p.post_id, p.content, p.emoji_mood, p.created_at,
               u.username, u.full_name, u.avatar,
               (SELECT COUNT(*) FROM likes WHERE post_id=p.post_id) AS like_count,
               (SELECT COUNT(*) FROM comments WHERE post_id=p.post_id) AS comment_count,
               (SELECT COUNT(*) FROM likes WHERE post_id=p.post_id AND user_id=?) AS user_liked
        FROM posts p JOIN users u ON p.user_id=u.user_id
        ORDER BY p.created_at DESC
    """, (current_user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_post_comments(post_id):
    conn = get_db()
    rows = conn.execute("""
        SELECT c.content, c.created_at, u.username, u.avatar
        FROM comments c JOIN users u ON c.user_id=u.user_id
        WHERE c.post_id=?
        ORDER BY c.created_at ASC
    """, (post_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_users(current_user_id=1):
    conn = get_db()
    rows = conn.execute("""
        SELECT u.user_id, u.username, u.full_name, u.avatar, u.bio,
               (SELECT COUNT(*) FROM follows WHERE following_id=u.user_id) AS followers,
               (SELECT COUNT(*) FROM follows WHERE follower_id=u.user_id) AS following,
               (SELECT COUNT(*) FROM posts WHERE user_id=u.user_id) AS post_count,
               (SELECT COUNT(*) FROM follows WHERE follower_id=? AND following_id=u.user_id) AS is_following
        FROM users u ORDER BY u.joined_at
    """, (current_user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def toggle_like(post_id, user_id):
    conn = get_db()
    existing = conn.execute("SELECT like_id FROM likes WHERE post_id=? AND user_id=?", (post_id, user_id)).fetchone()
    if existing:
        conn.execute("DELETE FROM likes WHERE post_id=? AND user_id=?", (post_id, user_id))
        action = "unliked"
    else:
        conn.execute("INSERT INTO likes (post_id, user_id) VALUES (?,?)", (post_id, user_id))
        action = "liked"
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM likes WHERE post_id=?", (post_id,)).fetchone()[0]
    conn.close()
    return action, count

def toggle_follow(follower_id, following_id):
    conn = get_db()
    existing = conn.execute("SELECT follow_id FROM follows WHERE follower_id=? AND following_id=?", (follower_id, following_id)).fetchone()
    if existing:
        conn.execute("DELETE FROM follows WHERE follower_id=? AND following_id=?", (follower_id, following_id))
        action = "unfollowed"
    else:
        conn.execute("INSERT INTO follows (follower_id, following_id) VALUES (?,?)", (follower_id, following_id))
        action = "followed"
    conn.commit()
    conn.close()
    return action

def add_post(user_id, content, emoji_mood):
    conn = get_db()
    conn.execute("INSERT INTO posts (user_id, content, emoji_mood) VALUES (?,?,?)", (user_id, content, emoji_mood))
    conn.commit()
    conn.close()

def add_comment(post_id, user_id, content):
    conn = get_db()
    conn.execute("INSERT INTO comments (post_id, user_id, content) VALUES (?,?,?)", (post_id, user_id, content))
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────
# HTML TEMPLATES
# ─────────────────────────────────────────────

BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500;600&display=swap');
:root {
  --bg: #0a0a0f;
  --surface: #13131a;
  --card: #1a1a24;
  --border: #2a2a3a;
  --accent: #c084fc;
  --accent2: #f472b6;
  --accent3: #38bdf8;
  --text: #e8e8f0;
  --muted: #888899;
  --liked: #f472b6;
  --radius: 16px;
}
* { margin:0; padding:0; box-sizing:border-box; }
body {
  font-family:'DM Sans',sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height:100vh;
  background-image: radial-gradient(ellipse at 20% 20%, #1a0a2e 0%, transparent 50%),
                    radial-gradient(ellipse at 80% 80%, #0a1a2e 0%, transparent 50%);
}
a { color:var(--accent); text-decoration:none; }
a:hover { text-decoration:underline; }
.navbar {
  background: rgba(19,19,26,0.85);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border);
  padding: 0 2rem;
  position: sticky; top:0; z-index:100;
  display:flex; align-items:center; justify-content:space-between; height:64px;
}
.brand {
  font-family:'Playfair Display',serif;
  font-size:1.6rem; font-weight:900;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  background-clip:text;
}
.nav-links { display:flex; gap:0.5rem; }
.nav-links a {
  padding:8px 18px; border-radius:999px;
  font-weight:500; font-size:0.9rem; color:var(--muted);
  transition: all 0.2s;
}
.nav-links a:hover, .nav-links a.active {
  background: rgba(192,132,252,0.15);
  color:var(--accent); text-decoration:none;
}
.container { max-width:720px; margin:0 auto; padding:2rem 1rem; }
.wide-container { max-width:1100px; margin:0 auto; padding:2rem 1rem; }
.card {
  background:var(--card);
  border:1px solid var(--border);
  border-radius:var(--radius);
  padding:1.5rem;
  margin-bottom:1rem;
  transition: border-color 0.2s, transform 0.2s;
}
.card:hover { border-color: rgba(192,132,252,0.3); }
.post-header { display:flex; align-items:center; gap:0.75rem; margin-bottom:1rem; }
.avatar-circle {
  width:44px; height:44px; border-radius:50%;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  display:flex; align-items:center; justify-content:center;
  font-size:1.3rem; flex-shrink:0;
}
.post-meta { flex:1; }
.post-meta strong { display:block; font-size:0.95rem; }
.post-meta small { color:var(--muted); font-size:0.8rem; }
.post-content { font-size:1rem; line-height:1.7; margin-bottom:1rem; }
.emoji-badge {
  display:inline-block; font-size:1.4rem;
  margin-right:0.5rem; vertical-align:middle;
}
.post-actions { display:flex; gap:0.5rem; flex-wrap:wrap; }
.btn {
  padding:8px 18px; border:1px solid var(--border);
  border-radius:999px; cursor:pointer;
  font-family:'DM Sans',sans-serif; font-size:0.85rem;
  font-weight:500; transition:all 0.2s;
  background:transparent; color:var(--text);
  display:inline-flex; align-items:center; gap:6px;
}
.btn:hover { background: rgba(255,255,255,0.06); }
.btn-like { }
.btn-like.liked { border-color:var(--liked); color:var(--liked); background:rgba(244,114,182,0.1); }
.btn-primary {
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  border:none; color:#fff; font-weight:600;
}
.btn-primary:hover { opacity:0.88; transform:translateY(-1px); }
.btn-follow {
  background: rgba(192,132,252,0.12);
  border-color: var(--accent); color:var(--accent);
}
.btn-follow.following {
  background: rgba(56,189,248,0.1);
  border-color: var(--accent3); color:var(--accent3);
}
.form-group { margin-bottom:1rem; }
.form-group label { display:block; margin-bottom:6px; font-size:0.9rem; color:var(--muted); font-weight:500; }
.form-group input, .form-group textarea, .form-group select {
  width:100%; padding:12px 16px;
  background:var(--surface); border:1px solid var(--border);
  border-radius:12px; color:var(--text);
  font-family:'DM Sans',sans-serif; font-size:0.95rem;
  transition: border-color 0.2s;
  outline:none;
}
.form-group input:focus, .form-group textarea:focus {
  border-color:var(--accent);
}
.form-group textarea { resize:vertical; min-height:100px; }
.page-title {
  font-family:'Playfair Display',serif;
  font-size:2rem; font-weight:900;
  margin-bottom:1.5rem;
  background: linear-gradient(135deg, var(--text), var(--muted));
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  background-clip:text;
}
.tag {
  display:inline-block; padding:4px 12px;
  background:rgba(192,132,252,0.12);
  border:1px solid rgba(192,132,252,0.3);
  border-radius:999px; font-size:0.78rem;
  color:var(--accent); font-weight:500;
}
.stats-row { display:flex; gap:1.5rem; margin:0.5rem 0; }
.stat { text-align:center; }
.stat strong { display:block; font-size:1.1rem; font-weight:700; }
.stat small { color:var(--muted); font-size:0.78rem; }
.comments-section { margin-top:1rem; border-top:1px solid var(--border); padding-top:1rem; }
.comment {
  display:flex; gap:0.6rem; margin-bottom:0.75rem; align-items:flex-start;
}
.comment-avatar { font-size:1.1rem; }
.comment-body { background:var(--surface); border-radius:12px; padding:8px 14px; flex:1; }
.comment-body strong { font-size:0.82rem; color:var(--accent); }
.comment-body p { font-size:0.9rem; margin-top:2px; }
.user-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:1rem; }
.user-card {
  background:var(--card); border:1px solid var(--border);
  border-radius:var(--radius); padding:1.5rem; text-align:center;
  transition: border-color 0.2s, transform 0.2s;
}
.user-card:hover { border-color:rgba(192,132,252,0.3); transform:translateY(-2px); }
.user-card .avatar-circle { width:64px;height:64px;font-size:1.8rem;margin:0 auto 0.75rem; }
.user-card h3 { font-size:1rem; margin-bottom:4px; }
.user-card p { color:var(--muted); font-size:0.83rem; margin-bottom:0.75rem; }
.flash {
  padding:12px 20px; border-radius:12px; margin-bottom:1rem;
  background:rgba(192,132,252,0.15); border:1px solid rgba(192,132,252,0.3);
  color:var(--accent); font-size:0.9rem;
}
.divider { height:1px; background:var(--border); margin:1.5rem 0; }
.emoji-picker { display:flex; gap:0.4rem; flex-wrap:wrap; margin-top:6px; }
.emoji-opt {
  padding:6px 10px; border:1px solid var(--border);
  border-radius:8px; cursor:pointer;
  background:var(--surface); font-size:1.1rem;
  transition:all 0.15s;
}
.emoji-opt:hover { border-color:var(--accent); background:rgba(192,132,252,0.1); }
.hero-bar {
  background: linear-gradient(135deg, rgba(192,132,252,0.08), rgba(244,114,182,0.08));
  border:1px solid rgba(192,132,252,0.15);
  border-radius:var(--radius); padding:2rem; margin-bottom:2rem; text-align:center;
}
.hero-bar h2 { font-family:'Playfair Display',serif; font-size:1.6rem; margin-bottom:0.5rem; }
.hero-bar p { color:var(--muted); font-size:0.95rem; }
</style>
"""

def nav(active="feed"):
    tabs = [("feed","🏠 Feed"),("users","👥 People"),("new","✏️ Post"),("profile","👤 Profile")]
    links = ""
    for key,label in tabs:
        cls = 'active' if active==key else ''
        links += f'<a href="/{key}" class="{cls}">{label}</a>'
    return f"""
    <nav class="navbar">
      <span class="brand">✨ SocialSpark</span>
      <div class="nav-links">{links}</div>
    </nav>"""

def render_page(title, body, active="feed"):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | SocialSpark ✨</title>
{BASE_CSS}
</head>
<body>
{nav(active)}
{body}
</body>
</html>"""

# ─────────────────────────────────────────────
# PAGE BUILDERS
# ─────────────────────────────────────────────

CURRENT_USER_ID = 1  # Simulated logged-in user (alex_spark)

def page_feed(msg=""):
    posts = get_all_posts(CURRENT_USER_ID)
    cards = ""
    for p in posts:
        liked_class = "liked" if p["user_liked"] else ""
        comments = get_post_comments(p["post_id"])
        comment_html = ""
        for c in comments:
            comment_html += f"""
            <div class="comment">
              <span class="comment-avatar">{c['avatar']}</span>
              <div class="comment-body">
                <strong>@{c['username']}</strong>
                <p>{c['content']}</p>
              </div>
            </div>"""
        cards += f"""
        <div class="card">
          <div class="post-header">
            <div class="avatar-circle">{p['avatar']}</div>
            <div class="post-meta">
              <strong>{p['full_name']} <span class="tag">@{p['username']}</span></strong>
              <small>🕐 {p['created_at'][:16]}</small>
            </div>
            <span style="font-size:1.8rem">{p['emoji_mood']}</span>
          </div>
          <p class="post-content">{p['content']}</p>
          <div class="post-actions">
            <form method="POST" action="/like" style="display:inline">
              <input type="hidden" name="post_id" value="{p['post_id']}">
              <button class="btn btn-like {liked_class}" type="submit">
                ❤️ {p['like_count']} Like{'s' if p['like_count']!=1 else ''}
              </button>
            </form>
            <span class="btn">💬 {p['comment_count']} Comment{'s' if p['comment_count']!=1 else ''}</span>
          </div>
          <div class="comments-section">
            {comment_html if comments else '<p style="color:var(--muted);font-size:0.85rem">No comments yet. Be first! 💬</p>'}
            <form method="POST" action="/comment" style="margin-top:0.75rem;display:flex;gap:0.5rem">
              <input type="hidden" name="post_id" value="{p['post_id']}">
              <input type="text" name="content" placeholder="Add a comment... 💭" style="flex:1;padding:8px 14px;border-radius:999px;background:var(--surface);border:1px solid var(--border);color:var(--text);font-family:DM Sans,sans-serif;outline:none">
              <button class="btn btn-primary" type="submit">Send</button>
            </form>
          </div>
        </div>"""
    flash = f'<div class="flash">🎉 {msg}</div>' if msg else ""
    body = f"""
    <div class="container">
      {flash}
      <div class="hero-bar">
        <h2>What's happening? 🌍</h2>
        <p>Stay connected with the people you love ✨</p>
      </div>
      <h1 class="page-title">🏠 Your Feed</h1>
      {cards}
    </div>"""
    return render_page("Feed", body, "feed")

def page_users(msg=""):
    users = get_all_users(CURRENT_USER_ID)
    cards = ""
    for u in users:
        if u["user_id"] == CURRENT_USER_ID:
            continue
        follow_label = "✅ Following" if u["is_following"] else "➕ Follow"
        follow_cls = "following" if u["is_following"] else ""
        cards += f"""
        <div class="user-card">
          <div class="avatar-circle">{u['avatar']}</div>
          <h3>{u['full_name']}</h3>
          <p>@{u['username']}</p>
          <p style="margin-bottom:0.5rem">{u['bio'] or 'No bio yet 🤷'}</p>
          <div class="stats-row" style="justify-content:center">
            <div class="stat"><strong>{u['followers']}</strong><small>Followers</small></div>
            <div class="stat"><strong>{u['following']}</strong><small>Following</small></div>
            <div class="stat"><strong>{u['post_count']}</strong><small>Posts</small></div>
          </div>
          <div style="margin-top:1rem">
            <form method="POST" action="/follow">
              <input type="hidden" name="target_id" value="{u['user_id']}">
              <button class="btn btn-follow {follow_cls}" type="submit">{follow_label}</button>
            </form>
          </div>
        </div>"""
    flash = f'<div class="flash">✅ {msg}</div>' if msg else ""
    body = f"""
    <div class="wide-container">
      {flash}
      <h1 class="page-title">👥 Discover People</h1>
      <div class="user-grid">{cards}</div>
    </div>"""
    return render_page("People", body, "users")

def page_new_post(msg=""):
    emojis = ["✨","🚀","❤️","😂","🌅","💡","🎨","☕","🔥","🎉","😍","🌿","📷","💻","🎵","🌙"]
    emoji_opts = "".join(f'<span class="emoji-opt" onclick="document.getElementById(\'mood\').value=\'{e}\'">{e}</span>' for e in emojis)
    flash = f'<div class="flash">🎉 {msg}</div>' if msg else ""
    body = f"""
    <div class="container">
      {flash}
      <h1 class="page-title">✏️ Create Post</h1>
      <div class="card">
        <form method="POST" action="/new">
          <div class="form-group">
            <label>📝 What's on your mind?</label>
            <textarea name="content" placeholder="Share your thoughts, ideas, or moments... ✨" required></textarea>
          </div>
          <div class="form-group">
            <label>🎭 Choose your mood emoji</label>
            <div class="emoji-picker">{emoji_opts}</div>
            <input type="text" id="mood" name="emoji_mood" value="✨" style="margin-top:8px;width:80px;text-align:center;font-size:1.4rem">
          </div>
          <button class="btn btn-primary" type="submit" style="width:100%;justify-content:center;padding:14px">
            🚀 Publish Post
          </button>
        </form>
      </div>
    </div>"""
    return render_page("New Post", body, "new")

def page_profile():
    conn = get_db()
    u = conn.execute("""
        SELECT u.*, 
               (SELECT COUNT(*) FROM posts WHERE user_id=u.user_id) AS post_count,
               (SELECT COUNT(*) FROM follows WHERE following_id=u.user_id) AS followers,
               (SELECT COUNT(*) FROM follows WHERE follower_id=u.user_id) AS following
        FROM users u WHERE u.user_id=?
    """, (CURRENT_USER_ID,)).fetchone()
    u = dict(u)
    posts_raw = conn.execute("""
        SELECT p.*, (SELECT COUNT(*) FROM likes WHERE post_id=p.post_id) AS like_count,
               (SELECT COUNT(*) FROM comments WHERE post_id=p.post_id) AS comment_count
        FROM posts p WHERE p.user_id=? ORDER BY created_at DESC
    """, (CURRENT_USER_ID,)).fetchall()
    conn.close()
    post_html = ""
    for p in posts_raw:
        p = dict(p)
        post_html += f"""
        <div class="card" style="margin-bottom:0.75rem">
          <p style="font-size:1.5rem;margin-bottom:0.5rem">{p['emoji_mood']}</p>
          <p class="post-content">{p['content']}</p>
          <small style="color:var(--muted)">❤️ {p['like_count']} likes &nbsp;·&nbsp; 💬 {p['comment_count']} comments &nbsp;·&nbsp; 🕐 {p['created_at'][:16]}</small>
        </div>"""
    body = f"""
    <div class="container">
      <h1 class="page-title">👤 My Profile</h1>
      <div class="card" style="text-align:center;padding:2rem">
        <div class="avatar-circle" style="width:80px;height:80px;font-size:2.2rem;margin:0 auto 1rem">{u['avatar']}</div>
        <h2 style="font-family:Playfair Display,serif;font-size:1.5rem">{u['full_name']}</h2>
        <p style="color:var(--muted);margin-bottom:0.5rem">@{u['username']}</p>
        <p style="margin-bottom:1rem">{u['bio'] or 'No bio yet.'}</p>
        <div class="stats-row" style="justify-content:center;gap:2.5rem">
          <div class="stat"><strong>{u['post_count']}</strong><small>Posts</small></div>
          <div class="stat"><strong>{u['followers']}</strong><small>Followers</small></div>
          <div class="stat"><strong>{u['following']}</strong><small>Following</small></div>
        </div>
      </div>
      <div class="divider"></div>
      <h2 style="font-family:Playfair Display,serif;margin-bottom:1rem">📸 My Posts</h2>
      {post_html or '<p style="color:var(--muted)">No posts yet. Create your first one! ✨</p>'}
    </div>"""
    return render_page("Profile", body, "profile")

# ─────────────────────────────────────────────
# HTTP SERVER
# ─────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)
        msg = qs.get("msg",[""])[0]

        if path in ("/","","/feed"):
            html = page_feed(msg)
        elif path == "/users":
            html = page_users(msg)
        elif path == "/new":
            html = page_new_post(msg)
        elif path == "/profile":
            html = page_profile()
        else:
            html = "<h1 style='color:white;padding:2rem'>404 - Page not found</h1>"

        self.send_response(200)
        self.send_header("Content-Type","text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        length = int(self.headers.get("Content-Length",0))
        body = self.rfile.read(length).decode("utf-8")
        params = parse_qs(body)

        def p(key): return unquote(params.get(key,[""])[0])

        if self.path == "/like":
            action, count = toggle_like(int(p("post_id")), CURRENT_USER_ID)
            msg = f"You {action} the post! ({'❤️' if action=='liked' else '💔'})"
            self.redirect("/feed", msg)

        elif self.path == "/comment":
            content = p("content")
            if content.strip():
                add_comment(int(p("post_id")), CURRENT_USER_ID, content)
            self.redirect("/feed", "Comment added! 💬")

        elif self.path == "/new":
            content = p("content")
            emoji = p("emoji_mood") or "✨"
            if content.strip():
                add_post(CURRENT_USER_ID, content, emoji)
            self.redirect("/feed", "Post published! 🚀")

        elif self.path == "/follow":
            target_id = int(p("target_id"))
            action = toggle_follow(CURRENT_USER_ID, target_id)
            msg = f"You {action} this person! {'💜' if action=='followed' else '👋'}"
            self.redirect("/users", msg)

        else:
            self.redirect("/feed")

    def redirect(self, to, msg=""):
        from urllib.parse import quote
        url = to + (f"?msg={quote(msg)}" if msg else "")
        self.send_response(302)
        self.send_header("Location", url)
        self.end_headers()

    def log_message(self, fmt, *args):
        pass  # Suppress console spam

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    port = 8080
    print("=" * 50)
    print("  ✨ SocialSpark DBMS Project")
    print(f"  🌐 Open: http://localhost:{port}")
    print("  🛑 Press Ctrl+C to stop")
    print("=" * 50)
    import webbrowser, threading
    threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{port}")).start()
    HTTPServer(("", port), Handler).serve_forever()
