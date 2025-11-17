import os
import shutil
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from datetime import datetime
from languages import LANGUAGES

PROFILE_DIR = "profiles"

class BatchAddWindow(tk.Toplevel):
    def __init__(self, parent, lang_dict):
        super().__init__(parent)
        self.transient(parent); self.grab_set(); self.result = None; self.lang_dict = lang_dict
        self.title(self.lang_dict['batch_add_prompt_title'])
        main_frame = ttk.Frame(self, padding="10"); main_frame.pack(fill="both", expand=True)
        ttk.Label(main_frame, text=self.lang_dict['batch_add_prompt_msg']).pack(padx=5, pady=5, anchor="w")
        text_frame = ttk.Frame(main_frame); text_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.text = tk.Text(text_frame, width=60, height=10, wrap="word"); self.text.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text.yview); scrollbar.pack(side="right", fill="y"); self.text.config(yscrollcommand=scrollbar.set)
        btn_frame = ttk.Frame(main_frame); btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text=self.lang_dict['ok_btn'], command=self.on_ok).pack(side="left", padx=10)
        ttk.Button(btn_frame, text=self.lang_dict['cancel_btn'], command=self.destroy).pack(side="left")
        self.resizable(True, True); self.text.focus_set()
    def on_ok(self): self.result = self.text.get("1.0", "end-1c").strip(); self.destroy()

