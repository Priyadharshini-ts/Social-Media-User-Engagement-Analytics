import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import os
from datetime import datetime

DB_PATH = "social_media.db"

# ─────────────────────────── DATABASE SETUP ───────────────────────────

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS AccountTypes (
        AccountTypeID INTEGER PRIMARY KEY,
        TypeName TEXT UNIQUE NOT NULL
    );
    CREATE TABLE IF NOT EXISTS PostTypes (
        PostTypeID INTEGER PRIMARY KEY,
        TypeName TEXT UNIQUE NOT NULL
    );
    CREATE TABLE IF NOT EXISTS InteractionTypes (
        InteractionTypeID INTEGER PRIMARY KEY,
        TypeName TEXT UNIQUE NOT NULL
    );
    INSERT OR IGNORE INTO AccountTypes VALUES (1,'Basic');
    INSERT OR IGNORE INTO AccountTypes VALUES (2,'Premium');
    INSERT OR IGNORE INTO PostTypes VALUES (1,'Text');
    INSERT OR IGNORE INTO PostTypes VALUES (2,'Image');
    INSERT OR IGNORE INTO PostTypes VALUES (3,'Video');
    INSERT OR IGNORE INTO InteractionTypes VALUES (1,'Like');
    INSERT OR IGNORE INTO InteractionTypes VALUES (2,'Share');
    INSERT OR IGNORE INTO InteractionTypes VALUES (3,'Comment');
    CREATE TABLE IF NOT EXISTS Users (
        UserID INTEGER PRIMARY KEY AUTOINCREMENT,
        Username TEXT UNIQUE NOT NULL,
        Email TEXT UNIQUE NOT NULL,
        JoinDate DATETIME DEFAULT CURRENT_TIMESTAMP,
        AccountTypeID INTEGER NOT NULL,
        FOREIGN KEY (AccountTypeID) REFERENCES AccountTypes(AccountTypeID)
    );
    CREATE TABLE IF NOT EXISTS Posts (
        PostID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER NOT NULL,
        ContentText TEXT,
        PostTypeID INTEGER NOT NULL,
        PostTimestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
        FOREIGN KEY (PostTypeID) REFERENCES PostTypes(PostTypeID)
    );
    CREATE TABLE IF NOT EXISTS Interactions (
        InteractionID INTEGER PRIMARY KEY AUTOINCREMENT,
        PostID INTEGER NOT NULL,
        UserID INTEGER NOT NULL,
        InteractionTypeID INTEGER NOT NULL,
        DurationViewed REAL,
        InteractedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (PostID) REFERENCES Posts(PostID) ON DELETE CASCADE,
        FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
        FOREIGN KEY (InteractionTypeID) REFERENCES InteractionTypes(InteractionTypeID),
        UNIQUE (PostID, UserID, InteractionTypeID)
    );
    CREATE TABLE IF NOT EXISTS Followers (
        FollowerID INTEGER NOT NULL,
        FollowingID INTEGER NOT NULL,
        FollowedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (FollowerID, FollowingID),
        FOREIGN KEY (FollowerID) REFERENCES Users(UserID) ON DELETE CASCADE,
        FOREIGN KEY (FollowingID) REFERENCES Users(UserID) ON DELETE CASCADE,
        CHECK (FollowerID <> FollowingID)
    );
    CREATE INDEX IF NOT EXISTS idx_post_user  ON Posts(UserID);
    CREATE INDEX IF NOT EXISTS idx_post_time  ON Posts(PostTimestamp);
    CREATE INDEX IF NOT EXISTS idx_inter_post ON Interactions(PostID);
    CREATE INDEX IF NOT EXISTS idx_inter_user ON Interactions(UserID);
    CREATE INDEX IF NOT EXISTS idx_inter_time ON Interactions(InteractedAt);
    """)
    conn.commit()
    conn.close()

# ─────────────────────────── STYLES ───────────────────────────

DARK_BG   = "#1a1d23"
PANEL_BG  = "#22262f"
CARD_BG   = "#2a2f3a"
ACCENT    = "#4f8ef7"
ACCENT2   = "#3ecfb2"
TEXT_PRI  = "#e8eaf0"
TEXT_SEC  = "#8a8fa8"
DANGER    = "#e05c5c"
SUCCESS   = "#3ecfb2"
BORDER    = "#363b4a"
ENTRY_BG  = "#1e222b"

def apply_styles(root):
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", background=DARK_BG, foreground=TEXT_PRI,
                    fieldbackground=ENTRY_BG, font=("Segoe UI", 10))
    style.configure("TFrame", background=DARK_BG)
    style.configure("Card.TFrame", background=CARD_BG, relief="flat")
    style.configure("Panel.TFrame", background=PANEL_BG)
    style.configure("TLabel", background=DARK_BG, foreground=TEXT_PRI)
    style.configure("Sub.TLabel", background=DARK_BG, foreground=TEXT_SEC, font=("Segoe UI", 9))
    style.configure("Card.TLabel", background=CARD_BG, foreground=TEXT_PRI)
    style.configure("H1.TLabel", background=DARK_BG, foreground=TEXT_PRI,
                    font=("Segoe UI", 16, "bold"))
    style.configure("H2.TLabel", background=DARK_BG, foreground=TEXT_PRI,
                    font=("Segoe UI", 12, "bold"))
    style.configure("Stat.TLabel", background=CARD_BG, foreground=ACCENT,
                    font=("Segoe UI", 22, "bold"))
    style.configure("StatSub.TLabel", background=CARD_BG, foreground=TEXT_SEC,
                    font=("Segoe UI", 9))
    style.configure("TButton", background=ACCENT, foreground="#ffffff",
                    font=("Segoe UI", 9, "bold"), relief="flat", padding=(10, 5))
    style.map("TButton", background=[("active", "#3a7de0"), ("pressed", "#2d6bcf")])
    style.configure("Danger.TButton", background=DANGER, foreground="#ffffff",
                    font=("Segoe UI", 9, "bold"), relief="flat", padding=(8, 4))
    style.map("Danger.TButton", background=[("active", "#c94e4e")])
    style.configure("Flat.TButton", background=PANEL_BG, foreground=TEXT_PRI,
                    font=("Segoe UI", 10), relief="flat", padding=(12, 8))
    style.map("Flat.TButton",
              background=[("active", CARD_BG), ("selected", CARD_BG)],
              foreground=[("active", ACCENT)])
    style.configure("Treeview", background=CARD_BG, foreground=TEXT_PRI,
                    fieldbackground=CARD_BG, rowheight=28,
                    font=("Segoe UI", 9))
    style.configure("Treeview.Heading", background=PANEL_BG, foreground=TEXT_SEC,
                    font=("Segoe UI", 9, "bold"), relief="flat")
    style.map("Treeview", background=[("selected", ACCENT)],
              foreground=[("selected", "#ffffff")])
    style.configure("TEntry", fieldbackground=ENTRY_BG, foreground=TEXT_PRI,
                    insertcolor=TEXT_PRI, relief="flat", padding=6)
    style.configure("TCombobox", fieldbackground=ENTRY_BG, foreground=TEXT_PRI,
                    background=ENTRY_BG, relief="flat")
    style.map("TCombobox", fieldbackground=[("readonly", ENTRY_BG)],
              foreground=[("readonly", TEXT_PRI)])
    style.configure("TScrollbar", background=PANEL_BG, troughcolor=DARK_BG,
                    arrowcolor=TEXT_SEC, relief="flat")
    style.configure("TNotebook", background=DARK_BG, tabmargins=0)
    style.configure("TNotebook.Tab", background=PANEL_BG, foreground=TEXT_SEC,
                    padding=(14, 7), font=("Segoe UI", 9))
    style.map("TNotebook.Tab",
              background=[("selected", DARK_BG)],
              foreground=[("selected", ACCENT)])
    style.configure("TSeparator", background=BORDER)

# ─────────────────────────── HELPERS ───────────────────────────

def labeled_entry(parent, label, row, col=0, width=26, colspan=1, bg=DARK_BG):
    lbl = ttk.Label(parent, text=label, style="Sub.TLabel")
    lbl.configure(background=bg)
    lbl.grid(row=row, column=col, sticky="w", padx=(0, 8), pady=(8, 0))
    ent = ttk.Entry(parent, width=width)
    ent.grid(row=row+1, column=col, columnspan=colspan, sticky="ew", pady=(2, 0))
    return ent

def labeled_combo(parent, label, values, row, col=0, width=24, bg=DARK_BG):
    lbl = ttk.Label(parent, text=label, style="Sub.TLabel")
    lbl.configure(background=bg)
    lbl.grid(row=row, column=col, sticky="w", padx=(0, 8), pady=(8, 0))
    var = tk.StringVar()
    cb  = ttk.Combobox(parent, textvariable=var, values=values,
                       state="readonly", width=width)
    cb.grid(row=row+1, column=col, sticky="ew", pady=(2, 0))
    if values:
        cb.current(0)
    return var, cb

def make_tree(parent, columns, headings, widths, height=12):
    frame = ttk.Frame(parent)
    frame.pack(fill="both", expand=True, pady=(0, 0))
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=height)
    for col, head, w in zip(columns, headings, widths):
        tree.heading(col, text=head,
                     command=lambda c=col, t=tree: sort_tree(t, c, False))
        tree.column(col, width=w, anchor="w")
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    return tree

def sort_tree(tree, col, reverse):
    data = [(tree.set(k, col), k) for k in tree.get_children("")]
    try:
        data.sort(key=lambda x: float(x[0]) if x[0] else 0, reverse=reverse)
    except ValueError:
        data.sort(key=lambda x: x[0].lower(), reverse=reverse)
    for idx, (_, k) in enumerate(data):
        tree.move(k, "", idx)
    tree.heading(col, command=lambda: sort_tree(tree, col, not reverse))

def stat_card(parent, title, value, col):
    f = ttk.Frame(parent, style="Card.TFrame", padding=16)
    f.grid(row=0, column=col, padx=6, pady=6, sticky="nsew")
    ttk.Label(f, text=value, style="Stat.TLabel").pack(anchor="w")
    ttk.Label(f, text=title, style="StatSub.TLabel").pack(anchor="w")

# ─────────────────────────── DIALOGS ───────────────────────────

class UserDialog(tk.Toplevel):
    def __init__(self, parent, title="Add User", data=None):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=DARK_BG)
        self.resizable(False, False)
        self.result = None
        self._build(data)
        self.grab_set()
        self.wait_window()

    def _build(self, data):
        f = ttk.Frame(self, padding=20)
        f.pack(fill="both", expand=True)
        ttk.Label(f, text="Username", style="Sub.TLabel").grid(row=0, column=0, sticky="w", pady=(0,2))
        self.username = ttk.Entry(f, width=30)
        self.username.grid(row=1, column=0, sticky="ew", pady=(0,8))
        ttk.Label(f, text="Email", style="Sub.TLabel").grid(row=2, column=0, sticky="w", pady=(0,2))
        self.email = ttk.Entry(f, width=30)
        self.email.grid(row=3, column=0, sticky="ew", pady=(0,8))
        ttk.Label(f, text="Account Type", style="Sub.TLabel").grid(row=4, column=0, sticky="w", pady=(0,2))
        self.acc_var = tk.StringVar(value="Basic")
        ttk.Combobox(f, textvariable=self.acc_var, values=["Basic","Premium"],
                     state="readonly", width=28).grid(row=5, column=0, sticky="ew", pady=(0,12))
        if data:
            self.username.insert(0, data.get("Username",""))
            self.email.insert(0, data.get("Email",""))
            self.acc_var.set(data.get("AccountType","Basic"))
        bf = ttk.Frame(f)
        bf.grid(row=6, column=0, sticky="ew")
        ttk.Button(bf, text="Save", command=self._save).pack(side="right", padx=(6,0))
        ttk.Button(bf, text="Cancel", command=self.destroy, style="Danger.TButton").pack(side="right")

    def _save(self):
        u = self.username.get().strip()
        e = self.email.get().strip()
        if not u or not e:
            messagebox.showwarning("Missing", "Username and Email are required.", parent=self)
            return
        self.result = {"username": u, "email": e, "account_type": self.acc_var.get()}
        self.destroy()


class PostDialog(tk.Toplevel):
    def __init__(self, parent, users):
        super().__init__(parent)
        self.title("Add Post")
        self.configure(bg=DARK_BG)
        self.resizable(False, False)
        self.result = None
        self._build(users)
        self.grab_set()
        self.wait_window()

    def _build(self, users):
        f = ttk.Frame(self, padding=20)
        f.pack(fill="both", expand=True)
        ttk.Label(f, text="User", style="Sub.TLabel").grid(row=0, column=0, sticky="w", pady=(0,2))
        self.user_var = tk.StringVar()
        user_names = [f"{u['UserID']}: {u['Username']}" for u in users]
        cb = ttk.Combobox(f, textvariable=self.user_var, values=user_names,
                          state="readonly", width=30)
        cb.grid(row=1, column=0, sticky="ew", pady=(0,8))
        if user_names: cb.current(0)
        ttk.Label(f, text="Post Type", style="Sub.TLabel").grid(row=2, column=0, sticky="w", pady=(0,2))
        self.type_var = tk.StringVar(value="Text")
        ttk.Combobox(f, textvariable=self.type_var, values=["Text","Image","Video"],
                     state="readonly", width=30).grid(row=3, column=0, sticky="ew", pady=(0,8))
        ttk.Label(f, text="Content", style="Sub.TLabel").grid(row=4, column=0, sticky="w", pady=(0,2))
        self.content = tk.Text(f, width=34, height=5, bg=ENTRY_BG, fg=TEXT_PRI,
                               insertbackground=TEXT_PRI, relief="flat", font=("Segoe UI", 10))
        self.content.grid(row=5, column=0, sticky="ew", pady=(0,12))
        bf = ttk.Frame(f)
        bf.grid(row=6, column=0, sticky="ew")
        ttk.Button(bf, text="Post", command=self._save).pack(side="right", padx=(6,0))
        ttk.Button(bf, text="Cancel", command=self.destroy, style="Danger.TButton").pack(side="right")

    def _save(self):
        if not self.user_var.get():
            messagebox.showwarning("Missing", "Select a user.", parent=self)
            return
        uid = int(self.user_var.get().split(":")[0])
        self.result = {
            "user_id": uid,
            "post_type": self.type_var.get(),
            "content": self.content.get("1.0", "end").strip()
        }
        self.destroy()


class InteractionDialog(tk.Toplevel):
    def __init__(self, parent, posts, users):
        super().__init__(parent)
        self.title("Add Interaction")
        self.configure(bg=DARK_BG)
        self.resizable(False, False)
        self.result = None
        self._build(posts, users)
        self.grab_set()
        self.wait_window()

    def _build(self, posts, users):
        f = ttk.Frame(self, padding=20)
        f.pack(fill="both", expand=True)
        ttk.Label(f, text="Post", style="Sub.TLabel").grid(row=0, column=0, sticky="w", pady=(0,2))
        self.post_var = tk.StringVar()
        post_items = [f"{p['PostID']}: {p['ContentText'][:30] if p['ContentText'] else '(no text)'}…" for p in posts]
        cb = ttk.Combobox(f, textvariable=self.post_var, values=post_items, state="readonly", width=32)
        cb.grid(row=1, column=0, sticky="ew", pady=(0,8))
        if post_items: cb.current(0)
        ttk.Label(f, text="User", style="Sub.TLabel").grid(row=2, column=0, sticky="w", pady=(0,2))
        self.user_var = tk.StringVar()
        user_items = [f"{u['UserID']}: {u['Username']}" for u in users]
        cb2 = ttk.Combobox(f, textvariable=self.user_var, values=user_items, state="readonly", width=32)
        cb2.grid(row=3, column=0, sticky="ew", pady=(0,8))
        if user_items: cb2.current(0)
        ttk.Label(f, text="Interaction Type", style="Sub.TLabel").grid(row=4, column=0, sticky="w", pady=(0,2))
        self.itype_var = tk.StringVar(value="Like")
        ttk.Combobox(f, textvariable=self.itype_var, values=["Like","Share","Comment"],
                     state="readonly", width=32).grid(row=5, column=0, sticky="ew", pady=(0,8))
        ttk.Label(f, text="Duration Viewed (sec, optional)", style="Sub.TLabel").grid(row=6, column=0, sticky="w", pady=(0,2))
        self.duration = ttk.Entry(f, width=34)
        self.duration.grid(row=7, column=0, sticky="ew", pady=(0,12))
        bf = ttk.Frame(f)
        bf.grid(row=8, column=0, sticky="ew")
        ttk.Button(bf, text="Save", command=self._save).pack(side="right", padx=(6,0))
        ttk.Button(bf, text="Cancel", command=self.destroy, style="Danger.TButton").pack(side="right")

    def _save(self):
        try:
            pid = int(self.post_var.get().split(":")[0])
            uid = int(self.user_var.get().split(":")[0])
        except (ValueError, IndexError):
            messagebox.showwarning("Missing", "Select post and user.", parent=self)
            return
        dur = None
        if self.duration.get().strip():
            try:
                dur = float(self.duration.get().strip())
            except ValueError:
                messagebox.showwarning("Invalid", "Duration must be a number.", parent=self)
                return
        self.result = {
            "post_id": pid, "user_id": uid,
            "interaction_type": self.itype_var.get(), "duration": dur
        }
        self.destroy()


class FollowerDialog(tk.Toplevel):
    def __init__(self, parent, users):
        super().__init__(parent)
        self.title("Add Follow")
        self.configure(bg=DARK_BG)
        self.resizable(False, False)
        self.result = None
        self._build(users)
        self.grab_set()
        self.wait_window()

    def _build(self, users):
        f = ttk.Frame(self, padding=20)
        f.pack(fill="both", expand=True)
        user_items = [f"{u['UserID']}: {u['Username']}" for u in users]
        ttk.Label(f, text="Follower", style="Sub.TLabel").grid(row=0, column=0, sticky="w", pady=(0,2))
        self.follower_var = tk.StringVar()
        cb1 = ttk.Combobox(f, textvariable=self.follower_var, values=user_items, state="readonly", width=30)
        cb1.grid(row=1, column=0, sticky="ew", pady=(0,8))
        if user_items: cb1.current(0)
        ttk.Label(f, text="Following", style="Sub.TLabel").grid(row=2, column=0, sticky="w", pady=(0,2))
        self.following_var = tk.StringVar()
        cb2 = ttk.Combobox(f, textvariable=self.following_var, values=user_items, state="readonly", width=30)
        cb2.grid(row=3, column=0, sticky="ew", pady=(0,12))
        if len(user_items) > 1: cb2.current(1)
        bf = ttk.Frame(f)
        bf.grid(row=4, column=0, sticky="ew")
        ttk.Button(bf, text="Save", command=self._save).pack(side="right", padx=(6,0))
        ttk.Button(bf, text="Cancel", command=self.destroy, style="Danger.TButton").pack(side="right")

    def _save(self):
        try:
            fid = int(self.follower_var.get().split(":")[0])
            gid = int(self.following_var.get().split(":")[0])
        except (ValueError, IndexError):
            messagebox.showwarning("Missing", "Select both users.", parent=self)
            return
        if fid == gid:
            messagebox.showwarning("Invalid", "A user cannot follow themselves.", parent=self)
            return
        self.result = {"follower_id": fid, "following_id": gid}
        self.destroy()

# ─────────────────────────── TABS ───────────────────────────

class UsersTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()
        self.load()

    def _build(self):
        top = ttk.Frame(self, padding=(12, 10, 12, 6))
        top.pack(fill="x")
        ttk.Label(top, text="Users", style="H2.TLabel").pack(side="left")
        ttk.Button(top, text="+ Add User", command=self._add).pack(side="right", padx=3)
        ttk.Button(top, text="Edit", command=self._edit).pack(side="right", padx=3)
        ttk.Button(top, text="Delete", command=self._delete, style="Danger.TButton").pack(side="right", padx=3)
        ttk.Button(top, text="Refresh", command=self.load).pack(side="right", padx=3)

        sf = ttk.Frame(self, padding=(12, 0))
        sf.pack(fill="x")
        ttk.Label(sf, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.load())
        ttk.Entry(sf, textvariable=self.search_var, width=22).pack(side="left", padx=6)

        cols = ("ID","Username","Email","Joined","Account")
        self.tree = make_tree(
            self, cols, cols,
            [50, 140, 200, 140, 80]
        )

    def load(self, *_):
        self.tree.delete(*self.tree.get_children())
        q = f"%{self.search_var.get()}%"
        conn = get_conn()
        rows = conn.execute("""
            SELECT u.UserID, u.Username, u.Email, u.JoinDate, a.TypeName
            FROM Users u JOIN AccountTypes a USING(AccountTypeID)
            WHERE u.Username LIKE ? OR u.Email LIKE ?
            ORDER BY u.UserID
        """, (q, q)).fetchall()
        conn.close()
        for r in rows:
            self.tree.insert("", "end", values=(r[0], r[1], r[2], r[3][:16], r[4]))

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a row first.")
            return None
        return self.tree.item(sel[0])["values"][0]

    def _add(self):
        dlg = UserDialog(self)
        if dlg.result:
            conn = get_conn()
            try:
                aid = conn.execute("SELECT AccountTypeID FROM AccountTypes WHERE TypeName=?",
                                   (dlg.result["account_type"],)).fetchone()[0]
                conn.execute("INSERT INTO Users(Username,Email,AccountTypeID) VALUES(?,?,?)",
                             (dlg.result["username"], dlg.result["email"], aid))
                conn.commit()
                self.load()
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

    def _edit(self):
        uid = self._selected_id()
        if uid is None: return
        conn = get_conn()
        row = conn.execute("""
            SELECT u.Username, u.Email, a.TypeName AS AccountType
            FROM Users u JOIN AccountTypes a USING(AccountTypeID)
            WHERE u.UserID=?
        """, (uid,)).fetchone()
        conn.close()
        if not row: return
        dlg = UserDialog(self, "Edit User", dict(row))
        if dlg.result:
            conn = get_conn()
            try:
                aid = conn.execute("SELECT AccountTypeID FROM AccountTypes WHERE TypeName=?",
                                   (dlg.result["account_type"],)).fetchone()[0]
                conn.execute("UPDATE Users SET Username=?,Email=?,AccountTypeID=? WHERE UserID=?",
                             (dlg.result["username"], dlg.result["email"], aid, uid))
                conn.commit()
                self.load()
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

    def _delete(self):
        uid = self._selected_id()
        if uid is None: return
        if not messagebox.askyesno("Confirm", f"Delete user ID {uid}? This will cascade to posts and interactions."):
            return
        conn = get_conn()
        conn.execute("DELETE FROM Users WHERE UserID=?", (uid,))
        conn.commit()
        conn.close()
        self.load()


class PostsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()
        self.load()

    def _build(self):
        top = ttk.Frame(self, padding=(12, 10, 12, 6))
        top.pack(fill="x")
        ttk.Label(top, text="Posts", style="H2.TLabel").pack(side="left")
        ttk.Button(top, text="+ Add Post", command=self._add).pack(side="right", padx=3)
        ttk.Button(top, text="Delete", command=self._delete, style="Danger.TButton").pack(side="right", padx=3)
        ttk.Button(top, text="Refresh", command=self.load).pack(side="right", padx=3)

        sf = ttk.Frame(self, padding=(12, 0))
        sf.pack(fill="x")
        ttk.Label(sf, text="Filter by type:").pack(side="left")
        self.type_var = tk.StringVar(value="All")
        ttk.Combobox(sf, textvariable=self.type_var,
                     values=["All","Text","Image","Video"],
                     state="readonly", width=10).pack(side="left", padx=6)
        self.type_var.trace_add("write", lambda *_: self.load())

        cols = ("ID","Author","Type","Content","Posted")
        self.tree = make_tree(self, cols, cols, [50, 120, 70, 280, 140])

    def load(self, *_):
        self.tree.delete(*self.tree.get_children())
        ft = self.type_var.get()
        conn = get_conn()
        q = "SELECT p.PostID, u.Username, pt.TypeName, p.ContentText, p.PostTimestamp FROM Posts p JOIN Users u USING(UserID) JOIN PostTypes pt USING(PostTypeID)"
        if ft != "All":
            rows = conn.execute(q + " WHERE pt.TypeName=? ORDER BY p.PostTimestamp DESC", (ft,)).fetchall()
        else:
            rows = conn.execute(q + " ORDER BY p.PostTimestamp DESC").fetchall()
        conn.close()
        for r in rows:
            snippet = (r[3] or "")[:60].replace("\n", " ")
            self.tree.insert("", "end", values=(r[0], r[1], r[2], snippet, r[4][:16]))

    def _add(self):
        conn = get_conn()
        users = conn.execute("SELECT UserID, Username FROM Users ORDER BY Username").fetchall()
        conn.close()
        if not users:
            messagebox.showinfo("No users", "Add at least one user first.")
            return
        dlg = PostDialog(self, users)
        if dlg.result:
            conn = get_conn()
            try:
                pid = conn.execute("SELECT PostTypeID FROM PostTypes WHERE TypeName=?",
                                   (dlg.result["post_type"],)).fetchone()[0]
                conn.execute("INSERT INTO Posts(UserID,ContentText,PostTypeID) VALUES(?,?,?)",
                             (dlg.result["user_id"], dlg.result["content"], pid))
                conn.commit()
                self.load()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

    def _delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a row first.")
            return
        pid = self.tree.item(sel[0])["values"][0]
        if not messagebox.askyesno("Confirm", f"Delete post ID {pid}?"):
            return
        conn = get_conn()
        conn.execute("DELETE FROM Posts WHERE PostID=?", (pid,))
        conn.commit()
        conn.close()
        self.load()


class InteractionsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()
        self.load()

    def _build(self):
        top = ttk.Frame(self, padding=(12, 10, 12, 6))
        top.pack(fill="x")
        ttk.Label(top, text="Interactions", style="H2.TLabel").pack(side="left")
        ttk.Button(top, text="+ Add", command=self._add).pack(side="right", padx=3)
        ttk.Button(top, text="Delete", command=self._delete, style="Danger.TButton").pack(side="right", padx=3)
        ttk.Button(top, text="Refresh", command=self.load).pack(side="right", padx=3)

        cols = ("ID","Post","User","Type","Duration","At")
        self.tree = make_tree(self, cols, cols, [50, 90, 120, 80, 80, 130])

    def load(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_conn()
        rows = conn.execute("""
            SELECT i.InteractionID, i.PostID, u.Username, it.TypeName,
                   i.DurationViewed, i.InteractedAt
            FROM Interactions i
            JOIN Users u ON i.UserID=u.UserID
            JOIN InteractionTypes it ON i.InteractionTypeID=it.InteractionTypeID
            ORDER BY i.InteractedAt DESC
        """).fetchall()
        conn.close()
        for r in rows:
            dur = f"{r[4]:.1f}s" if r[4] is not None else "-"
            self.tree.insert("", "end", values=(r[0], r[1], r[2], r[3], dur, r[5][:16]))

    def _add(self):
        conn = get_conn()
        posts = conn.execute("SELECT PostID, ContentText FROM Posts ORDER BY PostID").fetchall()
        users = conn.execute("SELECT UserID, Username FROM Users ORDER BY Username").fetchall()
        conn.close()
        if not posts or not users:
            messagebox.showinfo("Missing data", "Need at least one post and one user.")
            return
        dlg = InteractionDialog(self, posts, users)
        if dlg.result:
            conn = get_conn()
            try:
                iid = conn.execute("SELECT InteractionTypeID FROM InteractionTypes WHERE TypeName=?",
                                   (dlg.result["interaction_type"],)).fetchone()[0]
                conn.execute("""
                    INSERT INTO Interactions(PostID,UserID,InteractionTypeID,DurationViewed)
                    VALUES(?,?,?,?)
                """, (dlg.result["post_id"], dlg.result["user_id"], iid, dlg.result["duration"]))
                conn.commit()
                self.load()
            except sqlite3.IntegrityError as e:
                messagebox.showerror("Duplicate", f"This interaction already exists.\n{e}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

    def _delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a row first.")
            return
        iid = self.tree.item(sel[0])["values"][0]
        if not messagebox.askyesno("Confirm", f"Delete interaction ID {iid}?"):
            return
        conn = get_conn()
        conn.execute("DELETE FROM Interactions WHERE InteractionID=?", (iid,))
        conn.commit()
        conn.close()
        self.load()


class FollowersTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()
        self.load()

    def _build(self):
        top = ttk.Frame(self, padding=(12, 10, 12, 6))
        top.pack(fill="x")
        ttk.Label(top, text="Followers", style="H2.TLabel").pack(side="left")
        ttk.Button(top, text="+ Add Follow", command=self._add).pack(side="right", padx=3)
        ttk.Button(top, text="Unfollow", command=self._delete, style="Danger.TButton").pack(side="right", padx=3)
        ttk.Button(top, text="Refresh", command=self.load).pack(side="right", padx=3)

        sf = ttk.Frame(self, padding=(12, 0))
        sf.pack(fill="x")
        ttk.Label(sf, text="Show follows for user:").pack(side="left")
        self.filter_var = tk.StringVar(value="All")
        self.filter_cb = ttk.Combobox(sf, textvariable=self.filter_var, state="readonly", width=18)
        self.filter_cb.pack(side="left", padx=6)
        self.filter_var.trace_add("write", lambda *_: self.load())

        cols = ("Follower","Following","Since")
        self.tree = make_tree(self, cols, cols, [180, 180, 140])
        self._refresh_filter_users()

    def _refresh_filter_users(self):
        conn = get_conn()
        users = conn.execute("SELECT Username FROM Users ORDER BY Username").fetchall()
        conn.close()
        names = ["All"] + [u[0] for u in users]
        self.filter_cb["values"] = names

    def load(self, *_):
        self.tree.delete(*self.tree.get_children())
        self._refresh_filter_users()
        conn = get_conn()
        flt = self.filter_var.get()
        if flt == "All":
            rows = conn.execute("""
                SELECT u1.Username, u2.Username, f.FollowedAt
                FROM Followers f
                JOIN Users u1 ON f.FollowerID=u1.UserID
                JOIN Users u2 ON f.FollowingID=u2.UserID
                ORDER BY f.FollowedAt DESC
            """).fetchall()
        else:
            rows = conn.execute("""
                SELECT u1.Username, u2.Username, f.FollowedAt
                FROM Followers f
                JOIN Users u1 ON f.FollowerID=u1.UserID
                JOIN Users u2 ON f.FollowingID=u2.UserID
                WHERE u1.Username=? OR u2.Username=?
                ORDER BY f.FollowedAt DESC
            """, (flt, flt)).fetchall()
        conn.close()
        for r in rows:
            self.tree.insert("", "end", values=(r[0], r[1], r[2][:16]))

    def _add(self):
        conn = get_conn()
        users = conn.execute("SELECT UserID, Username FROM Users ORDER BY Username").fetchall()
        conn.close()
        if len(users) < 2:
            messagebox.showinfo("Not enough users", "Need at least 2 users to create a follow.")
            return
        dlg = FollowerDialog(self, users)
        if dlg.result:
            conn = get_conn()
            try:
                conn.execute("INSERT INTO Followers(FollowerID,FollowingID) VALUES(?,?)",
                             (dlg.result["follower_id"], dlg.result["following_id"]))
                conn.commit()
                self.load()
            except sqlite3.IntegrityError:
                messagebox.showerror("Duplicate", "This follow relationship already exists.")
            finally:
                conn.close()

    def _delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a row first.")
            return
        vals = self.tree.item(sel[0])["values"]
        if not messagebox.askyesno("Confirm", f"Remove follow: {vals[0]} → {vals[1]}?"):
            return
        conn = get_conn()
        conn.execute("""
            DELETE FROM Followers WHERE
            FollowerID=(SELECT UserID FROM Users WHERE Username=?)
            AND FollowingID=(SELECT UserID FROM Users WHERE Username=?)
        """, (vals[0], vals[1]))
        conn.commit()
        conn.close()
        self.load()


class DashboardTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()
        self.load()

    def _build(self):
        top = ttk.Frame(self, padding=(12, 10, 12, 0))
        top.pack(fill="x")
        ttk.Label(top, text="Dashboard", style="H2.TLabel").pack(side="left")
        ttk.Button(top, text="Refresh", command=self.load).pack(side="right")

        self.stats_frame = ttk.Frame(self, padding=(12, 8))
        self.stats_frame.pack(fill="x")
        for i in range(5):
            self.stats_frame.columnconfigure(i, weight=1)

        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=12, pady=4)

        mid = ttk.Frame(self, padding=(12, 0))
        mid.pack(fill="both", expand=True)
        mid.columnconfigure(0, weight=1)
        mid.columnconfigure(1, weight=1)

        lf = ttk.LabelFrame(mid, text=" Top Users by Posts ", padding=8)
        lf.grid(row=0, column=0, sticky="nsew", padx=(0,6), pady=6)
        self.top_posts_tree = make_tree(lf, ("User","Posts"), ("User","Posts"), [160, 60], height=7)

        rf = ttk.LabelFrame(mid, text=" Post Type Distribution ", padding=8)
        rf.grid(row=0, column=1, sticky="nsew", padx=(6,0), pady=6)
        self.post_type_tree = make_tree(rf, ("Type","Count"), ("Type","Count"), [130, 80], height=7)

        bf = ttk.LabelFrame(mid, text=" Most Interacted Posts ", padding=8)
        bf.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=6)
        self.top_inter_tree = make_tree(bf, ("PostID","Author","Type","Content","Interactions"),
                                        ("Post ID","Author","Type","Content","# Interactions"),
                                        [60, 100, 70, 300, 100], height=6)

    def load(self):
        for w in self.stats_frame.winfo_children():
            w.destroy()
        conn = get_conn()
        n_users  = conn.execute("SELECT COUNT(*) FROM Users").fetchone()[0]
        n_posts  = conn.execute("SELECT COUNT(*) FROM Posts").fetchone()[0]
        n_ints   = conn.execute("SELECT COUNT(*) FROM Interactions").fetchone()[0]
        n_fols   = conn.execute("SELECT COUNT(*) FROM Followers").fetchone()[0]
        n_prem   = conn.execute("SELECT COUNT(*) FROM Users WHERE AccountTypeID=2").fetchone()[0]

        for i, (title, val) in enumerate([
            ("Total Users", n_users), ("Total Posts", n_posts),
            ("Interactions", n_ints), ("Follows", n_fols), ("Premium Users", n_prem)
        ]):
            stat_card(self.stats_frame, title, str(val), i)

        self.top_posts_tree.delete(*self.top_posts_tree.get_children())
        for r in conn.execute("""
            SELECT u.Username, COUNT(*) as c FROM Posts p
            JOIN Users u USING(UserID) GROUP BY u.UserID ORDER BY c DESC LIMIT 10
        """).fetchall():
            self.top_posts_tree.insert("", "end", values=(r[0], r[1]))

        self.post_type_tree.delete(*self.post_type_tree.get_children())
        for r in conn.execute("""
            SELECT pt.TypeName, COUNT(*) FROM Posts p
            JOIN PostTypes pt USING(PostTypeID) GROUP BY pt.PostTypeID
        """).fetchall():
            self.post_type_tree.insert("", "end", values=(r[0], r[1]))

        self.top_inter_tree.delete(*self.top_inter_tree.get_children())
        for r in conn.execute("""
            SELECT p.PostID, u.Username, pt.TypeName, p.ContentText,
                   COUNT(i.InteractionID) as ic
            FROM Posts p
            JOIN Users u ON p.UserID=u.UserID
            JOIN PostTypes pt ON p.PostTypeID=pt.PostTypeID
            LEFT JOIN Interactions i ON p.PostID=i.PostID
            GROUP BY p.PostID ORDER BY ic DESC LIMIT 10
        """).fetchall():
            snippet = (r[3] or "")[:55].replace("\n", " ")
            self.top_inter_tree.insert("", "end", values=(r[0], r[1], r[2], snippet, r[4]))

        conn.close()


class SQLTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()

    def _build(self):
        top = ttk.Frame(self, padding=(12, 10, 12, 6))
        top.pack(fill="x")
        ttk.Label(top, text="SQL Query Runner", style="H2.TLabel").pack(side="left")

        qf = ttk.Frame(self, padding=(12, 0))
        qf.pack(fill="x")
        self.query_box = tk.Text(qf, height=6, bg=ENTRY_BG, fg=TEXT_PRI,
                                 insertbackground=TEXT_PRI, font=("Cascadia Code", 10),
                                 relief="flat", wrap="none")
        self.query_box.pack(fill="x", pady=(0, 6))
        self.query_box.insert("1.0", "SELECT u.Username, COUNT(p.PostID) AS posts\nFROM Users u\nLEFT JOIN Posts p USING(UserID)\nGROUP BY u.UserID\nORDER BY posts DESC;")

        bf = ttk.Frame(self, padding=(12, 0))
        bf.pack(fill="x")
        ttk.Button(bf, text="Run Query", command=self._run).pack(side="left", padx=(0,6))
        ttk.Button(bf, text="Clear", command=lambda: self.query_box.delete("1.0","end")).pack(side="left")
        self.status = ttk.Label(bf, text="", style="Sub.TLabel")
        self.status.pack(side="right")

        rf = ttk.Frame(self, padding=(12, 6))
        rf.pack(fill="both", expand=True)
        self.result_frame = rf
        self.result_tree = None

    def _run(self):
        q = self.query_box.get("1.0", "end").strip()
        if not q:
            return
        if self.result_tree:
            self.result_tree.destroy()
        conn = get_conn()
        try:
            cur = conn.execute(q)
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description] if cur.description else []
            widths = [max(80, min(200, len(c)*10)) for c in cols]
            self.result_tree = make_tree(self.result_frame, cols, cols, widths, height=14)
            for r in rows:
                self.result_tree.insert("", "end", values=tuple(r))
            conn.commit()
            self.status.config(text=f"{len(rows)} row(s) returned.", foreground=SUCCESS)
        except Exception as e:
            self.status.config(text=str(e), foreground=DANGER)
        finally:
            conn.close()

# ─────────────────────────── MAIN WINDOW ───────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Social Media DB Manager")
        self.geometry("1040x680")
        self.minsize(820, 560)
        self.configure(bg=DARK_BG)
        apply_styles(self)
        self._build()

    def _build(self):
        header = ttk.Frame(self, padding=(18, 12, 18, 8))
        header.pack(fill="x")
        ttk.Label(header, text="Social Media DB", style="H1.TLabel").pack(side="left")
        db_lbl = ttk.Label(header, text=f"  {os.path.abspath(DB_PATH)}", style="Sub.TLabel")
        db_lbl.pack(side="left", padx=(4,0))

        ttk.Separator(self, orient="horizontal").pack(fill="x")

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        self.dash  = DashboardTab(nb)
        self.users = UsersTab(nb)
        self.posts = PostsTab(nb)
        self.ints  = InteractionsTab(nb)
        self.fols  = FollowersTab(nb)
        self.sql   = SQLTab(nb)

        nb.add(self.dash,  text="  Dashboard  ")
        nb.add(self.users, text="  Users  ")
        nb.add(self.posts, text="  Posts  ")
        nb.add(self.ints,  text="  Interactions  ")
        nb.add(self.fols,  text="  Followers  ")
        nb.add(self.sql,   text="  SQL Runner  ")

        nb.bind("<<NotebookTabChanged>>", self._on_tab)

    def _on_tab(self, event):
        tab = event.widget.tab("current", "text").strip()
        if tab == "Dashboard":   self.dash.load()
        elif tab == "Users":     self.users.load()
        elif tab == "Posts":     self.posts.load()
        elif tab == "Interactions": self.ints.load()
        elif tab == "Followers": self.fols.load()

if __name__ == "__main__":
    init_db()
    app = App()
    app.mainloop()


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
