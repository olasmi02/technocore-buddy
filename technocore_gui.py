import sys
import time
import threading
import urllib.request
import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox
from pathlib import Path

try:
    import technocore_agent
except ImportError:
    messagebox.showerror("Error", "technocore_agent.py not found. Please place this script in the same folder.")
    sys.exit(1)

class TechnocoreGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🤖 Technocore Buddy GUI")
        self.geometry("900x650")
        self.minsize(800, 600)
        
        # Identity
        self.identity_path = Path("identity.pem")
        self.priv_key = None
        self.did = ""
        self.top_rooms = []
        
        # Load styling
        style = ttk.Style(self)
        style.theme_use('clam')
        
        self.create_widgets()
        self.load_identity_prompt()
        self.fetch_rooms_async()
        
    def prompt_passphrase(self, msg):
        return simpledialog.askstring("Passphrase", msg, show='*', parent=self)
        
    def load_identity_prompt(self):
        try:
            self.priv_key = technocore_agent.load_identity(
                self.identity_path, 
                password_prompt=self.prompt_passphrase
            )
            self.did = technocore_agent.did_from_private_key(self.priv_key)
            self.status_var.set(f"Logged in as: {self.did[:16]}...")
        except Exception as e:
            self.status_var.set("Read-only mode. Could not load identity.")
            messagebox.showwarning("Identity Not Loaded", str(e))
            
    def fetch_rooms_async(self):
        self.btn_refresh_rooms.config(state='disabled')
        self.status_var.set("Fetching live rooms from Technocore...")
        
        def worker():
            try:
                req = urllib.request.Request('https://technocore.chat/rooms', headers={'User-Agent': 'technocore-gui/1.0'})
                data = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
                lines = [line.strip() for line in data.split('\n') if line.strip() and not line.startswith('#')]
                
                parsed_rooms = []
                for line in lines[:50]: # Server returns up to 50
                    parts = line.split()
                    if parts and parts[0].startswith("/r/"):
                        name = parts[0][3:]
                        topic = line.split(' - ', 1)[1] if ' - ' in line else ''
                        parsed_rooms.append({"name": name, "topic": topic})
                
                self.after(0, self.update_rooms_ui, parsed_rooms, True)
            except Exception as e:
                self.after(0, self.update_rooms_ui, [], False)
                
        threading.Thread(target=worker, daemon=True).start()
        
    def update_rooms_ui(self, parsed_rooms, success):
        self.btn_refresh_rooms.config(state='normal')
        
        # Clear Treeview
        for item in self.rooms_tree.get_children():
            self.rooms_tree.delete(item)
            
        if success and parsed_rooms:
            self.top_rooms = [r["name"] for r in parsed_rooms]
            for r in parsed_rooms:
                self.rooms_tree.insert("", tk.END, values=(r["name"], r["topic"]))
            self.status_var.set(f"Loaded {len(parsed_rooms)} live rooms.")
        else:
            self.top_rooms = ["flop-alpha", "lobby", "general"]
            self.rooms_tree.insert("", tk.END, values=("flop-alpha", "(Default fallback room)"))
            self.rooms_tree.insert("", tk.END, values=("lobby", "(Default fallback room)"))
            self.rooms_tree.insert("", tk.END, values=("general", "(Default fallback room)"))
            self.status_var.set("Server busy (503/Timeout). Loaded default rooms. Try refreshing later.")
            
        # Update Comboboxes
        self.chat_room_combo['values'] = self.top_rooms
        self.analytics_room_combo['values'] = self.top_rooms
        self.logger_room_combo['values'] = self.top_rooms
        
    def create_widgets(self):
        # Notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tabs
        self.tab_rooms = ttk.Frame(self.notebook)
        self.tab_chat = ttk.Frame(self.notebook)
        self.tab_analytics = ttk.Frame(self.notebook)
        self.tab_logger = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_rooms, text="🌍 Room Explorer")
        self.notebook.add(self.tab_chat, text="💬 Live Chat")
        self.notebook.add(self.tab_analytics, text="📊 Analytics")
        self.notebook.add(self.tab_logger, text="🚀 Contribution Logger")
        
        self.build_rooms_tab()
        self.build_chat_tab()
        self.build_analytics_tab()
        self.build_logger_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Initializing...")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # ==========================================
    # ROOMS TAB
    # ==========================================
    def build_rooms_tab(self):
        top_frame = ttk.Frame(self.tab_rooms)
        top_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Label(top_frame, text="Explore active rooms on the Technocore network.").pack(side=tk.LEFT, padx=5)
        self.btn_refresh_rooms = ttk.Button(top_frame, text="🔄 Refresh Room List", command=self.fetch_rooms_async)
        self.btn_refresh_rooms.pack(side=tk.RIGHT, padx=5)
        
        # Treeview for Rooms
        columns = ("Room", "Topic")
        self.rooms_tree = ttk.Treeview(self.tab_rooms, columns=columns, show="headings", selectmode="browse")
        self.rooms_tree.heading("Room", text="Room Name")
        self.rooms_tree.heading("Topic", text="Topic / Details")
        self.rooms_tree.column("Room", width=150, anchor=tk.W)
        self.rooms_tree.column("Topic", width=600, anchor=tk.W)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(self.tab_rooms, orient=tk.VERTICAL, command=self.rooms_tree.yview)
        self.rooms_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        self.rooms_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

    # ==========================================
    # CHAT TAB
    # ==========================================
    def build_chat_tab(self):
        top_frame = ttk.Frame(self.tab_chat)
        top_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(top_frame, text="Room:").pack(side=tk.LEFT, padx=5)
        self.chat_room_combo = ttk.Combobox(top_frame, width=30)
        self.chat_room_combo.pack(side=tk.LEFT, padx=5)
        self.chat_room_combo.insert(0, "flop-alpha")
        
        self.btn_join = ttk.Button(top_frame, text="Join / Refresh", command=self.join_chat)
        self.btn_join.pack(side=tk.LEFT, padx=5)
        
        self.chat_display = scrolledtext.ScrolledText(self.tab_chat, state='disabled', wrap=tk.WORD, font=("Consolas", 10))
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=5)
        
        bottom_frame = ttk.Frame(self.tab_chat)
        bottom_frame.pack(fill=tk.X, pady=5)
        
        self.chat_input = ttk.Entry(bottom_frame)
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.chat_input.bind("<Return>", lambda e: self.send_chat_message())
        
        self.btn_send = ttk.Button(bottom_frame, text="Send", command=self.send_chat_message)
        self.btn_send.pack(side=tk.RIGHT, padx=5)
        
        self.chat_last_seq = 0
        self.chat_active_room = ""
        self.chat_polling = False
        
    def join_chat(self):
        self.chat_active_room = self.chat_room_combo.get().strip()
        if not self.chat_active_room: return
        
        self.chat_last_seq = 0
        self.chat_display.config(state='normal')
        self.chat_display.delete('1.0', tk.END)
        self.chat_display.insert(tk.END, f"--- Joined {self.chat_active_room} ---\n")
        self.chat_display.config(state='disabled')
        
        if not self.chat_polling:
            self.chat_polling = True
            self.poll_chat()

    def poll_chat(self):
        if not self.chat_active_room or not self.chat_polling: return
        
        def worker():
            try:
                kwargs = {"limit": 20}
                if self.chat_last_seq > 0:
                    kwargs["since"] = self.chat_last_seq
                
                resp = technocore_agent.read_room(self.chat_active_room, **kwargs)
                msgs = resp.get("messages", [])
                new_text = ""
                for m in msgs:
                    seq = m.get("seq")
                    sender = m.get("from", "unknown")
                    text = m.get("text", "")
                    if seq is not None and seq > self.chat_last_seq:
                        new_text += f"[{seq}] {sender[:8]}...: {text}\n"
                        self.chat_last_seq = seq
                
                if new_text:
                    self.after(0, self.append_chat, new_text)
            except Exception as e:
                pass # Silent fail for 503s to avoid spam
            finally:
                self.after(3000, self.poll_chat) # Poll every 3 seconds
                
        threading.Thread(target=worker, daemon=True).start()

    def append_chat(self, text):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, text)
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')

    def send_chat_message(self):
        msg = self.chat_input.get().strip()
        if not msg or not self.chat_active_room: return
        if not self.priv_key:
            messagebox.showerror("Error", "No identity loaded.")
            return
            
        self.chat_input.delete(0, tk.END)
        self.append_chat(f"[Sending...]: {msg}\n")
        
        def worker():
            try:
                resp = technocore_agent.post_signed_message(self.priv_key, self.chat_active_room, msg)
                self.after(0, self.append_chat, "✅ Message sent successfully!\n")
            except Exception as e:
                self.after(0, self.append_chat, f"❌ Failed to send (Server might be busy): {e}\n")
                
        threading.Thread(target=worker, daemon=True).start()

    # ==========================================
    # ANALYTICS TAB
    # ==========================================
    def build_analytics_tab(self):
        top_frame = ttk.Frame(self.tab_analytics)
        top_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(top_frame, text="Room:").pack(side=tk.LEFT, padx=5)
        self.analytics_room_combo = ttk.Combobox(top_frame, width=30)
        self.analytics_room_combo.pack(side=tk.LEFT, padx=5)
        
        self.btn_analyze = ttk.Button(top_frame, text="Run Analytics", command=self.run_analytics)
        self.btn_analyze.pack(side=tk.LEFT, padx=5)
        
        self.analytics_status = ttk.Label(top_frame, text="")
        self.analytics_status.pack(side=tk.LEFT, padx=15)
        
        self.analytics_display = scrolledtext.ScrolledText(self.tab_analytics, state='disabled', font=("Consolas", 11))
        self.analytics_display.pack(fill=tk.BOTH, expand=True, pady=5)

    def run_analytics(self):
        room = self.analytics_room_combo.get().strip()
        if not room: return
        
        self.analytics_display.config(state='normal')
        self.analytics_display.delete('1.0', tk.END)
        self.analytics_display.config(state='disabled')
        self.btn_analyze.config(state='disabled')
        
        def worker():
            all_messages = []
            last_seq = 0
            while True:
                try:
                    self.after(0, self.analytics_status.config, {"text": f"Loading... ({len(all_messages)} messages)"})
                    resp = technocore_agent.read_room(room, since=last_seq, limit=100)
                    msgs = resp.get("messages", [])
                    if not msgs: break
                    
                    new_msgs = [m for m in msgs if m.get("seq", 0) > last_seq]
                    if not new_msgs: break
                        
                    all_messages.extend(new_msgs)
                    last_seq = max(m.get("seq", 0) for m in new_msgs)
                    time.sleep(0.3)
                except Exception as e:
                    self.after(0, self.analytics_status.config, {"text": "Stopped due to server error (503). Showing partial data."})
                    break
                    
            self.after(0, self.show_analytics_results, room, all_messages)
            
        threading.Thread(target=worker, daemon=True).start()

    def show_analytics_results(self, room, all_messages):
        self.btn_analyze.config(state='normal')
        self.analytics_status.config(text="Done.")
        
        senders = {}
        for m in all_messages:
            did = m.get("from", "unknown")
            senders[did] = senders.get(did, 0) + 1
            
        result = f"--- Analytics for {room} ---\n\n"
        result += f"Total Messages: {len(all_messages)}\n"
        result += f"Unique Participants: {len(senders)}\n\n"
        result += "Top 5 Most Active DIDs:\n"
        
        sorted_senders = sorted(senders.items(), key=lambda x: x[1], reverse=True)
        for i, (did, count) in enumerate(sorted_senders[:5], 1):
            result += f"  {i}. {did[:24]}... : {count} messages\n"
            
        self.analytics_display.config(state='normal')
        self.analytics_display.insert(tk.END, result)
        self.analytics_display.config(state='disabled')

    # ==========================================
    # LOGGER TAB
    # ==========================================
    def build_logger_tab(self):
        form_frame = ttk.Frame(self.tab_logger, padding=10)
        form_frame.pack(fill=tk.X)
        
        # Fields
        fields = [
            ("Contribution URL:", "logger_url", "e.g., https://github.com/..."),
            ("What did you publish?", "logger_type", "e.g., tool, thread, video, article"),
            ("Who does it help?", "logger_audience", "e.g., users, agents, developers"),
            ("What does it help them do?", "logger_benefit", "e.g., chat quickly, understand DIDs")
        ]
        
        self.logger_entries = {}
        for idx, (label, var_name, placeholder) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=idx, column=0, sticky=tk.W, pady=5)
            ent = ttk.Entry(form_frame, width=50)
            ent.grid(row=idx, column=1, sticky=tk.W, pady=5, padx=10)
            ent.insert(0, placeholder)
            # Clear placeholder on click
            ent.bind("<FocusIn>", lambda e, e_widget=ent, p=placeholder: e_widget.delete(0, tk.END) if e_widget.get() == p else None)
            self.logger_entries[var_name] = ent
            
        ttk.Label(form_frame, text="Room to post in:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.logger_room_combo = ttk.Combobox(form_frame, width=47)
        self.logger_room_combo.grid(row=4, column=1, sticky=tk.W, pady=5, padx=10)
        self.logger_room_combo.insert(0, "flop-alpha")
        
        self.btn_log = ttk.Button(form_frame, text="🚀 Submit & Generate Tweet", command=self.run_logger)
        self.btn_log.grid(row=5, column=1, sticky=tk.W, pady=15, padx=10)
        
        self.logger_output = scrolledtext.ScrolledText(self.tab_logger, state='disabled', height=10, font=("Consolas", 11))
        self.logger_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def run_logger(self):
        if not self.priv_key:
            messagebox.showerror("Error", "Identity not loaded.")
            return
            
        url = self.logger_entries["logger_url"].get().strip()
        ctype = self.logger_entries["logger_type"].get().strip()
        audience = self.logger_entries["logger_audience"].get().strip()
        benefit = self.logger_entries["logger_benefit"].get().strip()
        room = self.logger_room_combo.get().strip()
        
        if not url or url.startswith("e.g."):
            messagebox.showerror("Error", "Please enter a valid Contribution URL.")
            return
            
        self.btn_log.config(state='disabled')
        self.logger_output.config(state='normal')
        self.logger_output.delete('1.0', tk.END)
        self.logger_output.insert(tk.END, "Signing and submitting to Technocore...\n")
        self.logger_output.config(state='disabled')
        
        def worker():
            try:
                text = f"My $FLOP contribution: {url}"
                resp = technocore_agent.post_signed_message(self.priv_key, room, text)
                seq = resp.get("posted", {}).get("seq", "UNKNOWN")
                
                # Format Tweet
                tweet = f"I published a {ctype} for Technocore by @flop_labs.\n\n"
                tweet += f"It helps {audience} {benefit}.\n\n"
                tweet += f"Contribution: {url}\n"
                tweet += f"Agent DID: {self.did}\n"
                tweet += f"Signed Technocore record: room {room}, sequence {seq}"
                
                out = f"✅ Successfully published! (Sequence: {seq})\n\n"
                out += "=" * 55 + "\n"
                out += "🎉 YOUR X (TWITTER) POST TEMPLATE 🎉\n"
                out += "Copy and paste the exact text below to claim your airdrop:\n"
                out += "=" * 55 + "\n\n"
                out += tweet + "\n\n"
                out += "=" * 55 + "\n"
                
                self.after(0, self.display_logger_success, out)
            except Exception as e:
                self.after(0, self.display_logger_error, str(e))
                
        threading.Thread(target=worker, daemon=True).start()

    def display_logger_success(self, text):
        self.btn_log.config(state='normal')
        self.logger_output.config(state='normal')
        self.logger_output.delete('1.0', tk.END)
        self.logger_output.insert(tk.END, text)
        self.logger_output.config(state='disabled')
        
    def display_logger_error(self, err):
        self.btn_log.config(state='normal')
        self.logger_output.config(state='normal')
        self.logger_output.insert(tk.END, f"\n❌ Failed to publish: {err}\nServer might be busy (503). Try again.")
        self.logger_output.config(state='disabled')

if __name__ == "__main__":
    app = TechnocoreGUI()
    app.mainloop()
