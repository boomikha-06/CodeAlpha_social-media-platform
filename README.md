# ✨ SocialSpark — Social Media DBMS Project

A beautiful social media web app built purely with **Python + SQLite**. No JavaScript framework required!

---

## 🚀 Features

| Feature | Description |
|---|---|
| 👤 User Profiles | View profile, stats (posts, followers, following) |
| 📸 Posts | Create posts with emoji moods, view feed |
| 💬 Comments | Comment on any post |
| ❤️ Likes | Toggle like/unlike on posts |
| 🤝 Follow System | Follow and unfollow users |

---

## 🛠️ Tech Stack

- **Backend:** Python 3 (stdlib only — no pip install needed!)
- **Database:** SQLite 3
- **Frontend:** HTML + CSS (no JavaScript framework)
- **Server:** Python's built-in `http.server`

---

## ▶️ How to Run

### Windows
Double-click **`start.bat`** — that's it! 🎉

### Mac / Linux
```bash
python3 app.py
```

Then open [http://localhost:8080](http://localhost:8080)

---

## 📁 Project Structure

```
socialmedia_dbms/
├── app.py          ← Main Python server + all routes
├── schema.sql      ← SQLite database schema + seed data
├── start.bat       ← Windows launcher
└── README.md       ← You are here
```

The database file `socialmedia.db` is auto-created on first run.

---

## 🗄️ Database Schema (ERD Summary)

```
users ──< posts ──< comments
  |           |
  └──< follows  └──< likes
```

### Tables
- **users** — User profiles (id, username, email, avatar, bio)
- **posts** — Posts by users (content, emoji_mood, timestamp)
- **comments** — Comments on posts
- **likes** — Many-to-many: users ↔ posts (unique constraint)
- **follows** — Many-to-many: users ↔ users (self-referential)

---

## 👤 Demo Accounts (Pre-loaded)

| Username | Name | Bio |
|---|---|---|
| alex_spark | Alex Johnson | Coffee ☕ Coder 💻 (YOU — logged in) |
| luna_vibes | Luna Martinez | Photographer 📷 Traveller ✈️ |
| devesh_codes | Devesh Patel | Full-stack dev 🚀 |
| sara_bloom | Sara Williams | Artist 🎨 Nature lover 🌿 |

---

*Made for DBMS course project* 🎓
