# Task Manager GUI - Aplikasi manajemen tugas dengan antarmuka grafis (Tkinter)
# Fitur: CRUD tugas, prioritas, kategori, reminder, statistik, pencarian.

import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from pathlib import Path
from dataclasses import dataclass, asdict

import tkinter as tk
from tkinter import ttk, messagebox


TASKS_FILE = Path.home() / ".task_manager" / "tasks.json"
CATEGORIES = ["kerja", "pribadi", "belajar", "kesehatan", "horticulture", "other"]
PRIORITIES = {"high": "🔴 Tinggi", "medium": "🟡 Sedang", "low": "🟢 Rendah"}
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    id: str
    title: str
    priority: str = "medium"
    status: str = "pending"
    created_at: str = ""
    category: str = "general"
    tags: List[str] = None
    due_date: Optional[str] = None
    completed_at: Optional[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


def ensure_tasks_file():
    """Pastikan file tasks ada dan valid JSON"""
    if not TASKS_FILE.exists():
        TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
        TASKS_FILE.write_text("[]")


def load_tasks() -> List[Dict]:
    """Muat semua tugas dari file"""
    ensure_tasks_file()
    try:
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_tasks(tasks: List[Dict]):
    """Simpan tugas ke file"""
    ensure_tasks_file()
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2, default=str)