class RuleEditorWindow(tk.Toplevel):
    def __init__(self, parent, lang_dict, rule_data=None, callback=None):
        super().__init__(parent)
        self.transient(parent); self.grab_set()
        self.lang_dict, self.rule_data, self.callback = lang_dict, rule_data or {}, callback
        self.title(self.lang_dict['rule_editor_edit_title'] if rule_data else self.lang_dict['rule_editor_add_title'])
        frame = ttk.Frame(self, padding="10"); frame.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1); self.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1); frame.grid_columnconfigure(3, weight=1)
        ttk.Label(frame, text=self.lang_dict['rule_name_label']).grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Entry(frame, width=40); self.name_entry.grid(row=0, column=1, columnspan=3, sticky="ew")
        ttk.Label(frame, text=self.lang_dict['keyword_label']).grid(row=1, column=0, sticky="w", pady=5)
        self.keyword_entry = ttk.Entry(frame, width=40); self.keyword_entry.grid(row=1, column=1, columnspan=3, sticky="ew")
        ttk.Label(frame, text=self.lang_dict['date_filter_label']).grid(row=2, column=0, sticky="w", pady=5)
        self.date_mode = tk.StringVar()
        self.date_mode_cb = ttk.Combobox(frame, textvariable=self.date_mode, values=self.lang_dict['date_options'], state="readonly")
        self.date_mode_cb.grid(row=2, column=1, columnspan=3, sticky="ew"); self.date_mode_cb.bind("<<ComboboxSelected>>", self.update_date_fields)
        self.date1_label = ttk.Label(frame, text="Date:"); self.date1_entry = ttk.Entry(frame, width=18)
        self.date2_label = ttk.Label(frame, text="To"); self.date2_entry = ttk.Entry(frame, width=18)
        self.date1_label.grid_remove(); self.date1_entry.grid_remove(); self.date2_label.grid_remove(); self.date2_entry.grid_remove()
        ttk.Label(frame, text=self.lang_dict['dest_folder_label']).grid(row=4, column=0, sticky="w", pady=5)
        self.dest_entry = ttk.Entry(frame, width=40); self.dest_entry.grid(row=4, column=1, columnspan=2, sticky="ew")
        ttk.Button(frame, text=self.lang_dict['browse_btn'], command=self.browse_dest).grid(row=4, column=3, padx=5)
        btn_frame = ttk.Frame(frame); btn_frame.grid(row=5, column=0, columnspan=4, pady=10)
        ttk.Button(btn_frame, text=self.lang_dict['save_btn'], command=self.save_rule).pack(side="left", padx=10)
        ttk.Button(btn_frame, text=self.lang_dict['cancel_btn'], command=self.destroy).pack(side="left")
        self.load_rule_data()
    def update_date_fields(self, event=None):
        mode = self.date_mode.get()
        self.date1_label.grid_remove(); self.date1_entry.grid_remove(); self.date2_label.grid_remove(); self.date2_entry.grid_remove()
        if mode in [self.lang_dict['date_options'][1], self.lang_dict['date_options'][2]]:
            self.date1_label.config(text=self.lang_dict['date_label']); self.date1_label.grid(row=3, column=0, sticky="w", pady=5, padx=5)
            self.date1_entry.grid(row=3, column=1, columnspan=3, sticky="w")
        elif mode == self.lang_dict['date_options'][3]:
            self.date1_label.config(text=self.lang_dict['date_from_label']); self.date1_label.grid(row=3, column=0, sticky="e", pady=5)
            self.date1_entry.grid(row=3, column=1, sticky="ew"); self.date2_label.config(text=self.lang_dict['date_to_label'])
            self.date2_label.grid(row=3, column=2, sticky="ew", padx=5); self.date2_entry.grid(row=3, column=3, sticky="ew")
    def load_rule_data(self):
        if not self.rule_data: self.date_mode_cb.set(self.lang_dict['date_options'][0]); return
        self.name_entry.insert(0, self.rule_data.get("name", "")); self.keyword_entry.insert(0, self.rule_data.get("keyword", ""))
        self.dest_entry.insert(0, self.rule_data.get("destination", ""))
        date_filter = self.rule_data.get("date_filter", {}); mode = date_filter.get("mode", "none")
        self.date_mode_cb.set(self.lang_dict['date_options'][{"none": 0, "after": 1, "before": 2, "between": 3}.get(mode, 0)])
        self.date1_entry.insert(0, date_filter.get("date1", "")); self.date2_entry.insert(0, date_filter.get("date2", "")); self.update_date_fields()
    def browse_dest(self):
        folder = filedialog.askdirectory();
        if folder: self.dest_entry.delete(0, tk.END); self.dest_entry.insert(0, folder)
    def save_rule(self):
        mode_map = {v: k for k, v in {"none": self.lang_dict['date_options'][0], "after": self.lang_dict['date_options'][1], "before": self.lang_dict['date_options'][2], "between": self.lang_dict['date_options'][3]}.items()}
        selected_mode = mode_map.get(self.date_mode.get(), "none"); date_filter = {"mode": selected_mode, "date1": "", "date2": ""}; date1_str, date2_str = self.date1_entry.get().strip(), self.date2_entry.get().strip()
        if selected_mode in ["after", "before"]:
            if not date1_str: messagebox.showerror(self.lang_dict['error_title'], self.lang_dict['rule_editor_error_date_empty'], parent=self); return
            try: datetime.strptime(date1_str, "%Y-%m-%d"); date_filter["date1"] = date1_str
            except ValueError: messagebox.showerror(self.lang_dict['error_title'], self.lang_dict['rule_editor_error_date_format'], parent=self); return
        elif selected_mode == "between":
            if not date1_str or not date2_str: messagebox.showerror(self.lang_dict['error_title'], self.lang_dict['rule_editor_error_start_end_date_empty'], parent=self); return
            try:
                d1, d2 = datetime.strptime(date1_str, "%Y-%m-%d"), datetime.strptime(date2_str, "%Y-%m-%d")
                if d1 > d2: messagebox.showerror(self.lang_dict['error_title'], self.lang_dict['rule_editor_error_date_order'], parent=self); return
                date_filter["date1"], date_filter["date2"] = date1_str, date2_str
            except ValueError: messagebox.showerror(self.lang_dict['error_title'], self.lang_dict['rule_editor_error_date_format'], parent=self); return
        new_rule = {"enabled": self.rule_data.get("enabled", True), "name": self.name_entry.get().strip(), "keyword": self.keyword_entry.get().strip(), "destination": self.dest_entry.get().strip(), "date_filter": date_filter}
        if not new_rule["name"] or not new_rule["destination"]: messagebox.showerror(self.lang_dict['error_title'], self.lang_dict['rule_editor_error_name_dest_empty'], parent=self); return
        if self.callback: self.callback(new_rule)
        self.destroy()

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent, self.rules, self.current_lang = parent, [], "zh_tw"
        self.lang_dict = LANGUAGES[self.current_lang]
        self.setup_ui(); self.refresh_profile_list(); self.update_ui_text()
    def setup_ui(self):
        main_frame = ttk.Frame(self, padding="10"); main_frame.pack(fill="both", expand=True)
        self.profile_frame = ttk.LabelFrame(main_frame, padding="10"); self.profile_frame.pack(fill="x", pady=5)
        self.profile_var = tk.StringVar()
        self.profile_menu = ttk.Combobox(self.profile_frame, textvariable=self.profile_var, state="readonly"); self.profile_menu.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.load_profile_btn = ttk.Button(self.profile_frame, command=self.load_profile); self.load_profile_btn.pack(side="left", padx=2)
        self.save_profile_btn = ttk.Button(self.profile_frame, command=self.save_profile); self.save_profile_btn.pack(side="left", padx=2)
        self.save_as_profile_btn = ttk.Button(self.profile_frame, command=self.save_as_profile); self.save_as_profile_btn.pack(side="left", padx=2)
        self.delete_profile_btn = ttk.Button(self.profile_frame, command=self.delete_profile); self.delete_profile_btn.pack(side="left", padx=2)
        self.paned_window = ttk.PanedWindow(main_frame, orient="vertical"); self.paned_window.pack(fill="both", expand=True, pady=5)
        top_pane = ttk.Frame(self.paned_window); self.paned_window.add(top_pane, weight=1)
        self.source_frame = ttk.LabelFrame(top_pane, padding="10"); self.source_frame.pack(fill="both", expand=True)
        self.source_listbox = tk.Listbox(self.source_frame, height=4, selectmode="extended"); self.source_listbox.pack(side="left", fill="both", expand=True)
        source_scrollbar = ttk.Scrollbar(self.source_frame, orient="vertical", command=self.source_listbox.yview); source_scrollbar.pack(side="left", fill="y"); self.source_listbox.config(yscrollcommand=source_scrollbar.set)
        source_btn_frame = ttk.Frame(self.source_frame); source_btn_frame.pack(side="left", fill="y", padx=5)
        self.add_source_btn = ttk.Button(source_btn_frame, command=self.add_source); self.add_source_btn.pack(pady=2, fill="x")
        self.batch_add_source_btn = ttk.Button(source_btn_frame, command=self.batch_add_sources); self.batch_add_source_btn.pack(pady=2, fill="x")
        self.remove_source_btn = ttk.Button(source_btn_frame, command=self.remove_source); self.remove_source_btn.pack(pady=2, fill="x")
        self.remove_all_sources_btn = ttk.Button(source_btn_frame, command=self.remove_all_sources); self.remove_all_sources_btn.pack(pady=2, fill="x")
        bottom_pane = ttk.Frame(self.paned_window); self.paned_window.add(bottom_pane, weight=3)
        self.rules_frame = ttk.LabelFrame(bottom_pane, padding="10"); self.rules_frame.pack(fill="both", expand=True)
        columns = ("enabled", "name", "keyword", "date_filter", "destination"); self.rules_tree = ttk.Treeview(self.rules_frame, columns=columns, show="headings", height=6); self.rules_tree.pack(side="left", fill="both", expand=True)
        rules_scrollbar = ttk.Scrollbar(self.rules_frame, orient="vertical", command=self.rules_tree.yview); rules_scrollbar.pack(side="left", fill="y"); self.rules_tree.config(yscrollcommand=rules_scrollbar.set); self.rules_tree.bind("<Button-1>", self.on_tree_click)
        rules_btn_frame = ttk.Frame(self.rules_frame); rules_btn_frame.pack(side="left", fill="y", padx=5)
        self.add_rule_btn = ttk.Button(rules_btn_frame, command=self.add_rule); self.add_rule_btn.pack(pady=2, fill="x")
        self.edit_rule_btn = ttk.Button(rules_btn_frame, command=self.edit_rule); self.edit_rule_btn.pack(pady=2, fill="x")
        self.copy_rule_btn = ttk.Button(rules_btn_frame, command=self.copy_rule); self.copy_rule_btn.pack(pady=2, fill="x")
        self.delete_rule_btn = ttk.Button(rules_btn_frame, command=self.delete_rule); self.delete_rule_btn.pack(pady=2, fill="x")
        self.recursive_var = tk.BooleanVar(value=True); self.recursive_checkbtn = ttk.Checkbutton(main_frame, variable=self.recursive_var); self.recursive_checkbtn.pack(anchor="w", pady=5)
        
        # <<< V2.2: 操作模式 UI ---
        self.mode_frame = ttk.LabelFrame(main_frame, padding="10")
        self.mode_frame.pack(fill="x", pady=5)
        self.operation_mode = tk.StringVar(value="copy")
        self.copy_radio = ttk.Radiobutton(self.mode_frame, variable=self.operation_mode, value="copy")
        self.copy_radio.pack(side="left", padx=5)
        self.move_radio = ttk.Radiobutton(self.mode_frame, variable=self.operation_mode, value="move")
        self.move_radio.pack(side="left", padx=5)

        self.conflict_frame = ttk.LabelFrame(main_frame, padding="10"); self.conflict_frame.pack(fill="x", pady=5)
        self.conflict_entry = ttk.Entry(self.conflict_frame); self.conflict_entry.pack(side="left", fill="x", expand=True)
        self.browse_conflict_btn = ttk.Button(self.conflict_frame, command=self.browse_conflict); self.browse_conflict_btn.pack(side="left", padx=5)
        action_frame = ttk.Frame(main_frame); action_frame.pack(fill="x", pady=5)
        self.start_button = ttk.Button(action_frame, command=self.start_classification, style="Accent.TButton"); self.start_button.pack(side="left", expand=True, fill="x", padx=(0,5), pady=5)
        self.lang_button = ttk.Button(action_frame, command=self.toggle_language); self.lang_button.pack(side="right", padx=(5,0), pady=5)
        self.log_frame = ttk.LabelFrame(main_frame, padding="10"); self.log_frame.pack(fill="both", expand=True, pady=5)
        self.log_text = tk.Text(self.log_frame, height=8, wrap="word"); self.log_text.pack(fill="both", expand=True)
        self.parent.protocol("WM_DELETE_WINDOW", self.on_closing)
    def get_current_settings_data(self):
        return {"sources": list(self.source_listbox.get(0, tk.END)), "recursive": self.recursive_var.get(), "rules": self.rules, "conflict_folder": self.conflict_entry.get(), "operation_mode": self.operation_mode.get()}
    def load_settings_from_data(self, settings):
        self.clear_all_settings()
        for src in settings.get("sources", []): self.source_listbox.insert(tk.END, src)
        self.recursive_var.set(settings.get("recursive", True)); self.rules = settings.get("rules", [])
        self.conflict_entry.insert(0, settings.get("conflict_folder", "")); self.operation_mode.set(settings.get("operation_mode", "copy")); self.update_rules_tree()
    def update_ui_text(self):
        ld = self.lang_dict; self.parent.title(ld['window_title']); self.profile_frame.config(text=ld['profile_frame_title']); self.load_profile_btn.config(text=ld['load_profile_btn']); self.save_profile_btn.config(text=ld['save_profile_btn']); self.save_as_profile_btn.config(text=ld['save_as_profile_btn']); self.delete_profile_btn.config(text=ld['delete_profile_btn']); self.source_frame.config(text=ld['source_frame_title']); self.add_source_btn.config(text=ld['add_source_btn']); self.batch_add_source_btn.config(text=ld['batch_add_source_btn']); self.remove_source_btn.config(text=ld['remove_source_btn']); self.remove_all_sources_btn.config(text=ld['remove_all_sources_btn']); self.recursive_checkbtn.config(text=ld['recursive_checkbtn']); self.mode_frame.config(text=ld['operation_mode_label']); self.copy_radio.config(text=ld['copy_mode_radio']); self.move_radio.config(text=ld['move_mode_radio']); self.rules_frame.config(text=ld['rules_frame_title']); self.rules_tree.heading("enabled", text=ld['col_enabled']); self.rules_tree.heading("name", text=ld['col_name']); self.rules_tree.heading("keyword", text=ld['col_keyword']); self.rules_tree.heading("date_filter", text=ld['col_date_filter']); self.rules_tree.heading("destination", text=ld['col_destination']); self.add_rule_btn.config(text=ld['add_rule_btn']); self.edit_rule_btn.config(text=ld['edit_rule_btn']); self.copy_rule_btn.config(text=ld['copy_rule_btn']); self.delete_rule_btn.config(text=ld['delete_rule_btn']); self.conflict_frame.config(text=ld['conflict_frame_title']); self.browse_conflict_btn.config(text=ld['browse_btn']); self.start_button.config(text=ld['start_button']); self.log_frame.config(text=ld['log_frame_title']); self.lang_button.config(text=ld['lang_button']); self.update_rules_tree()
    def start_classification(self):
        sources, conflict_folder, active_rules, mode = list(self.source_listbox.get(0, tk.END)), self.conflict_entry.get(), [r for r in self.rules if r.get("enabled", True)], self.operation_mode.get()
        if not sources or not active_rules or not os.path.isdir(conflict_folder): messagebox.showerror(self.lang_dict['error_title'], self.lang_dict['config_validation_error']); return
        self.start_button.config(state="disabled"); self.log_text.delete(1.0, tk.END); start_time = datetime.now(); self.log(self.lang_dict['log_start_task'].format(start_time.strftime('%Y-%m-%d %H:%M:%S')))
        processed_count, conflicted_count = 0, 0
        for src_path in sources:
            self.log(self.lang_dict['log_scanning'].format(src_path))
            if self.recursive_var.get():
                for root, _, files in os.walk(src_path):
                    for filename in files: file_path = os.path.join(root, filename); p, f = self.process_file(file_path, filename, active_rules, conflict_folder, mode); processed_count += p; conflicted_count += f
            else:
                try:
                    for item in os.listdir(src_path):
                        file_path = os.path.join(src_path, item)
                        if os.path.isfile(file_path): p, f = self.process_file(file_path, item, active_rules, conflict_folder, mode); processed_count += p; conflicted_count += f
                except OSError as e: self.log(self.lang_dict['log_read_error'].format(src_path, e))
        end_time = datetime.now(); self.log(self.lang_dict['log_task_complete'].format(end_time.strftime('%Y-%m-%d %H:%M:%S'))); self.log(self.lang_dict['log_summary'].format(processed_count, conflicted_count)); self.log(self.lang_dict['log_duration'].format((end_time - start_time).total_seconds())); self.start_button.config(state="normal")
    def process_file(self, file_path, filename, active_rules, conflict_folder, mode):
        matching_rules = [];
        try: file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        except OSError: return 0, 0
        for rule in active_rules:
            keyword = rule.get("keyword", ""); name_match = keyword.lower() in filename.lower() if keyword else True
            date_filter = rule.get("date_filter", {}); date_mode = date_filter.get("mode", "none"); date_match = False
            if date_mode == "none": date_match = True
            else:
                try:
                    if date_mode == "after": d1 = datetime.strptime(date_filter["date1"], "%Y-%m-%d"); date_match = file_mod_time > d1
                    elif date_mode == "before": d1 = datetime.strptime(date_filter["date1"], "%Y-%m-%d"); date_match = file_mod_time < d1
                    elif date_mode == "between":
                        d1 = datetime.strptime(date_filter["date1"] + " 00:00:00", "%Y-%m-%d %H:%M:%S")
                        d2 = datetime.strptime(date_filter["date2"] + " 23:59:59", "%Y-%m-%d %H:%M:%S")
                        date_match = d1 <= file_mod_time <= d2
                except (ValueError, KeyError): date_match = False
            if name_match and date_match: matching_rules.append(rule)
        
        processed_count, conflicted_count = 0, 0
        action_func = shutil.move if mode == 'move' else shutil.copy2
        log_key_success = 'log_moved' if mode == 'move' else 'log_copied'
        log_key_fail = 'log_move_failed' if mode == 'move' else 'log_copy_failed'

        if len(matching_rules) == 1:
            dest_folder = matching_rules[0]["destination"]
            try:
                if not os.path.exists(dest_folder): os.makedirs(dest_folder)
                action_func(file_path, os.path.join(dest_folder, filename))
                self.log(self.lang_dict[log_key_success].format(filename, matching_rules[0]['name'])); processed_count = 1
            except Exception as e: self.log(self.lang_dict[log_key_fail].format(filename, e))
        elif len(matching_rules) > 1:
            try:
                action_func(file_path, os.path.join(conflict_folder, filename))
                rule_names = ", ".join([r['name'] for r in matching_rules]); self.log(self.lang_dict['log_conflict'].format(filename, rule_names)); conflicted_count = 1
            except Exception as e: self.log(self.lang_dict['log_conflict_failed'].format(filename, e))
        return processed_count, conflicted_count
    
    # (The rest of the functions are unchanged from V2.1.2)
    def on_closing(self): self.parent.destroy()
    def refresh_profile_list(self):
        if not os.path.exists(PROFILE_DIR): os.makedirs(PROFILE_DIR)
        profiles = sorted([f.replace('.json', '') for f in os.listdir(PROFILE_DIR) if f.endswith('.json')])
        self.profile_menu['values'] = profiles or [""]
        if profiles: self.profile_var.set(profiles[0]); self.load_profile()
        else: self.profile_var.set(""); self.clear_all_settings()
    def load_profile(self):
        profile_name = self.profile_var.get()
        if not profile_name: self.clear_all_settings(); return
        file_path = os.path.join(PROFILE_DIR, f"{profile_name}.json")
        try:
            with open(file_path, "r", encoding='utf-8') as f: self.load_settings_from_data(json.load(f)); self.log(self.lang_dict['profile_load_success'].format(profile_name))
        except Exception as e: messagebox.showerror(self.lang_dict['error_title'], self.lang_dict['config_load_error_msg'].format(e))
    def save_profile(self, profile_name=None):
        if not profile_name: profile_name = self.profile_var.get()
        if not profile_name: self.save_as_profile(); return
        file_path = os.path.join(PROFILE_DIR, f"{profile_name}.json")
        try:
            with open(file_path, "w", encoding='utf-8') as f: json.dump(self.get_current_settings_data(), f, indent=4); self.log(self.lang_dict['profile_save_success'].format(profile_name))
        except Exception as e: messagebox.showwarning(self.lang_dict['config_save_warning_title'], self.lang_dict['config_save_warning_msg'].format(e))
    def save_as_profile(self):
        profile_name = simpledialog.askstring(self.lang_dict['new_profile_prompt_title'], self.lang_dict['new_profile_prompt_msg'], parent=self)
        if profile_name: self.save_profile(profile_name); self.refresh_profile_list(); self.profile_var.set(profile_name)
    def delete_profile(self):
        profile_name = self.profile_var.get()
        if not profile_name: return
        if messagebox.askyesno(self.lang_dict['confirm_delete_title'], self.lang_dict['profile_delete_confirm'].format(profile_name)):
            file_path = os.path.join(PROFILE_DIR, f"{profile_name}.json")
            if os.path.exists(file_path): os.remove(file_path)
            self.refresh_profile_list()
    def clear_all_settings(self):
        self.source_listbox.delete(0, tk.END); self.rules = []; self.conflict_entry.delete(0, tk.END); self.update_rules_tree()
    def add_source(self):
        folder = filedialog.askdirectory()
        if folder and folder not in self.source_listbox.get(0, tk.END): self.source_listbox.insert(tk.END, folder)
    def batch_add_sources(self):
        dialog = BatchAddWindow(self, self.lang_dict); self.wait_window(dialog)
        if dialog.result is not None:
            paths = [path.strip() for path in dialog.result.split('\n') if path.strip()]
            current_sources = self.source_listbox.get(0, tk.END)
            for path in paths:
                if os.path.isdir(path) and path not in current_sources: self.source_listbox.insert(tk.END, path)
    def remove_source(self):
        selected = self.source_listbox.curselection()
        if selected:
            for i in sorted(selected, reverse=True): self.source_listbox.delete(i)
    def remove_all_sources(self): self.source_listbox.delete(0, tk.END)
    def browse_conflict(self):
        folder = filedialog.askdirectory()
        if folder: self.conflict_entry.delete(0, tk.END); self.conflict_entry.insert(0, folder)
    def toggle_language(self):
        self.current_lang = "en" if self.current_lang == "zh_tw" else "zh_tw"; self.lang_dict = LANGUAGES[self.current_lang]; self.update_ui_text()
    def log(self, message): self.log_text.insert(tk.END, f"{message}\n"); self.log_text.see(tk.END); self.parent.update_idletasks()
    def format_date_filter_for_display(self, date_filter):
        if not date_filter or date_filter.get("mode") == "none": return self.lang_dict['date_display_none']
        mode, d1, d2 = date_filter.get("mode"), date_filter.get("date1"), date_filter.get("date2")
        if mode == "after": return f"> {d1}"
        if mode == "before": return f"< {d1}"
        if mode == "between": return f"{d1} ~ {d2}"
        return self.lang_dict['date_display_none']
    def update_rules_tree(self):
        self.rules_tree.delete(*self.rules_tree.get_children())
        for i, rule in enumerate(self.rules):
            enabled_char = "✅" if rule.get("enabled", True) else "❎"
            date_display = self.format_date_filter_for_display(rule.get("date_filter"))
            values = (enabled_char, rule.get("name", ""), rule.get("keyword", ""), date_display, rule.get("destination", ""))
            self.rules_tree.insert("", "end", iid=i, values=values)
    def on_tree_click(self, event):
        region = self.rules_tree.identify_region(event.x, event.y)
        if region == "cell" and self.rules_tree.identify_column(event.x) == '#1':
            selected_item_id = self.rules_tree.identify_row(event.y)
            if selected_item_id:
                try:
                    rule_index = self.rules_tree.index(selected_item_id)
                    self.rules[rule_index]["enabled"] = not self.rules[rule_index].get("enabled", True)
                    self.update_rules_tree()
                except IndexError:
                    pass
    def add_rule(self): RuleEditorWindow(self, self.lang_dict, callback=lambda new_rule: (self.rules.append(new_rule), self.update_rules_tree()))
    def edit_rule(self):
        selected = self.rules_tree.focus()
        if not selected: messagebox.showinfo(self.lang_dict['info_title'], self.lang_dict['select_rule_to_edit_msg']); return
        rule_index = int(selected)
        def callback(updated_rule): self.rules[rule_index] = updated_rule; self.update_rules_tree()
        RuleEditorWindow(self, self.lang_dict, rule_data=self.rules[rule_index], callback=callback)
    def copy_rule(self):
        selected = self.rules_tree.focus()
        if not selected: messagebox.showinfo(self.lang_dict['info_title'], self.lang_dict['select_rule_to_copy_msg']); return
        rule_to_copy = json.loads(json.dumps(self.rules[int(selected)])); rule_to_copy["name"] += self.lang_dict['copied_suffix']; self.rules.append(rule_to_copy); self.update_rules_tree()
    def delete_rule(self):
        selected = self.rules_tree.focus()
        if not selected: messagebox.showinfo(self.lang_dict['info_title'], self.lang_dict['select_rule_to_delete_msg']); return
        if messagebox.askyesno(self.lang_dict['confirm_delete_title'], self.lang_dict['confirm_delete_msg']): del self.rules[int(selected)]; self.update_rules_tree()

if __name__ == "__main__":
    root = tk.Tk()
    try:
        style = ttk.Style(root)
        if "vista" in style.theme_names(): style.theme_use('vista')
        style.configure("Accent.TButton", foreground="white", background="dodgerblue")
    except tk.TclError: pass
    app = MainApplication(root)
    app.pack(side="top", fill="both", expand=True)
    root.mainloop()