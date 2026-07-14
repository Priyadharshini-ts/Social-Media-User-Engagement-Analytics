import sqlite3

conn = sqlite3.connect("social_media.db")
cursor = conn.cursor()

# ---------------- CLEAN OLD DATA ----------------
cursor.execute("DELETE FROM Interactions")
cursor.execute("DELETE FROM Posts")
cursor.execute("DELETE FROM Users")

# ---------------- USERS ----------------
users = [
("alex_ray","alex@mail.com",2), ("sara_m","sara@mail.com",1),
("dev_jones","dev@mail.com",2), ("priya_k","priya@mail.com",1),
("tom_bright","tom@mail.com",1), ("nina_patel","nina@mail.com",2),
("leo_x","leo@mail.com",1), ("zara_w","zara@mail.com",2),
("mike_chan","mike@mail.com",1), ("emily_rose","emily@mail.com",2),
("jack_l","jack@mail.com",1), ("chloe_f","chloe@mail.com",2),
("ravi_s","ravi@mail.com",1), ("lucy_b","lucy@mail.com",1),
("oscar_t","oscar@mail.com",2), ("maya_d","maya@mail.com",1),
("ethan_v","ethan@mail.com",2), ("hannah_g","hannah@mail.com",1),
("carlos_m","carlos@mail.com",2), ("isabelle_r","isa@mail.com",1),
("noah_k","noah@mail.com",2), ("ava_l","ava@mail.com",1),
("liam_d","liam@mail.com",2), ("mia_s","mia@mail.com",1),
("arjun_r","arjun@mail.com",2)
]

cursor.executemany("""
INSERT INTO Users (Username, Email, AccountTypeID)
VALUES (?, ?, ?)
""", users)

# ---------------- POSTS ----------------
posts = []
post_id = 1

for user_id in range(1, 26):
    # each user 1–2 posts
    num_posts = 2 if user_id <= 10 else 1

    for i in range(num_posts):
        posts.append((
            user_id,
            f"Post {post_id} by user {user_id}",
            (post_id % 3) + 1
        ))
        post_id += 1

cursor.executemany("""
INSERT INTO Posts (UserID, ContentText, PostTypeID)
VALUES (?, ?, ?)
""", posts)

# ---------------- INTERACTIONS ----------------
interactions = []

# Popular posts (1–10) get more interactions
for post_id in range(1, 41):

    if post_id <= 10:
        users_range = range(1, 16)  # more engagement
    else:
        users_range = range(1, 10)

    for user_id in users_range:
        if user_id % 3 == 0:
            interactions.append((post_id, user_id, 1, None))  # Like
        elif user_id % 5 == 0:
            interactions.append((post_id, user_id, 2, None))  # Share
        else:
            interactions.append((post_id, user_id, 3, 30.0))  # Comment

cursor.executemany("""
INSERT INTO Interactions (PostID, UserID, InteractionTypeID, DurationViewed)
VALUES (?, ?, ?, ?)
""", interactions)

conn.commit()
conn.close()

print("Structured 125+ records inserted successfully!")