def generate_id() -> str:
    """Generate ID unik untuk tugas"""
    return datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse string tanggal ke datetime"""
    if not date_str:
        return None
    formats = ["%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def load_task_objects() -> List[Task]:
    """Muat tugas sebagai objek Task"""
    data = load_tasks()
    return [Task(**item) for item in data]


def save_task_objects(tasks: List[Task]):
    """Simpan objek Task ke file"""
    data = [asdict(t) for t in tasks]
    save_tasks(data)


class TaskManagerGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("📋 Task Manager")
        self.root.geometry("900x650")
        self.root.configure(bg="#f0f2f5")

        # Data
        self.tasks: List[Task] = []
        self.selected_task: Optional[Task] = None

        # Setup UI
        self.setup_styles()
        self.setup_header()
        self.setup_toolbar()
        self.setup_treeview()
        self.setup_detail_panel()
        self.setup_status_bar()

        # Load data
        self.refresh_tasks()

    def setup_styles(self):
        """Setup style untuk tkinter widgets"""
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Treeview',
                        background='white',
                        fg='black',
                        fieldbackground='white',
                        rowheight=28,
                        font=('Segoe UI', 10))
        style.map('Treeview', background=[('selected', '#4a90d9')])
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))

        style.configure('TButton', padding=6, relief='flat')
        style.configure('Header.TLabel', font=('Segoe UI', 18, 'bold'))
        style.configure('Status.TLabel', font=('Segoe UI', 9))

    def setup_header(self):
        """Setup header"""
        header = tk.Frame(self.root, bg="#1e3a8a", height=60)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(header, text="📋 Task Manager",
                 font=("Segoe UI", 20, "bold"),
                 bg="#1e3a8a", fg="white").pack(pady=15)

    def setup_toolbar(self):
        """Setup toolbar dengan tombol aksi"""
        toolbar = tk.Frame(self.root, bg="#f0f2f5", height=50)
        toolbar.pack(fill='x', padx=10, pady=5)

        btns = [
            ("➕ Tambah", self.add_task_window, "#28a745"),
            ("✏️ Edit", self.edit_task_window, "#007bff"),
            ("✅ Selesai", self.complete_task, "#17a2b8"),
            ("🗑️ Hapus", self.delete_task, "#dc3545"),
            ("📊 Statistik", self.show_stats, "#6f42c1"),
            ("⏰ Reminder", self.check_reminders, "#ffc107"),
            ("🔄 Refresh", self.refresh_tasks, "#6c757d"),
        ]

        for text, cmd, color in btns:
            btn = tk.Button(toolbar, text=text, command=cmd,
                            font=("Segoe UI", 10, "bold"),
                            bg=color, fg="white",
                            relief='flat', padx=12, pady=5)
            btn.pack(side='left', padx=4, pady=8)

    def setup_treeview(self):
        """Setup treeview untuk daftar tugas"""
        # Frame untuk treeview
        tree_frame = tk.Frame(self.root, bg="white")
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        # Search bar
        search_frame = tk.Frame(tree_frame, bg="white")
        search_frame.pack(fill='x', pady=(0, 5))

        tk.Label(search_frame, text="🔍 Cari:", bg="white",
                 font=("Segoe UI", 10)).pack(side='left', padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                font=("Segoe UI", 11), width=40)
        search_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))

        # Filter
        tk.Label(search_frame, text="Filter:", bg="white",
                 font=("Segoe UI", 10)).pack(side='left', padx=(5, 5))
        self.filter_var = tk.StringVar(value="all")
        filter_combo = ttk.Combobox(search_frame, textvariable=self.filter_var,
                                     values=["all", "pending", "completed"],
                                     state='readonly', width=10)
        filter_combo.pack(side='left', padx=(0, 10))
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_tasks())

        # Treeview
        columns = ("status", "priority", "title", "due_date", "category", "tags")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings',
                                  selectmode='browse')

        # Headings
        self.tree.heading("status", text="Status")
        self.tree.heading("priority", text="Prioritas")
        self.tree.heading("title", text="Judul")
        self.tree.heading("due_date", text="Due Date")
        self.tree.heading("category", text="Kategori")
        self.tree.heading("tags", text="Tags")

        # Column widths
        self.tree.column("status", width=60, anchor='center')
        self.tree.column("priority", width=80, anchor='center')
        self.tree.column("title", width=250, anchor='w')
        self.tree.column("due_date", width=120, anchor='center')
        self.tree.column("category", width=100, anchor='center')
        self.tree.column("tags", width=150, anchor='w')

        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        h_scroll = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=v_scroll.set, xscroll=h_scroll.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Bind events
        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)
        self.tree.bind("<Double-1>", self.on_double_click)

    def setup_detail_panel(self):
        """Setup panel detail tugas"""
        self.detail_frame = tk.LabelFrame(self.root, text="🔍 Detail Tugas",
                                          bg="white", font=("Segoe UI", 10, "bold"))
        self.detail_frame.pack(fill='x', padx=10, pady=(0, 10))

        self.detail_vars = {
            'title': tk.StringVar(value="Judul: -"),
            'priority': tk.StringVar(value="Prioritas: -"),
            'status': tk.StringVar(value="Status: -"),
            'category': tk.StringVar(value="Kategori: -"),
            'tags': tk.StringVar(value="Tags: -"),
            'due_date': tk.StringVar(value="Due: -"),
            'created_at': tk.StringVar(value="Dibuat: -")
        }

        for i, (key, var) in enumerate(self.detail_vars.items()):
            tk.Label(self.detail_frame, textvariable=var,
                     font=("Segoe UI", 10),
                     bg="white", anchor='w').grid(row=i // 4, column=i % 4,
                                                   sticky='w', padx=15, pady=3)

    def setup_status_bar(self):
        """Setup status bar"""
        self.status_var = tk.StringVar(value="Total tugas: 0")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                              bg="#e9ecef", font=("Segoe UI", 9),
                              anchor='w', padx=10)
        status_bar.pack(fill='x', side='bottom')

    def refresh_tasks(self, search_query: str = "", filter_status: str = "all"):
        """Refresh daftar tugas"""
        self.tasks = load_task_objects()

        # Filter by status
        if filter_status == "pending":
            self.tasks = [t for t in self.tasks if t.status != "completed"]
        elif filter_status == "completed":
            self.tasks = [t for t in self.tasks if t.status == "completed"]

        # Filter by search
        if search_query:
            query = search_query.lower()
            self.tasks = [t for t in self.tasks
                          if query in t.title.lower() or
                          any(query in tag.lower() for tag in (t.tags or []))]

        # Sort: pending first, then by priority and due date
        self.tasks.sort(key=lambda t: (
            0 if t.status == "pending" else 1,
            PRIORITY_ORDER.get(t.priority, 1),
            t.due_date or ""
        ))

        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert tasks
        for task in self.tasks:
            due_str = ""
            if task.due_date:
                due_dt = parse_date(task.due_date)
                due_str = due_dt.strftime("%Y-%m-%d %H:%M") if due_dt else ""

            tags_str = ", ".join(task.tags) if task.tags else ""

            values = (
                "✓" if task.status == "completed" else "○",
                PRIORITIES.get(task.priority, "🟡"),
                task.title,
                due_str,
                task.category.title(),
                tags_str
            )

            self.tree.insert("", "end", values=values)

        # Update status bar
        total = len(self.tasks)
        pending = len([t for t in self.tasks if t.status == "pending"])
        completed = total - pending
        self.status_var.set(f"Total: {total} | Pending: {pending} | Selesai: {completed}")

    def on_search(self, *args):
        """Handle search"""
        query = self.search_var.get()
        filter_status = self.filter_var.get()
        self.refresh_tasks(query, filter_status)

    def on_tree_select(self, event):
        """Handle tree selection"""
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            if 0 <= index < len(self.tasks):
                self.selected_task = self.tasks[index]
                self.show_task_detail()

    def on_double_click(self, event):
        """Handle double click to edit"""
        selected = self.tree.selection()
        if selected:
            index = self.tree.index(selected[0])
            if 0 <= index < len(self.tasks):
                self.selected_task = self.tasks[index]
                self.edit_task_window()

    def show_task_detail(self):
        """Show detail of selected task"""
        if not self.selected_task:
            return

        task = self.selected_task
        self.detail_vars['title'].set(f"Judul: {task.title}")
        self.detail_vars['priority'].set(f"Prioritas: {PRIORITIES.get(task.priority, '🟡')}")
        self.detail_vars['status'].set(f"Status: {'Selesai' if task.status == 'completed' else 'Pending'}")
        self.detail_vars['category'].set(f"Kategori: {task.category}")
        self.detail_vars['tags'].set(f"Tags: {', '.join(task.tags) if task.tags else 'Tidak ada'}")
        self.detail_vars['due_date'].set(f"Due: {task.due_date or 'Tidak ada'}")
        created = task.created_at[:19].replace('T', ' ') if task.created_at else "-"
        self.detail_vars['created_at'].set(f"Dibuat: {created}")

    def add_task_window(self):
        """Buka window tambah tugas"""
        self.selected_task = None

        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Tambah Tugas Baru")
        dialog.geometry("400x380")
        dialog.grab_set()

        # Form fields
        tk.Label(dialog, text="Judul Tugas *", font=("Segoe UI", 10, "bold")).pack(anchor='w', padx=20, pady=(15, 0))
        title_var = tk.StringVar()
        tk.Entry(dialog, textvariable=title_var, font=("Segoe UI", 11), width=40).pack(fill='x', padx=20, pady=5)

        tk.Label(dialog, text="Prioritas", font=("Segoe UI", 10, "bold")).pack(anchor='w', padx=20)
        priority_var = tk.StringVar(value='medium')
        ttk.Combobox(dialog, textvariable=priority_var, values=['high', 'medium', 'low'],
                     state='readonly').pack(fill='x', padx=20, pady=5)

        tk.Label(dialog, text="Kategori", font=("Segoe UI", 10, "bold")).pack(anchor='w', padx=20)
        category_var = tk.StringVar(value='general')
        ttk.Combobox(dialog, textvariable=category_var, values=CATEGORIES,
                     state='readonly').pack(fill='x', padx=20, pady=5)

        tk.Label(dialog, text="Due Date (YYYY-MM-DD HH:MM)", font=("Segoe UI", 10, "bold")).pack(anchor='w', padx=20)
        due_var = tk.StringVar()
        tk.Entry(dialog, textvariable=due_var, font=("Segoe UI", 11)).pack(fill='x', padx=20, pady=5)

        tk.Label(dialog, text="Tags (pisahkan koma)", font=("Segoe UI", 10, "bold")).pack(anchor='w', padx=20)
        tags_var = tk.StringVar()
        tk.Entry(dialog, textvariable=tags_var, font=("Segoe UI", 11)).pack(fill='x', padx=20, pady=5)

        # Buttons
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="Batal", command=dialog.destroy, width=10).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Simpan", command=lambda: save_new_task(dialog, title_var, priority_var, category_var, due_var, tags_var),
                 bg="#28a745", fg="white", width=10).pack(side='left', padx=5)

        # Focus title field
        title_var.trace_add('write', lambda *args: title_var.get() or None)
        dialog.after(100, lambda: title_var.set(title_var.get()))

        def save_new_task(dialog, title_var, priority_var, category_var, due_var, tags_var):
            title = title_var.get().strip()
            if not title:
                messagebox.showwarning("Peringatan", "Judul tugas tidak boleh kosong!", parent=dialog)
                return

            due_date_str = due_var.get().strip()
            due_date = None
            if due_date_str:
                due_date = parse_date(due_date_str)
                if not due_date:
                    messagebox.showwarning("Peringatan", "Format tanggal tidak valid!", parent=dialog)
                    return

            new_task = Task(
                id=generate_id(),
                title=title,
                priority=priority_var.get(),
                category=category_var.get(),
                due_date=due_date.isoformat() if due_date else None,
                tags=[t.strip() for t in tags_var.get().split(",") if t.strip()]
            )

            self.tasks.append(new_task)
            save_task_objects(self.tasks)
            self.refresh_tasks(self.search_var.get(), self.filter_var.get())
            dialog.destroy()
            messagebox.showinfo("Sukses", f"✅ Tugas '{title}' ditambahkan!", parent=self.root)

    def edit_task_window(self):
        """Buka window edit tugas"""
        if not self.selected_task:
            messagebox.showwarning("Peringatan", "Pilih tugas yang ingin diedit!", parent=self.root)
            return

        task = self.selected_task

        dialog = tk.Toplevel(self.root)
        dialog.title("✏️ Edit Tugas")
        dialog.geometry("400x380")
        dialog.grab_set()

        tk.Label(dialog, text="Judul Tugas *", font=("Segoe UI", 10, "bold")).pack(anchor='w', padx=20, pady=(15, 0))
        title_var = tk.StringVar(value=task.title)
        tk.Entry(dialog, textvariable=title_var, font=("Segoe UI", 11), width=40).pack(fill='x', padx=20, pady=5)

        tk.Label(dialog, text="Prioritas", font=("Segoe UI", 10, "bold")).pack(anchor='w', padx=20)
        priority_var = tk.StringVar(value=task.priority)
        ttk.Combobox(dialog, textvariable=priority_var, values=['high', 'medium', 'low'],
                     state='readonly').pack(fill='x', padx=20, pady=5)

        tk.Label(dialog, text="Kategori", font=("Segoe UI", 10, "bold")).pack(anchor='w', padx=20)
        category_var = tk.StringVar(value=task.category)
        ttk.Combobox(dialog, textvariable=category_var, values=CATEGORIES,
                     state='readonly').pack(fill='x', padx=20, pady=5)

        tk.Label(dialog, text="Due Date (YYYY-MM-DD HH:MM)", font=("Segoe UI", 10, "bold")).pack(anchor='w', padx=20)
        due_var = tk.StringVar(value=task.due_date[:19] if task.due_date else "")
        tk.Entry(dialog, textvariable=due_var, font=("Segoe UI", 11)).pack(fill='x', padx=20, pady=5)

        tk.Label(dialog, text="Tags (pisahkan koma)", font=("Segoe UI", 10, "bold")).pack(anchor='w', padx=20)
        tags_var = tk.StringVar(value=", ".join(task.tags))
        tk.Entry(dialog, textvariable=tags_var, font=("Segoe UI", 11)).pack(fill='x', padx=20, pady=5)

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="Batal", command=dialog.destroy, width=10).pack(side='left', padx=5)
        tk.Button(btn_frame, text="Simpan",
                 command=lambda: save_edit(dialog, title_var, priority_var, category_var, due_var, tags_var, task),
                 bg="#007bff", fg="white", width=10).pack(side='left', padx=5)

        def save_edit(dialog, title_var, priority_var, category_var, due_var, tags_var, task):
            due_date_str = due_var.get().strip()
            due_date = None
            if due_date_str:
                due_date = parse_date(due_date_str)
                if not due_date:
                    messagebox.showwarning("Peringatan", "Format tanggal tidak valid!", parent=dialog)
                    return

            task.title = title_var.get().strip()
            task.priority = priority_var.get()
            task.category = category_var.get()
            task.due_date = due_date.isoformat() if due_date else None
            task.tags = [t.strip() for t in tags_var.get().split(",") if t.strip()]

            save_task_objects(self.tasks)
            self.refresh_tasks(self.search_var.get(), self.filter_var.get())
            dialog.destroy()
            messagebox.showinfo("Sukses", f"✅ Tugas '{task.title}' telah diedit!", parent=self.root)

    def complete_task(self):
        """Tandai tugas selesai"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih tugas yang ingin ditandai selesai!", parent=self.root)
            return

        index = self.tree.index(selected[0])
        if 0 <= index < len(self.tasks):
            task = self.tasks[index]
            if task.status == "completed":
                messagebox.showinfo("Info", "Tugas sudah selesai!", parent=self.root)
                return

            if messagebox.askyesno("Konfirmasi", f"Tandai '{task.title}' sebagai selesai?", parent=self.root):
                task.status = "completed"
                task.completed_at = datetime.now().isoformat()
                save_task_objects(self.tasks)
                self.refresh_tasks(self.search_var.get(), self.filter_var.get())
                messagebox.showinfo("Sukses", f"✅ Tugas '{task.title}' selesai!", parent=self.root)

    def delete_task(self):
        """Hapus tugas"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Peringatan", "Pilih tugas yang ingin dihapus!", parent=self.root)
            return

        index = self.tree.index(selected[0])
        if 0 <= index < len(self.tasks):
            task = self.tasks[index]
            if messagebox.askyesno("Konfirmasi", f"Yakin hapus tugas '{task.title}'?", parent=self.root):
                self.tasks.remove(task)
                save_task_objects(self.tasks)
                self.refresh_tasks(self.search_var.get(), self.filter_var.get())
                messagebox.showinfo("Sukses", f"🗑️ Tugas '{task.title}' dihapus!", parent=self.root)

    def show_stats(self):
        """Tampilkan statistik tugas"""
        if not self.tasks:
            messagebox.showinfo("Statistik", "Tidak ada tugas yang terdaftar!", parent=self.root)
            return

        total = len(self.tasks)
        completed = len([t for t in self.tasks if t.status == "completed"])
        pending = total - completed

        by_priority = {}
        by_category = {}

        for task in self.tasks:
            by_priority[task.priority] = by_priority.get(task.priority, 0) + 1
            by_category[task.category] = by_category.get(task.category, 0) + 1

        stats_text = f"""📊 STATISTIK TUGAS

