import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import io
import requests
from opds_browser import OPDSBrowser
import json
import os
import argparse
import logging

def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
            logging.debug("Loaded environment variables from .env file")
        except ImportError:
            logging.warning("python-dotenv not installed, skipping .env file")
        except Exception as e:
            logging.warning(f"Error loading .env file: {e}")

def setup_logging(config):
    """Setup logging based on configuration and environment variables"""
    # Load .env file first
    load_env_file()
    
    # Check environment variables first
    disable_logs = os.getenv('OPDS_DISABLE_LOGS', '').lower() == 'true'
    env_log_level = os.getenv('OPDS_LOG_LEVEL', '').upper()
    
    # Check config file
    config_logging = config.get('logging', {})
    config_enabled = config_logging.get('enabled', True)
    config_level = config_logging.get('level', 'INFO').upper()
    
    # Determine final settings
    if disable_logs or not config_enabled:
        logging.getLogger().setLevel(logging.ERROR)
        return
    
    # Set log level
    if env_log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
        log_level = getattr(logging, env_log_level)
    elif config_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
        log_level = getattr(logging, config_level)
    else:
        log_level = logging.INFO
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s:%(message)s',
        force=True
    )

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

class OPDSBrowserGUI:
    def __init__(self, root, catalog_url=None):
        self.root = root
        self.root.title('OPDS Catalog Browser')
        self.config = self.load_config()
        
        # Setup logging based on config and environment
        setup_logging(self.config)
        
        self.catalogs = self.config.get('catalogs', [])
        
        # Get default catalog from environment or config
        default_catalog = os.getenv('OPDS_DEFAULT_CATALOG')
        self.catalog_url = catalog_url or default_catalog or self.config.get('last_catalog_url')
        
        # If no catalogs in config, create default from environment
        if not self.catalogs and default_catalog:
            self.catalogs = [{'name': 'Default', 'url': default_catalog}]
        elif not self.catalogs:
            # Fallback to Flibusta if nothing is configured
            self.catalogs = [{'name': 'Flibusta', 'url': 'https://flibusta.is/opds'}]
            self.catalog_url = self.catalog_url or 'https://flibusta.is/opds'
        
        self.last_entry_id = self.config.get('last_entry_id')
        self.last_entry_path = self.config.get('last_entry_path') # Initialize new attribute
        self.browser = OPDSBrowser(self.catalog_url)
        self.entries = []
        self.covers = {}
        self.icons = self.create_icons()
        self.setup_widgets()
        self.load_feed()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_config(self):
        self.config['catalogs'] = self.catalogs
        self.config['last_catalog_url'] = self.catalog_url
        self.config['last_entry_id'] = self.last_entry_id
        self.config['last_entry_path'] = self.last_entry_path
        
        # Preserve logging settings if they exist
        if 'logging' not in self.config:
            self.config['logging'] = {'enabled': True, 'level': 'INFO'}
        
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def create_icons(self):
        # Create simple icons for folder and book
        folder_img = tk.PhotoImage(width=16, height=16)
        # Draw a yellow folder
        folder_img.put("#FFD700", to=(2, 6, 13, 13))
        folder_img.put("#FFD700", to=(4, 4, 11, 6))
        book_img = tk.PhotoImage(width=16, height=16)
        # Draw a blue book
        book_img.put("#4682B4", to=(3, 3, 13, 13))
        book_img.put("#FFFFFF", to=(5, 5, 11, 11))
        return {'folder': folder_img, 'book': book_img}

    def setup_widgets(self):
        # Catalog selection
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(top_frame, text='Catalog:').pack(side='left')
        self.catalog_var = tk.StringVar(value=self.catalog_url)
        self.catalog_combo = ttk.Combobox(top_frame, textvariable=self.catalog_var, state='readonly', width=40)
        self.catalog_combo['values'] = [c['url'] for c in self.catalogs]
        self.catalog_combo.pack(side='left', padx=5)
        self.catalog_combo.bind('<<ComboboxSelected>>', self.on_catalog_select)
        add_btn = ttk.Button(top_frame, text='+', width=2, command=self.add_catalog_dialog)
        add_btn.pack(side='left')

        # Search bar
        search_frame = ttk.Frame(self.root)
        search_frame.pack(fill='x', padx=5, pady=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side='left', fill='x', expand=True)
        search_entry.bind('<Return>', lambda e: self.on_search())
        search_btn = ttk.Button(search_frame, text='Search', command=self.on_search)
        search_btn.pack(side='left', padx=5)

        # Treeview for entries with icons
        self.tree = ttk.Treeview(self.root, show='tree', selectmode='browse', height=20)
        self.tree.pack(fill='both', expand=True, padx=5, pady=5)
        self.tree.bind('<<TreeviewSelect>>', self.on_select_entry)

        # Book details
        self.details_frame = ttk.Frame(self.root)
        self.details_frame.pack(fill='x', padx=5, pady=5)
        self.cover_label = ttk.Label(self.details_frame)
        self.cover_label.grid(row=0, column=0, rowspan=3, sticky='nw')
        self.title_var = tk.StringVar()
        self.author_var = tk.StringVar()
        self.summary_var = tk.StringVar()
        ttk.Label(self.details_frame, textvariable=self.title_var, font=('Arial', 12, 'bold')).grid(row=0, column=1, sticky='w')
        ttk.Label(self.details_frame, textvariable=self.author_var, font=('Arial', 10)).grid(row=1, column=1, sticky='w')
        ttk.Label(self.details_frame, textvariable=self.summary_var, wraplength=400, font=('Arial', 9)).grid(row=2, column=1, sticky='w')
        self.attachments_frame = ttk.Frame(self.details_frame)
        self.attachments_frame.grid(row=3, column=1, sticky='w', pady=(5,0))

        # Navigation buttons
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(fill='x', padx=5, pady=5)
        self.up_btn = ttk.Button(nav_frame, text='Up', command=self.go_up)
        self.up_btn.pack(side='left')
        self.back_btn = ttk.Button(nav_frame, text='Back', command=self.go_back)
        self.back_btn.pack(side='left')
        self.prev_btn = ttk.Button(nav_frame, text='Previous', command=lambda: self.navigate('previous'))
        self.prev_btn.pack(side='left')
        self.next_btn = ttk.Button(nav_frame, text='Next', command=lambda: self.navigate('next'))
        self.next_btn.pack(side='left', padx=5)
        self.home_btn = ttk.Button(nav_frame, text='Home', command=lambda: self.navigate('start'))
        self.home_btn.pack(side='left')

    def on_catalog_select(self, event=None):
        self.catalog_url = self.catalog_var.get()
        self.browser = OPDSBrowser(self.catalog_url)
        self.save_config()
        self.load_feed()

    def add_catalog_dialog(self):
        win = tk.Toplevel(self.root)
        win.title('Add Catalog')
        ttk.Label(win, text='Catalog Name:').pack(padx=5, pady=2)
        name_var = tk.StringVar()
        ttk.Entry(win, textvariable=name_var).pack(padx=5, pady=2)
        ttk.Label(win, text='Catalog URL:').pack(padx=5, pady=2)
        url_var = tk.StringVar()
        ttk.Entry(win, textvariable=url_var).pack(padx=5, pady=2)
        def add():
            name = name_var.get().strip()
            url = url_var.get().strip()
            if name and url:
                self.catalogs.append({'name': name, 'url': url})
                self.catalog_combo['values'] = [c['url'] for c in self.catalogs]
                self.catalog_var.set(url)
                self.on_catalog_select()
                self.save_config()
                win.destroy()
        ttk.Button(win, text='Add', command=add).pack(pady=5)

    def load_feed(self):
        try:
            self.browser.fetch_feed()
            self.entries = self.browser.get_entries()
            self.update_tree()
            self.update_nav_buttons()
            # Restore last position if available
            if self.last_entry_path:
                self.restore_entry_path(self.last_entry_path, select_last_only=True)
            elif self.last_entry_id:
                for idx, entry in enumerate(self.entries):
                    if entry['id'] == self.last_entry_id:
                        self.tree.selection_set(str(idx))
                        self.tree.see(str(idx))
                        self.on_select_entry(None)
                        break
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def update_tree(self):
        self.tree.delete(*self.tree.get_children())
        for idx, entry in enumerate(self.entries):
            entry_type = entry.get('type', 'book')
            icon = self.icons.get(entry_type, self.icons['book'])
            if entry_type == 'folder':
                display = f"{entry['title']}"
            else:
                display = f"{entry['title']} - {entry['author']}"
            self.tree.insert('', 'end', iid=str(idx), text=display, image=icon)
        self.clear_details()

    def update_nav_buttons(self):
        nav = self.browser.get_navigation_links()
        self.prev_btn['state'] = 'normal' if 'previous' in nav else 'disabled'
        self.next_btn['state'] = 'normal' if 'next' in nav else 'disabled'
        self.home_btn['state'] = 'normal' if 'start' in nav else 'disabled'
        self.back_btn['state'] = 'normal' if getattr(self.browser, 'history', None) else 'disabled'
        # Enable Up only if not at root (path length > 0)
        up_enabled = self.last_entry_path and len(self.last_entry_path) > 0
        logging.debug(f"[NAV] Up enabled: {up_enabled}, last_entry_path: {self.last_entry_path}")
        self.up_btn['state'] = 'normal' if up_enabled else 'disabled'

    def on_search(self):
        query = self.search_var.get().strip()
        if not query:
            self.load_feed()
            return
        try:
            self.browser.search(query)
            self.entries = self.browser.get_entries()
            self.update_tree()
            self.update_nav_buttons()
        except Exception as e:
            messagebox.showerror('Search Error', str(e))

    def navigate(self, rel):
        try:
            self.browser.go_to(rel)
            self.entries = self.browser.get_entries()
            self.update_tree()
            self.update_nav_buttons()
        except Exception as e:
            messagebox.showerror('Navigation Error', str(e))

    def go_back(self):
        try:
            self.browser.go_back()
            self.entries = self.browser.get_entries()
            self.update_tree()
            self.update_nav_buttons()
        except Exception as e:
            messagebox.showerror('Back Navigation Error', str(e))

    def go_up(self):
        logging.debug(f"[UP] Before: last_entry_path={self.last_entry_path}, last_entry_id={self.last_entry_id}")
        if not self.last_entry_path or len(self.last_entry_path) == 0:
            logging.debug("[UP] Already at root, nothing to do.")
            return
        
        # Navigate back to the parent level
        old_path = list(self.last_entry_path)
        new_path = self.last_entry_path[:-1]
        
        # First, navigate to the parent level
        if new_path:
            # Reset browser to root and navigate to the parent level
            self.browser.reset_to_root()
            self.entries = self.browser.get_entries()
            self.update_tree()
            
            # Now restore the path to the parent level
            self.restore_entry_path(new_path, select_last_only=True)
            
            # Update our path tracking
            self.last_entry_path = new_path
            self.last_entry_id = new_path[-1] if new_path else None
            self.save_config()
            
            logging.debug(f"[UP] After: new_path={new_path}, new_id={self.last_entry_id}")
        else:
            # Going to root
            self.browser.reset_to_root()
            self.entries = self.browser.get_entries()
            self.update_tree()
            self.last_entry_path = []
            self.last_entry_id = None
            self.save_config()
            logging.debug("[UP] Reset to root")
        
        self.update_nav_buttons()

    def on_select_entry(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        idx = int(selected[0])
        entry = self.entries[idx]
        self.last_entry_id = entry.get('id')
        # Save full path: all parent folder ids + current entry id
        self.last_entry_path = self.browser.get_path_ids() + [entry.get('id')]
        self.save_config()
        if entry.get('type') == 'folder' and entry.get('url'):
            try:
                self.browser.fetch_feed(entry['url'], parent_id=entry.get('id'))
                self.entries = self.browser.get_entries()
                self.update_tree()
                self.update_nav_buttons()
            except Exception as e:
                messagebox.showerror('Navigation Error', str(e))
            return
        self.title_var.set(entry['title'])
        self.author_var.set(entry['author'])
        self.summary_var.set(entry['summary'])
        if entry['cover']:
            self.show_cover(entry['cover'])
        else:
            self.cover_label.config(image='')
            self.cover_label.image = None
        self.show_attachments(entry.get('attachments', []))

    def show_cover(self, url):
        try:
            if url in self.covers:
                img = self.covers[url]
            else:
                resp = requests.get(url)
                resp.raise_for_status()
                img_data = resp.content
                pil_img = Image.open(io.BytesIO(img_data)).resize((80, 120))
                img = ImageTk.PhotoImage(pil_img)
                self.covers[url] = img
            self.cover_label.config(image=img)
            self.cover_label.image = img
        except Exception:
            self.cover_label.config(image='')
            self.cover_label.image = None

    def show_attachments(self, attachments):
        for widget in self.attachments_frame.winfo_children():
            widget.destroy()
        if not attachments:
            return
        ttk.Label(self.attachments_frame, text='Attachments:', font=('Arial', 9, 'bold')).pack(anchor='w')
        for att in attachments:
            text = f"{att['rel'] or 'file'} ({att['type']})"
            link = ttk.Label(self.attachments_frame, text=text, foreground='blue', cursor='hand2', font=('Arial', 9, 'underline'))
            link.pack(anchor='w')
            link.bind('<Button-1>', lambda e, url=att['url']: self.open_url(url))

    def open_url(self, url):
        import webbrowser
        webbrowser.open(url)

    def clear_details(self):
        self.title_var.set('')
        self.author_var.set('')
        self.summary_var.set('')
        self.cover_label.config(image='')
        self.cover_label.image = None
        for widget in self.attachments_frame.winfo_children():
            widget.destroy()

    def get_entry_path(self, idx):
        # Traverse up the history to build the path of IDs
        # For now, just use the current stack of URLs in browser.history
        # (Assumes each navigation is a folder, which is true for OPDS)
        path = []
        for url in self.browser.history:
            # Try to find the entry id for this url in the entries at that level
            # Not perfect, but works for linear navigation
            # Could be improved by storing (id, url) pairs
            pass  # Placeholder for future improvement
        path.append(self.entries[idx].get('id'))
        return path

    def restore_entry_path(self, path, select_last_only=False):
        logging.debug(f"[RESTORE] Start path: {path}, select_last_only={select_last_only}")
        if not path:
            logging.debug("[RESTORE] Empty path, nothing to restore.")
            return
        self.browser.path_ids = []  # Reset path stack before replaying
        current_path = list(path)
        while current_path:
            target_id = current_path.pop(0)
            found = False
            for idx, entry in enumerate(self.entries):
                logging.debug(f"[RESTORE] Checking entry idx={idx}, id={entry['id']}, type={entry.get('type')}")
                if entry['id'] == target_id:
                    self.tree.selection_set(str(idx))
                    self.tree.see(str(idx))
                    logging.debug(f"[RESTORE] Found id={target_id} at idx={idx}, current_path={current_path}")
                    if entry.get('type') == 'folder' and entry.get('url') and current_path:
                        self.browser.fetch_feed(entry['url'], parent_id=entry.get('id'))
                        self.entries = self.browser.get_entries()
                        self.update_tree()
                        self.update_nav_buttons()
                    elif not current_path and select_last_only:
                        logging.debug(f"[RESTORE] Select only, not entering: {entry['id']}")
                        pass
                    else:
                        logging.debug(f"[RESTORE] on_select_entry for {entry['id']}")
                        self.on_select_entry(None)
                    found = True
                    break
            if not found:
                logging.debug(f"[RESTORE] id={target_id} not found in current entries.")
                break

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--catalog', type=str, help='OPDS catalog URL to use')
    args = parser.parse_args()
    root = tk.Tk()
    app = OPDSBrowserGUI(root, catalog_url=args.catalog)
    root.mainloop() 