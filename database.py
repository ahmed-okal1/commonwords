import sqlite3
import os

DB_NAME = "vocabulary.db"

import sys

def get_db_path():
    # Use a safe fallback for the log
    log_file = os.path.join(os.path.expanduser("~"), "english_mastery_debug.log")
    def debug_log(msg):
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[DB_PATH_LOG] {msg}\n")
        except: pass

    try:
        # Detect Android
        is_android = os.environ.get("ANDROID_ARGUMENT") or os.environ.get("ANDROID_BOOTLOGO")
        
        if is_android:
            debug_log("Android detected")
            base_path = os.environ.get("FILES_DIR", os.path.expanduser("~"))
        elif getattr(sys, 'frozen', False):
            debug_log("Frozen (executable) detected")
            base_path = os.path.dirname(sys.executable)
            
            # Ultra-safe check for write permissions
            test_file = os.path.join(base_path, ".write_test")
            can_write = False
            try:
                with open(test_file, "w") as f: f.write("test")
                os.remove(test_file)
                can_write = True
            except:
                debug_log("Program folder is READ-ONLY")

            if not can_write:
                app_data = os.getenv('APPDATA')
                if not app_data:
                    app_data = os.path.expanduser('~')
                base_path = os.path.join(app_data, 'EnglishMasteryApp')
                if not os.path.exists(base_path):
                    os.makedirs(base_path)
                debug_log(f"Using APPDATA fallback: {base_path}")
        else:
            debug_log("Source mode detected")
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        final_path = os.path.join(base_path, DB_NAME)
        debug_log(f"Final Path: {final_path}")
        return final_path
    except Exception as e:
        debug_log(f"CRITICAL ERROR in get_db_path: {str(e)}")
        # Ultimate fallback
        return os.path.join(os.path.expanduser("~"), DB_NAME)

def get_db_connection():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Users table
    # current_level: 1-6
    # current_word_index: Index of the word the user is currently on in that level
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    current_level INTEGER DEFAULT 1,
                    current_word_index INTEGER DEFAULT 0,
                    score INTEGER DEFAULT 0
                )''')

    # Words table
    c.execute('''CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level INTEGER NOT NULL,
                    english_word TEXT NOT NULL,
                    arabic_word TEXT NOT NULL,
                    audio_path TEXT
                )''')
    
    # Per-level progress table
    c.execute('''CREATE TABLE IF NOT EXISTS level_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    level INTEGER NOT NULL,
                    word_index INTEGER DEFAULT 0,
                    UNIQUE(username, level)
                )''')

    # Word errors table - tracks wrong attempts
    c.execute('''CREATE TABLE IF NOT EXISTS word_errors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    word_id INTEGER NOT NULL,
                    error_count INTEGER DEFAULT 0,
                    UNIQUE(username, word_id)
                )''')

    conn.commit()
    conn.close()

def get_user(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return user

def create_user(username):
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute('INSERT INTO users (username) VALUES (?)', (username,))
        conn.commit()
        user_id = cur.lastrowid
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        return user
    except sqlite3.IntegrityError:
        conn.close()
        return get_user(username)

def get_words_by_level(level):
    conn = get_db_connection()
    words = conn.execute('SELECT * FROM words WHERE level = ? ORDER BY id', (level,)).fetchall()
    conn.close()
    return [dict(w) for w in words]

def update_user_progress(username, level, index, score_increment=0):
    conn = get_db_connection()
    conn.execute('''UPDATE users 
                    SET current_level = ?, current_word_index = ?, score = score + ? 
                    WHERE username = ?''', 
                 (level, index, score_increment, username))
    conn.commit()
    conn.close()

def reset_user_progress_for_level(username, level):
    conn = get_db_connection()
    conn.execute('UPDATE users SET current_level = ? WHERE username = ?', (level, username))
    # Reset per-level progress
    conn.execute('INSERT OR REPLACE INTO level_progress (username, level, word_index) VALUES (?, ?, 0)', (username, level))
    conn.commit()
    conn.close()

def get_level_progress(username, level):
    """Get the saved word index for a specific level."""
    conn = get_db_connection()
    row = conn.execute('SELECT word_index FROM level_progress WHERE username = ? AND level = ?', (username, level)).fetchone()
    conn.close()
    return row['word_index'] if row else 0

def set_level_progress(username, level, word_index):
    """Save word index for a specific level."""
    conn = get_db_connection()
    conn.execute('INSERT OR REPLACE INTO level_progress (username, level, word_index) VALUES (?, ?, ?)', (username, level, word_index))
    conn.commit()
    conn.close()

def delete_word(word_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM words WHERE id = ?', (word_id,))
    conn.commit()
    conn.close()

def delete_words_bulk(word_ids):
    if not word_ids:
        return
    conn = get_db_connection()
    placeholders = ','.join('?' for _ in word_ids)
    conn.execute(f'DELETE FROM words WHERE id IN ({placeholders})', word_ids)
    conn.commit()
    conn.close()

def update_word(word_id, english_word, arabic_word):
    conn = get_db_connection()
    conn.execute('UPDATE words SET english_word = ?, arabic_word = ? WHERE id = ?', 
                 (english_word, arabic_word, word_id))
    conn.commit()
    conn.close()

def get_word_count_by_level():
    conn = get_db_connection()
    rows = conn.execute('SELECT level, count(*) as cnt FROM words GROUP BY level ORDER BY level').fetchall()
    conn.close()
    return {r['level']: r['cnt'] for r in rows}

def increment_word_error(username, word_id):
    """Increment error count for a word."""
    conn = get_db_connection()
    conn.execute('''INSERT INTO word_errors (username, word_id, error_count) 
                    VALUES (?, ?, 1)
                    ON CONFLICT(username, word_id) 
                    DO UPDATE SET error_count = error_count + 1''', (username, word_id))
    conn.commit()
    conn.close()

def get_difficult_words(username, min_errors=3):
    """Get words where user made errors >= min_errors."""
    conn = get_db_connection()
    rows = conn.execute('''SELECT w.id, w.level, w.english_word, w.arabic_word, we.error_count
                           FROM word_errors we
                           JOIN words w ON we.word_id = w.id
                           WHERE we.username = ? AND we.error_count >= ?
                           ORDER BY we.error_count DESC''', (username, min_errors)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def remove_from_difficult(username, word_id):
    """Remove a word from difficult list (reset error count)."""
    conn = get_db_connection()
    conn.execute('DELETE FROM word_errors WHERE username = ? AND word_id = ?', (username, word_id))
    conn.commit()
    conn.close()