Total Tugas: {total}
✅ Selesai: {completed} ({completed*100//total if total else 0}%)
⏳ Pending: {pending}

By Prioritas:
  🔴 Tinggi: {by_priority.get('high', 0)}
  🟡 Sedang: {by_priority.get('medium', 0)}
  🟢 Rendah: {by_priority.get('low', 0)}

By Kategori:
"""
        for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
            stats_text += f"  • {cat.title()}: {count}\n"

        messagebox.showinfo("Statistik Tugas", stats_text, parent=self.root)

    def check_reminders(self):
        """Cek reminder tugas"""
        now = datetime.now()
        reminders = []

        for task in self.tasks:
            if task.status == "completed":
                continue

            if task.due_date:
                due = parse_date(task.due_date)
                if due:
                    time_diff = due - now

                    if now > due:
                        reminders.append(("🚨 OVERDUE", task))
                    elif time_diff <= timedelta(hours=24):
                        reminders.append(("⏰ Mendekati", task))

        if not reminders:
            messagebox.showinfo("Reminder", "✅ Tidak ada tugas yang perlu diingatkan!", parent=self.root)
            return

        reminder_text = "⏰ REMINDER TUGAS\n\n"
        for r_type, task in reminders:
            due_str = ""
            if task.due_date:
                due_dt = parse_date(task.due_date)
                due_str = f" (due: {due_dt.strftime('%Y-%m-%d %H:%M')})" if due_dt else ""
            reminder_text += f"{r_type}: {task.title}{due_str}\n"

        messagebox.showwarning("Reminder Tugas", reminder_text, parent=self.root)


def main():
    root = tk.Tk()
    app = TaskManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()