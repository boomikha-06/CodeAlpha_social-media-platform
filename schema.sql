-- ============================================
-- 🌟 SocialSpark - Social Media App Schema
-- DBMS Project | SQLite Database
-- ============================================

PRAGMA foreign_keys = ON;

-- 👤 USER PROFILES TABLE
CREATE TABLE IF NOT EXISTS users (
    user_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT NOT NULL UNIQUE,
    full_name   TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE,
    password    TEXT NOT NULL,
    bio         TEXT DEFAULT '',
    avatar      TEXT DEFAULT '🧑',
    joined_at   DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 📸 POSTS TABLE
CREATE TABLE IF NOT EXISTS posts (
    post_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    content     TEXT NOT NULL,
    emoji_mood  TEXT DEFAULT '✨',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 💬 COMMENTS TABLE
CREATE TABLE IF NOT EXISTS comments (
    comment_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id     INTEGER NOT NULL,
    user_id     INTEGER NOT NULL,
    content     TEXT NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id)  REFERENCES posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)  REFERENCES users(user_id) ON DELETE CASCADE
);

-- ❤️ LIKES TABLE
CREATE TABLE IF NOT EXISTS likes (
    like_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id     INTEGER NOT NULL,
    user_id     INTEGER NOT NULL,
    liked_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, user_id),
    FOREIGN KEY (post_id)  REFERENCES posts(post_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id)  REFERENCES users(user_id) ON DELETE CASCADE
);

-- 🤝 FOLLOWS TABLE
CREATE TABLE IF NOT EXISTS follows (
    follow_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    follower_id INTEGER NOT NULL,
    following_id INTEGER NOT NULL,
    followed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(follower_id, following_id),
    CHECK(follower_id != following_id),
    FOREIGN KEY (follower_id)  REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (following_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================
-- 🌱 SEED DATA
-- ============================================
INSERT OR IGNORE INTO users (username, full_name, email, password, bio, avatar) VALUES
('alex_spark',   'Alex Johnson',   'alex@spark.com',   'pass123', 'Coffee lover ☕ | Coder 💻 | Dreamer 🌙', '🧑'),
('luna_vibes',   'Luna Martinez',  'luna@spark.com',   'pass123', 'Photographer 📷 | Traveller ✈️ | Cat mom 🐱', '👩'),
('devesh_codes', 'Devesh Patel',   'devesh@spark.com', 'pass123', 'Full-stack dev 🚀 | Open source ❤️', '🧔'),
('sara_bloom',   'Sara Williams',  'sara@spark.com',   'pass123', 'Artist 🎨 | Nature lover 🌿 | Yoga 🧘', '👩‍🦰');

INSERT OR IGNORE INTO posts (user_id, content, emoji_mood) VALUES
(1, 'Just deployed my first app to production! The feeling is UNREAL 🚀 Hard work pays off!', '🚀'),
(2, 'Golden hour at the beach today 🌅 Some moments are just meant to be captured forever.', '🌅'),
(3, 'Hot take: Clean code is not a luxury, it is a necessity. Discuss 👇', '💡'),
(4, 'Painted for 3 hours straight today. Lost track of time completely. That is what flow feels like 🎨', '🎨'),
(1, 'Morning coffee + lo-fi music + open terminal = perfect morning ☕', '☕'),
(2, 'Traveled 1000km just to see this sunset. Zero regrets. 🌄', '🌄');

INSERT OR IGNORE INTO comments (post_id, user_id, content) VALUES
(1, 2, 'Congratulations!! You deserve it 🎉🎉'),
(1, 3, 'Which stack did you use? Would love to know! 🤩'),
(1, 4, 'That feeling is absolutely priceless! So happy for you! 💖'),
(2, 1, 'This photo is breathtaking! 😍 Where was this?'),
(3, 1, 'Totally agree. Spaghetti code gives me nightmares 😅'),
(3, 4, 'Yes! Readable code saves future-you so much pain 🙏'),
(4, 2, 'Flow state is the best state 🌊 Your work is so beautiful!');

INSERT OR IGNORE INTO likes (post_id, user_id) VALUES
(1, 2),(1, 3),(1, 4),
(2, 1),(2, 3),(2, 4),
(3, 1),(3, 2),
(4, 1),(4, 2),(4, 3),
(5, 2),(5, 4),
(6, 1),(6, 3),(6, 4);

INSERT OR IGNORE INTO follows (follower_id, following_id) VALUES
(1, 2),(1, 3),(1, 4),
(2, 1),(2, 3),
(3, 1),(3, 4),
(4, 2),(4, 3);
