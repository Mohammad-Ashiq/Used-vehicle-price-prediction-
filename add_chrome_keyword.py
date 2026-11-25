import sqlite3
import uuid
import time
import os
import glob

def register_keyword():
    base_dir = r"C:\Users\786mo\AppData\Local\Google\Chrome\User Data"
    profiles = ["Profile 2", "Default", "Profile 1"]
    
    found_any = False
    for prof in profiles:
        db_path = os.path.join(base_dir, prof, "Web Data")
        if not os.path.isfile(db_path):
            continue
        
        try:
            conn = sqlite3.connect(db_path, timeout=5)
            cur = conn.cursor()
            
            # Check existing
            cur.execute("SELECT id, keyword, url FROM keywords WHERE keyword = 'revahan';")
            existing = cur.fetchone()
            if existing:
                print(f"[{prof}] 'revahan' keyword already exists: {existing}")
                # Update URL just in case
                cur.execute("UPDATE keywords SET url = 'http://127.0.0.1:5000/?q={searchTerms}', is_active = 1 WHERE keyword = 'revahan';")
                conn.commit()
                print(f"[{prof}] Updated 'revahan' shortcut url!")
            else:
                sync_guid = str(uuid.uuid4())
                now = int(time.time())
                cur.execute("""
                    INSERT INTO keywords (
                        short_name, keyword, favicon_url, url, safe_for_autoreplace,
                        originating_url, date_created, usage_count, input_encodings,
                        suggest_url, prepopulate_id, created_by_policy, last_modified,
                        sync_guid, alternate_urls, image_url, search_url_post_params,
                        suggest_url_post_params, image_url_post_params, new_tab_url,
                        last_visited, created_from_play_api, is_active, starter_pack_id,
                        enforced_by_policy, featured_by_policy, url_hash
                    ) VALUES (
                        'ReVahan', 'revahan', 'http://127.0.0.1:5000/static/images/favicon.ico',
                        'http://127.0.0.1:5000/?q={searchTerms}', 0,
                        '', ?, 100, 'UTF-8',
                        '', 0, 0, ?,
                        ?, '[]', '', '',
                        '', '', 'http://127.0.0.1:5000',
                        ?, 0, 1, 0,
                        0, 0, ''
                    );
                """, (now, now, sync_guid, now))
                conn.commit()
                print(f"[{prof}] Successfully registered 'revahan' shortcut in Chrome!")
            
            conn.close()
            found_any = True
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                print(f"[{prof}] Chrome is currently running and locking the database.")
            else:
                print(f"[{prof}] Database error: {e}")
        except Exception as e:
            print(f"[{prof}] Error: {e}")
            
    return found_any

if __name__ == "__main__":
    register_keyword()
