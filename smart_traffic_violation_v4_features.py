import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date
from collections import Counter
import csv

DB = "traffic_violation.db"

FINE_RULES = {
    "Over-speeding": 1000,
    "No helmet": 500,
    "Signal violation": 1000,
    "Wrong parking": 500,
    "No seat belt": 500,
}

# A vehicle is considered a repeat offender when it has 2 or more recorded violations.
REPEAT_OFFENDER_THRESHOLD = 2

PRIORITY = {
    "Over-speeding": "High",
    "No helmet": "Medium",
    "Signal violation": "High",
    "Wrong parking": "Low",
    "No seat belt": "Medium",
}

class TrafficApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Parking Violation – Traffic Violation & Fine Management")
        self.root.geometry("1250x760")
        self.root.minsize(1050, 680)
        self.root.configure(bg="#f5f7fb")

        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except:
            pass
        self.setup_styles()
        self.db = sqlite3.connect(DB)
        self.db.row_factory = sqlite3.Row
        self.create_tables()
        self.build_ui()
        self.refresh_dashboard()

        

    def setup_styles(self):
        self.style.configure("TFrame", background="#f5f7fb")
        self.style.configure("Card.TFrame", background="#ffffff")
        self.style.configure("TLabel", background="#f5f7fb", foreground="#334155", font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", background="#ffffff", foreground="#0f172a", font=("Segoe UI", 22, "bold"))
        self.style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", foreground="#334155", rowheight=34, font=("Segoe UI", 9))
        self.style.configure("Treeview.Heading", background="#eef2f7", foreground="#334155", font=("Segoe UI", 9, "bold"), padding=8)
        self.style.map("Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", "#0f172a")])
        self.style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=(15, 9))
        self.style.configure("TButton", font=("Segoe UI", 9), padding=(12, 8))
        self.style.configure("TEntry", padding=8)
        self.style.configure("TCombobox", padding=7)

    def build_ui(self):
        # Modern application shell: dark sidebar + clean workspace.
        self.root.configure(bg="#f5f7fb")

        sidebar = tk.Frame(self.root, bg="#0f172a", width=235)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand = tk.Frame(sidebar, bg="#0f172a", height=105)
        brand.pack(fill="x")
        tk.Label(brand, text="◈", bg="#0f172a", fg="#38bdf8", font=("Segoe UI", 27, "bold")).pack(anchor="w", padx=22, pady=(18,0))
        tk.Label(brand, text="SMART TRAFFIC", bg="#0f172a", fg="white", font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=23)
        tk.Label(brand, text="Violation & Fine Control", bg="#0f172a", fg="#94a3b8", font=("Segoe UI", 8)).pack(anchor="w", padx=23, pady=(0,10))

        tk.Label(sidebar, text="MAIN MENU", bg="#0f172a", fg="#64748b", font=("Segoe UI",8,"bold")).pack(anchor="w", padx=23, pady=(12,8))
        self.nav_buttons = {}
        items = [
            ("Dashboard", "⌂", self.show_dashboard),
            ("Vehicles", "▣", self.show_vehicles),
            ("Violations", "⚠", self.show_violations),
            ("Fines & Payments", "₹", self.show_fines),
            ("Analytics", "◫", self.show_analysis),
            ("Reports", "▤", self.show_reports),
        ]
        for name, icon, cmd in items:
            b = tk.Button(sidebar, text=f"  {icon}   {name}", command=cmd, anchor="w",
                          bg="#0f172a", fg="#cbd5e1", activebackground="#1e293b", activeforeground="white",
                          bd=0, relief="flat", font=("Segoe UI", 10, "bold"), padx=18, pady=10, cursor="hand2")
            b.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[name] = b

        tk.Frame(sidebar, bg="#1e293b", height=1).pack(fill="x", padx=18, pady=18)
        tk.Label(sidebar, text="TRAFFIC ADMIN", bg="#0f172a", fg="#64748b", font=("Segoe UI",8,"bold")).pack(anchor="w", padx=23)
        tk.Label(sidebar, text="●  System Online", bg="#0f172a", fg="#4ade80", font=("Segoe UI",9,"bold")).pack(anchor="w", padx=23, pady=7)
        tk.Label(sidebar, text="SQLite database enabled", bg="#0f172a", fg="#64748b", font=("Segoe UI",8)).pack(anchor="w", padx=23)

        workspace = tk.Frame(self.root, bg="#f5f7fb")
        workspace.pack(side="left", fill="both", expand=True)

        topbar = tk.Frame(workspace, bg="white", height=72, highlightbackground="#e2e8f0", highlightthickness=1)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)
        left = tk.Frame(topbar, bg="white")
        left.pack(side="left", fill="y", padx=24)
        tk.Label(left, text="Traffic Violation Management", bg="white", fg="#0f172a", font=("Segoe UI", 15, "bold")).pack(anchor="w", pady=(15,0))
        tk.Label(left, text="Centralized command center for vehicles, violations and fines", bg="white", fg="#94a3b8", font=("Segoe UI", 8)).pack(anchor="w")
        tk.Label(topbar, text=datetime.now().strftime("%d %b %Y"), bg="white", fg="#64748b", font=("Segoe UI",9,"bold")).pack(side="right", padx=24)

        self.content = tk.Frame(workspace, bg="#f5f7fb")
        self.content.pack(fill="both", expand=True, padx=26, pady=22)

        self.status = tk.Label(workspace, text="Ready • System online", anchor="w", bg="#e2e8f0", fg="#475569", font=("Segoe UI",8), padx=15)
        self.status.pack(fill="x", side="bottom", ipady=5)

    def create_tables(self):
        c = self.db.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS vehicles(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registration TEXT UNIQUE NOT NULL,
            owner TEXT NOT NULL,
            vehicle_type TEXT NOT NULL,
            contact TEXT,
            license TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS violations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            violation_id TEXT UNIQUE NOT NULL,
            registration TEXT NOT NULL,
            violation_type TEXT NOT NULL,
            vdate TEXT NOT NULL,
            location TEXT,
            fine REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending',
            priority TEXT NOT NULL
        )""")
        self.db.commit()

    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#17202a", height=82)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="🚦  SMART TRAFFIC", bg="#17202a", fg="white",
                 font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=25, pady=(13,0))
        tk.Label(header, text="Violation & Fine Management System",
                 bg="#17202a", fg="#b0bec5", font=("Segoe UI", 9)).pack(anchor="w", padx=27)

        # Navigation
        nav = tk.Frame(self.root, bg="#263238", height=52)
        nav.pack(fill="x")
        nav.pack_propagate(False)
        self.nav_buttons = {}
        items = [
            ("Dashboard", self.show_dashboard),
            ("Vehicles", self.show_vehicles),
            ("Violations", self.show_violations),
            ("Fines", self.show_fines),
            ("Analysis", self.show_analysis),
            ("Reports", self.show_reports),
        ]
        for name, cmd in items:
            b = tk.Button(nav, text=name, command=cmd, bg="#263238", fg="white",
                          activebackground="#37474f", activeforeground="white",
                          bd=0, relief="flat", font=("Segoe UI", 10, "bold"),
                          padx=18, cursor="hand2")
            b.pack(side="left", fill="y")
            self.nav_buttons[name] = b

        self.content = tk.Frame(self.root, bg="#f5f7fb")
        self.content.pack(fill="both", expand=True, padx=22, pady=18)

        self.status = tk.Label(self.root, text="Ready", anchor="w",
                               bg="#eceff1", fg="#546e7a", font=("Segoe UI", 9), padx=12)
        self.status.pack(fill="x", side="bottom", ipady=5)

    def clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    def set_active(self, name):
        for n, b in self.nav_buttons.items():
            b.configure(bg="#455a64" if n == name else "#263238")

    def heading(self, title, subtitle=""):
        f = tk.Frame(self.content, bg="#f5f7fb")
        f.pack(fill="x", pady=(0,16))
        tk.Label(f, text=title, bg="#f5f7fb", fg="#0f172a",
                 font=("Segoe UI", 23, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(f, text=subtitle, bg="#f5f7fb", fg="#64748b",
                     font=("Segoe UI", 10)).pack(anchor="w", pady=(4,0))

    def card(self, parent, title, value, accent="#1976d2"):
        c = tk.Frame(parent, bg="white", highlightbackground="#e0e0e0",
                     highlightthickness=1)
        c.pack(side="left", fill="both", expand=True, padx=6)
        tk.Frame(c, bg=accent, height=5).pack(fill="x")
        tk.Label(c, text=title.upper(), bg="white", fg="#64748b",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(14,2))
        tk.Label(c, text=str(value), bg="white", fg="#0f172a",
                 font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=16, pady=(0,15))
        return c

    def refresh_dashboard(self):
        self.show_dashboard()

    def show_dashboard(self):
        self.clear(); self.set_active("Dashboard")
        self.heading("Dashboard", "Real-time overview of traffic violations and fine collection")

        cur = self.db.cursor()
        vehicles = cur.execute("SELECT COUNT(*) FROM vehicles").fetchone()[0]
        violations = cur.execute("SELECT COUNT(*) FROM violations").fetchone()[0]
        pending = cur.execute("SELECT COALESCE(SUM(fine),0) FROM violations WHERE status='Pending'").fetchone()[0]
        paid = cur.execute("SELECT COALESCE(SUM(fine),0) FROM violations WHERE status='Paid'").fetchone()[0]

        row = tk.Frame(self.content, bg="#f5f7fb")
        row.pack(fill="x", pady=(0,18))
        self.card(row, "Registered Vehicles", vehicles, "#1976d2")
        self.card(row, "Total Violations", violations, "#8e44ad")
        self.card(row, "Pending Fines", f"₹{pending:,.0f}", "#e67e22")
        self.card(row, "Collected Fines", f"₹{paid:,.0f}", "#27ae60")

        lower = tk.Frame(self.content, bg="#f5f7fb")
        lower.pack(fill="both", expand=True)

        left = tk.Frame(lower, bg="white", highlightbackground="#e0e0e0", highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0,8))
        tk.Label(left, text="Recent Violations", bg="white", fg="#0f172a",
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=12)
        cols = ("ID","Vehicle","Type","Date","Fine","Status")
        tree = ttk.Treeview(left, columns=cols, show="headings", height=9)
        widths = [90,110,160,100,90,90]
        for col,w in zip(cols,widths):
            tree.heading(col,text=col); tree.column(col,width=w,anchor="center")
        tree.pack(fill="both", expand=True, padx=12, pady=(0,12))
        for r in cur.execute("SELECT violation_id,registration,violation_type,vdate,fine,status FROM violations ORDER BY id DESC LIMIT 9"):
            tree.insert("", "end", values=(r["violation_id"],r["registration"],r["violation_type"],
                                           r["vdate"],f"₹{r['fine']:,.0f}",r["status"]))

        right = tk.Frame(lower, bg="white", highlightbackground="#e0e0e0", highlightthickness=1)
        right.pack(side="left", fill="both", expand=True, padx=(8,0))
        tk.Label(right, text="System Alerts", bg="white", fg="#0f172a",
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=16, pady=12)
        repeated = cur.execute("""SELECT registration, COUNT(*) AS cnt
                                  FROM violations
                                  GROUP BY registration
                                  HAVING COUNT(*) >= ?
                                  ORDER BY cnt DESC""",
                               (REPEAT_OFFENDER_THRESHOLD,)).fetchall()
        tk.Label(right, text=f"Repeat Offender Alerts  •  {len(repeated)} vehicle(s)",
                 bg="white", fg="#0f172a", font=("Segoe UI",11,"bold"),
                 anchor="w").pack(fill="x", padx=16, pady=(0,8))

        if repeated:
            for r in repeated[:6]:
                tk.Label(right, text=f"⚠  {r['registration']}   •   {r['cnt']} violations",
                         bg="#fff7ed", fg="#c2410c", font=("Segoe UI",10,"bold"),
                         anchor="w", padx=12, pady=9).pack(fill="x", padx=12, pady=4)
        else:
            tk.Label(right, text="✓  No repeat offenders detected.",
                     bg="#ecfdf5", fg="#15803d", font=("Segoe UI",10,"bold"),
                     anchor="w", padx=12, pady=10).pack(fill="x", padx=12, pady=4)

        if pending > 0:
            tk.Label(right, text=f"●  ₹{pending:,.0f} in unpaid fines",
                     bg="#fef2f2", fg="#dc2626", font=("Segoe UI",10,"bold"),
                     anchor="w", padx=12, pady=10).pack(fill="x", padx=12, pady=4)

    def show_vehicles(self):
        self.clear(); self.set_active("Vehicles")
        self.heading("Vehicle Management",
                     "Register, search, filter by vehicle type and sort by violation count")

        # ── Action toolbar ──────────────────────────────────────────────
        action = tk.Frame(self.content, bg="#f5f7fb")
        action.pack(fill="x", pady=(0,8))

        ttk.Button(action, text="+ Add Vehicle",
                   command=self.vehicle_form).pack(side="left")
        ttk.Button(action, text="Edit Selected",
                   command=self.edit_vehicle).pack(side="left", padx=8)
        ttk.Button(action, text="Delete Selected",
                   command=self.delete_vehicle).pack(side="left")
        ttk.Button(action, text="Refresh",
                   command=self.load_vehicles).pack(side="left", padx=8)

        # ── Search / filter / sorting toolbar ──────────────────────────
        filters = tk.Frame(self.content, bg="white",
                           highlightbackground="#dbe3ec",
                           highlightthickness=1)
        filters.pack(fill="x", pady=(0,10), ipady=8)

        tk.Label(filters, text="Search",
                 bg="white", fg="#475569",
                 font=("Segoe UI",9,"bold")).pack(side="left", padx=(14,5))

        self.vehicle_search = tk.StringVar()
        search_entry = ttk.Entry(filters, textvariable=self.vehicle_search,
                                 width=27)
        search_entry.pack(side="left", padx=(0,6))
        search_entry.bind("<Return>", lambda event: self.load_vehicles())

        ttk.Button(filters, text="Search",
                   command=self.load_vehicles).pack(side="left")
        ttk.Button(filters, text="Clear",
                   command=self.clear_vehicle_filters).pack(side="left", padx=6)

        tk.Label(filters, text="Vehicle Type",
                 bg="white", fg="#475569",
                 font=("Segoe UI",9,"bold")).pack(side="left", padx=(18,5))

        self.vehicle_type_filter = tk.StringVar(value="All Types")
        type_box = ttk.Combobox(
            filters,
            textvariable=self.vehicle_type_filter,
            values=["All Types","Car","Bike","Auto","Bus","Truck","Van","Other"],
            state="readonly",
            width=15
        )
        type_box.pack(side="left")
        type_box.bind("<<ComboboxSelected>>",
                      lambda event: self.load_vehicles())

        tk.Label(filters, text="Sort",
                 bg="white", fg="#475569",
                 font=("Segoe UI",9,"bold")).pack(side="left", padx=(18,5))

        self.vehicle_sort = tk.StringVar(value="Newest First")
        sort_box = ttk.Combobox(
            filters,
            textvariable=self.vehicle_sort,
            values=[
                "Newest First",
                "Oldest First",
                "Violations: High to Low",
                "Violations: Low to High",
                "Registration A-Z",
                "Owner A-Z"
            ],
            state="readonly",
            width=23
        )
        sort_box.pack(side="left")
        sort_box.bind("<<ComboboxSelected>>",
                      lambda event: self.load_vehicles())

        # Result counter
        self.vehicle_result_label = tk.Label(
            filters, text="",
            bg="white", fg="#64748b",
            font=("Segoe UI",9)
        )
        self.vehicle_result_label.pack(side="right", padx=14)

        # ── Vehicle table ───────────────────────────────────────────────
        frame = tk.Frame(self.content, bg="white",
                         highlightbackground="#dbe3ec",
                         highlightthickness=1)
        frame.pack(fill="both", expand=True)

        cols = ("ID","Registration","Owner","Vehicle Type",
                "Contact","License","Violations")

        self.vtree = ttk.Treeview(frame, columns=cols, show="headings")

        for col, width in zip(
            cols, [55,150,200,125,135,140,100]
        ):
            self.vtree.heading(col, text=col)
            self.vtree.column(col, width=width, anchor="center")

        # Visual emphasis for vehicles with 2+ violations.
        self.vtree.tag_configure("repeat", background="#fff7ed")
        self.vtree.tag_configure("normal", background="white")

        self.vtree.pack(fill="both", expand=True, padx=10, pady=10)

        # Double-click opens vehicle editor.
        self.vtree.bind("<Double-1>", lambda event: self.edit_vehicle())

        search_entry.focus_set()
        self.load_vehicles()

    def clear_vehicle_filters(self):
        self.vehicle_search.set("")
        self.vehicle_type_filter.set("All Types")
        self.vehicle_sort.set("Newest First")
        self.load_vehicles()

    def load_vehicles(self):
        if not hasattr(self, "vtree"):
            return

        # Clear existing rows.
        for item in self.vtree.get_children():
            self.vtree.delete(item)

        search = self.vehicle_search.get().strip()
        vehicle_type = self.vehicle_type_filter.get()

        # Build the query safely with parameters.
        conditions = []
        params = []

        if search:
            like = f"%{search}%"
            conditions.append(
                "(v.registration LIKE ? COLLATE NOCASE "
                "OR v.owner LIKE ? COLLATE NOCASE "
                "OR v.contact LIKE ? "
                "OR v.license LIKE ? COLLATE NOCASE)"
            )
            params.extend([like, like, like, like])

        if vehicle_type and vehicle_type != "All Types":
            conditions.append("v.vehicle_type = ?")
            params.append(vehicle_type)

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        # Sorting is selected from a fixed whitelist; no user input is
        # inserted into SQL.
        sort_map = {
            "Newest First": "v.id DESC",
            "Oldest First": "v.id ASC",
            "Violations: High to Low": "cnt DESC, v.id DESC",
            "Violations: Low to High": "cnt ASC, v.id DESC",
            "Registration A-Z": "v.registration COLLATE NOCASE ASC",
            "Owner A-Z": "v.owner COLLATE NOCASE ASC"
        }
        order_by = sort_map.get(
            self.vehicle_sort.get(), "v.id DESC"
        )

        query = f"""
            SELECT v.*,
                   COUNT(x.id) AS cnt
            FROM vehicles v
            LEFT JOIN violations x
                   ON v.registration = x.registration
            {where}
            GROUP BY v.id
            ORDER BY {order_by}
        """

        rows = self.db.execute(query, params).fetchall()

        for r in rows:
            tag = "repeat" if r["cnt"] >= REPEAT_OFFENDER_THRESHOLD else "normal"
            self.vtree.insert(
                "", "end",
                values=(
                    r["id"],
                    r["registration"],
                    r["owner"],
                    r["vehicle_type"],
                    r["contact"],
                    r["license"],
                    r["cnt"]
                ),
                tags=(tag,)
            )

        if hasattr(self, "vehicle_result_label"):
            self.vehicle_result_label.config(
                text=f"{len(rows)} vehicle(s) displayed"
            )

        if hasattr(self, "status"):
            if search or (vehicle_type and vehicle_type != "All Types"):
                self.status.config(
                    text=f"Vehicle search/filter applied • {len(rows)} result(s)"
                )
            else:
                self.status.config(
                    text=f"Showing all vehicles • {len(rows)} vehicle(s)"
                )

    def vehicle_form(self, row=None):
        win=tk.Toplevel(self.root); win.title("Vehicle Details"); win.geometry("460x450")
        win.transient(self.root); win.grab_set(); win.configure(bg="#f5f7fb")
        tk.Label(win,text="Vehicle Details",bg="#f5f7fb",fg="#0f172a",
                 font=("Segoe UI",18,"bold")).pack(pady=18)
        fields=[("Registration Number","registration"),("Owner Name","owner"),
                ("Contact Number","contact"),("License Number","license")]
        vars={}
        for label,key in fields:
            tk.Label(win,text=label,bg="#f5f7fb",anchor="w").pack(fill="x",padx=35)
            v=tk.StringVar(value="" if not row else row[key]); vars[key]=v
            ttk.Entry(win,textvariable=v).pack(fill="x",padx=35,pady=(2,10))
        tk.Label(win,text="Vehicle Type",bg="#f5f7fb",anchor="w").pack(fill="x",padx=35)
        typ=tk.StringVar(value="" if not row else row["vehicle_type"])
        ttk.Combobox(win,textvariable=typ,values=["Car","Bike","Auto","Bus","Truck","Van","Other"],
                     state="readonly").pack(fill="x",padx=35,pady=(2,15))
        def save():
            reg=vars["registration"].get().strip().upper()
            owner=vars["owner"].get().strip()
            if not reg or not owner or not typ.get():
                messagebox.showwarning("Missing Data","Registration, owner and vehicle type are required.",parent=win); return
            try:
                if row:
                    self.db.execute("""UPDATE vehicles SET registration=?,owner=?,vehicle_type=?,contact=?,license=?
                                       WHERE id=?""",(reg,owner,typ.get(),vars["contact"].get(),vars["license"].get(),row["id"]))
                else:
                    self.db.execute("""INSERT INTO vehicles(registration,owner,vehicle_type,contact,license)
                                       VALUES(?,?,?,?,?)""",(reg,owner,typ.get(),vars["contact"].get(),vars["license"].get()))
                self.db.commit(); win.destroy(); self.load_vehicles()
                self.status.config(text="Vehicle saved successfully.")
            except sqlite3.IntegrityError:
                messagebox.showerror("Duplicate","That registration number already exists.",parent=win)
        ttk.Button(win,text="Save Vehicle",command=save).pack(pady=5)

    def selected_vehicle(self):
        sel=self.vtree.selection()
        if not sel: return None
        vals=self.vtree.item(sel[0],"values")
        return self.db.execute("SELECT * FROM vehicles WHERE id=?",(vals[0],)).fetchone()

    def edit_vehicle(self):
        r=self.selected_vehicle()
        if r: self.vehicle_form(r)
        else: messagebox.showinfo("Select Vehicle","Please select a vehicle first.")

    def delete_vehicle(self):
        r=self.selected_vehicle()
        if not r: messagebox.showinfo("Select Vehicle","Please select a vehicle first."); return
        if messagebox.askyesno("Confirm Delete",f"Delete vehicle {r['registration']}?"):
            self.db.execute("DELETE FROM vehicles WHERE id=?",(r["id"],)); self.db.commit()
            self.load_vehicles()

    def show_violations(self):
        self.clear(); self.set_active("Violations")
        self.heading("Violation Management","Record violations and automatically calculate penalties")
        bar=tk.Frame(self.content,bg="#f5f7fb"); bar.pack(fill="x",pady=(0,10))
        ttk.Button(bar,text="+ Record Violation",command=self.violation_form).pack(side="left")
        ttk.Button(bar,text="View Vehicle History",command=self.vehicle_history).pack(side="left",padx=8)
        self.vi_search=tk.StringVar()
        ttk.Entry(bar,textvariable=self.vi_search,width=28).pack(side="right")
        tk.Label(bar,text="Search:",bg="#f5f7fb").pack(side="right",padx=5)
        self.vi_search.trace_add("write",lambda *_:self.load_violations())
        frame=tk.Frame(self.content,bg="white",highlightbackground="#e0e0e0",highlightthickness=1); frame.pack(fill="both",expand=True)
        cols=("Violation ID","Vehicle","Type","Date","Location","Fine","Priority","Status")
        self.vtree=ttk.Treeview(frame,columns=cols,show="headings")
        for c,w in zip(cols,[105,105,155,100,170,90,85,90]):
            self.vtree.heading(c,text=c);self.vtree.column(c,width=w,anchor="center")
        self.vtree.pack(fill="both",expand=True,padx=10,pady=10)
        self.load_violations()

    def load_violations(self):
        if not hasattr(self,"vtree"): return
        for i in self.vtree.get_children(): self.vtree.delete(i)
        q=f"%{self.vi_search.get().strip()}%"
        rows=self.db.execute("""SELECT * FROM violations WHERE violation_id LIKE ?
                                OR registration LIKE ? OR violation_type LIKE ?
                                ORDER BY id DESC""",(q,q,q)).fetchall()
        for r in rows:
            self.vtree.insert("", "end", values=(r["violation_id"],r["registration"],r["violation_type"],
                           r["vdate"],r["location"],f"₹{r['fine']:,.0f}",r["priority"],r["status"]))

    def violation_form(self):
        win=tk.Toplevel(self.root);win.title("Record Violation");win.geometry("500x540")
        win.transient(self.root);win.grab_set();win.configure(bg="#f5f7fb")
        tk.Label(win,text="Record New Violation",bg="#f5f7fb",fg="#0f172a",
                 font=("Segoe UI",18,"bold")).pack(pady=15)
        def field(label):
            tk.Label(win,text=label,bg="#f5f7fb",anchor="w").pack(fill="x",padx=35)
        field("Vehicle Registration")
        reg=tk.StringVar(); ttk.Entry(win,textvariable=reg).pack(fill="x",padx=35,pady=(2,10))
        field("Violation Type")
        typ=tk.StringVar(); combo=ttk.Combobox(win,textvariable=typ,values=list(FINE_RULES),state="readonly")
        combo.pack(fill="x",padx=35,pady=(2,10))
        fine=tk.StringVar(value="₹0"); priority=tk.StringVar(value="Priority: —")
        def update_rule(*_):
            t=typ.get(); fine.set(f"₹{FINE_RULES.get(t,0):,.0f}"); priority.set(f"Priority: {PRIORITY.get(t,'—')}")
        combo.bind("<<ComboboxSelected>>",update_rule)
        field("Date (YYYY-MM-DD)")
        dt=tk.StringVar(value=date.today().isoformat());ttk.Entry(win,textvariable=dt).pack(fill="x",padx=35,pady=(2,10))
        field("Location")
        loc=tk.StringVar();ttk.Entry(win,textvariable=loc).pack(fill="x",padx=35,pady=(2,10))
        tk.Label(win,textvariable=fine,bg="#f5f7fb",fg="#1976d2",font=("Segoe UI",16,"bold")).pack(pady=5)
        tk.Label(win,textvariable=priority,bg="#f5f7fb",fg="#e67e22",font=("Segoe UI",10,"bold")).pack()
        def save():
            r=reg.get().strip().upper(); t=typ.get().strip()
            if not self.db.execute("SELECT id FROM vehicles WHERE registration=?",(r,)).fetchone():
                messagebox.showerror("Vehicle Not Found","Register the vehicle before recording a violation.",parent=win);return
            if not t or not loc.get().strip(): messagebox.showwarning("Missing Data","Select violation type and enter location.",parent=win);return
            try: datetime.strptime(dt.get().strip(),"%Y-%m-%d")
            except: messagebox.showerror("Invalid Date","Use YYYY-MM-DD format.",parent=win);return
            vid=f"V{datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]}"
            self.db.execute("""INSERT INTO violations(violation_id,registration,violation_type,vdate,location,fine,status,priority)
                               VALUES(?,?,?,?,?,?,?,?)""",(vid,r,t,dt.get().strip(),loc.get().strip(),FINE_RULES[t],"Pending",PRIORITY[t]))
            self.db.commit();win.destroy();self.load_violations();self.status.config(text=f"Violation {vid} recorded.")
        ttk.Button(win,text="Save Violation",command=save).pack(pady=18)

    def vehicle_history(self):
        if not hasattr(self,"vtree"): return
        sel=self.vtree.selection()
        if not sel: messagebox.showinfo("Select Violation","Select a violation to identify its vehicle."); return
        reg=self.vtree.item(sel[0],"values")[1]
        rows=self.db.execute("SELECT * FROM violations WHERE registration=? ORDER BY vdate DESC",(reg,)).fetchall()
        win=tk.Toplevel(self.root);win.title(f"History – {reg}");win.geometry("900x430")
        tk.Label(win,text=f"Violation History: {reg}",font=("Segoe UI",16,"bold")).pack(pady=12)
        tr=ttk.Treeview(win,columns=("ID","Type","Date","Location","Fine","Status"),show="headings")
        for c,w in zip(("ID","Type","Date","Location","Fine","Status"),(130,150,100,180,100,100)):
            tr.heading(c,text=c);tr.column(c,width=w,anchor="center")
        tr.pack(fill="both",expand=True,padx=15,pady=10)
        for r in rows:tr.insert("", "end",values=(r["violation_id"],r["violation_type"],r["vdate"],r["location"],f"₹{r['fine']:,.0f}",r["status"]))

    def show_fines(self):
        self.clear();self.set_active("Fines")
        self.heading("Fine Management","Track pending payments, paid fines and total collection")
        cur=self.db.cursor()
        pending=cur.execute("SELECT COALESCE(SUM(fine),0) FROM violations WHERE status='Pending'").fetchone()[0]
        paid=cur.execute("SELECT COALESCE(SUM(fine),0) FROM violations WHERE status='Paid'").fetchone()[0]
        row=tk.Frame(self.content,bg="#f5f7fb");row.pack(fill="x",pady=(0,15))
        self.card(row,"Pending",f"₹{pending:,.0f}","#e67e22");self.card(row,"Collected",f"₹{paid:,.0f}","#27ae60")
        bar=tk.Frame(self.content,bg="#f5f7fb");bar.pack(fill="x",pady=(0,10))
        ttk.Button(bar,text="Mark Selected as Paid",command=self.mark_paid).pack(side="left")
        ttk.Button(bar,text="Refresh",command=self.show_fines).pack(side="left",padx=8)
        frame=tk.Frame(self.content,bg="white",highlightbackground="#e0e0e0",highlightthickness=1);frame.pack(fill="both",expand=True)
        cols=("Violation ID","Vehicle","Type","Date","Fine","Status")
        self.ftree=ttk.Treeview(frame,columns=cols,show="headings")
        for c,w in zip(cols,(130,120,180,110,110,100)):
            self.ftree.heading(c,text=c);self.ftree.column(c,width=w,anchor="center")
        self.ftree.pack(fill="both",expand=True,padx=10,pady=10)
        for r in cur.execute("SELECT * FROM violations ORDER BY id DESC"):
            self.ftree.insert("", "end",values=(r["violation_id"],r["registration"],r["violation_type"],r["vdate"],f"₹{r['fine']:,.0f}",r["status"]))

    def mark_paid(self):
        sel=self.ftree.selection()
        if not sel: messagebox.showinfo("Select Fine","Select a fine first.");return
        vid=self.ftree.item(sel[0],"values")[0]
        r=self.db.execute("SELECT status FROM violations WHERE violation_id=?",(vid,)).fetchone()
        if r["status"]=="Paid": messagebox.showinfo("Already Paid","This fine is already marked as paid.");return
        if messagebox.askyesno("Confirm Payment",f"Mark {vid} as PAID?"):
            self.db.execute("UPDATE violations SET status='Paid' WHERE violation_id=?",(vid,));self.db.commit();self.show_fines()

    def show_analysis(self):
        self.clear(); self.set_active("Analytics")
        self.heading("Violation Analytics",
                     "Identify repeat offenders, frequent violations and fine patterns")

        cur = self.db.cursor()
        total = cur.execute(
            "SELECT COALESCE(SUM(fine),0) FROM violations"
        ).fetchone()[0]
        count = cur.execute(
            "SELECT COUNT(*) FROM violations"
        ).fetchone()[0]
        repeat_count = cur.execute(
            """SELECT COUNT(*) FROM (
                   SELECT registration
                   FROM violations
                   GROUP BY registration
                   HAVING COUNT(*) >= ?
               )""",
            (REPEAT_OFFENDER_THRESHOLD,)
        ).fetchone()[0]

        common = cur.execute(
            """SELECT violation_type, COUNT(*) AS n
               FROM violations
               GROUP BY violation_type
               ORDER BY n DESC, violation_type ASC
               LIMIT 1"""
        ).fetchone()

        maxv = cur.execute(
            """SELECT registration, COUNT(*) AS n
               FROM violations
               GROUP BY registration
               ORDER BY n DESC, registration ASC
               LIMIT 1"""
        ).fetchone()

        row = tk.Frame(self.content, bg="#f5f7fb")
        row.pack(fill="x", pady=(0,15))
        self.card(row, "Total Fine Amount", f"₹{total:,.0f}", "#2563eb")
        self.card(row, "Total Violations", count, "#7c3aed")
        self.card(row, "Repeat Offenders", repeat_count, "#dc2626")
        self.card(row, "Most Common", common["violation_type"] if common else "—", "#ea580c")

        # Repeat offender table
        body = tk.Frame(self.content, bg="white",
                        highlightbackground="#dbe3ec", highlightthickness=1)
        body.pack(fill="both", expand=True)

        top = tk.Frame(body, bg="white")
        top.pack(fill="x", padx=16, pady=(15,8))
        tk.Label(top, text=f"Repeat Offenders  •  {REPEAT_OFFENDER_THRESHOLD}+ violations",
                 bg="white", fg="#0f172a",
                 font=("Segoe UI",13,"bold")).pack(side="left")
        tk.Label(top,
                 text="A vehicle is flagged after its 2nd violation.",
                 bg="white", fg="#64748b",
                 font=("Segoe UI",9)).pack(side="right")

        columns = ("Rank","Vehicle","Owner","Violations","Total Fine","Alert")
        tr = ttk.Treeview(body, columns=columns, show="headings")
        for c,w in zip(columns,(70,150,220,120,140,130)):
            tr.heading(c,text=c)
            tr.column(c,width=w,anchor="center")
        tr.tag_configure("repeat", background="#fff7ed")
        tr.tag_configure("high", foreground="#b91c1c")
        tr.pack(fill="both", expand=True, padx=12, pady=(0,12))

        rows = cur.execute(
            """SELECT x.registration,
                      COALESCE(v.owner,'Unknown') AS owner,
                      COUNT(x.id) AS cnt,
                      COALESCE(SUM(x.fine),0) AS total
               FROM violations x
               LEFT JOIN vehicles v ON v.registration = x.registration
               GROUP BY x.registration, v.owner
               HAVING COUNT(x.id) >= ?
               ORDER BY cnt DESC, x.registration ASC""",
            (REPEAT_OFFENDER_THRESHOLD,)
        ).fetchall()

        if rows:
            for i,r in enumerate(rows,1):
                tr.insert("", "end",
                          values=(i, r["registration"], r["owner"], r["cnt"],
                                  f"₹{r['total']:,.0f}", "⚠ REPEAT OFFENDER"),
                          tags=("repeat",))
        else:
            # Never leave the analysis area looking broken/empty.
            tr.insert("", "end",
                      values=("—","No repeat offenders yet","Record 2 violations for a vehicle",
                              "—","—","Monitoring"),
                      tags=("high",))

        # Small insight strip
        insight = tk.Frame(self.content, bg="#eff6ff",
                           highlightbackground="#bfdbfe", highlightthickness=1)
        insight.pack(fill="x", pady=(12,0))
        max_text = (f"Highest violation count: {maxv['registration']} ({maxv['n']})"
                    if maxv else "Highest violation count: —")
        tk.Label(insight, text=f"ℹ  {max_text}    •    "
                 f"Repeat-offender rule: {REPEAT_OFFENDER_THRESHOLD}+ violations",
                 bg="#eff6ff", fg="#1d4ed8", font=("Segoe UI",9,"bold"),
                 anchor="w").pack(fill="x", padx=14, pady=9)

    def show_reports(self):
        self.clear();self.set_active("Reports")
        self.heading("Reports & Export","Generate and export traffic department records")
        box=tk.Frame(self.content,bg="white",highlightbackground="#e0e0e0",highlightthickness=1)
        box.pack(fill="x",pady=5)
        tk.Label(box,text="Export violation records to CSV",bg="white",font=("Segoe UI",13,"bold")).pack(anchor="w",padx=18,pady=(18,5))
        tk.Label(box,text="The CSV can be opened in Excel, Google Sheets or any spreadsheet application.",
                 bg="white",fg="#64748b").pack(anchor="w",padx=18,pady=(0,12))
        ttk.Button(box,text="Export All Violations",command=self.export_csv).pack(anchor="w",padx=18,pady=(0,18))
        box2=tk.Frame(self.content,bg="white",highlightbackground="#e0e0e0",highlightthickness=1)
        box2.pack(fill="x",pady=15)
        tk.Label(box2,text="Monthly Report",bg="white",font=("Segoe UI",13,"bold")).pack(anchor="w",padx=18,pady=(18,5))
        month=tk.StringVar(value=date.today().strftime("%Y-%m"))
        ttk.Entry(box2,textvariable=month,width=15).pack(anchor="w",padx=18,pady=5)
        out=tk.Label(box2,text="",bg="white",fg="#37474f",justify="left",font=("Segoe UI",10))
        out.pack(anchor="w",padx=18,pady=8)
        def gen():
            m=month.get().strip()
            rows=self.db.execute("""SELECT COUNT(*) cnt,COALESCE(SUM(fine),0) total,
                                    COALESCE(SUM(CASE WHEN status='Paid' THEN fine ELSE 0 END),0) paid
                                    FROM violations WHERE substr(vdate,1,7)=?""",(m,)).fetchone()
            common=self.db.execute("""SELECT violation_type,COUNT(*) n FROM violations
                                      WHERE substr(vdate,1,7)=? GROUP BY violation_type
                                      ORDER BY n DESC LIMIT 1""",(m,)).fetchone()
            out.config(text=f"Report for {m}\n\nViolations: {rows['cnt']}\nTotal fines: ₹{rows['total']:,.0f}\nCollected: ₹{rows['paid']:,.0f}\nMost common: {common['violation_type'] if common else 'No records'}")
        ttk.Button(box2,text="Generate Report",command=gen).pack(anchor="w",padx=18,pady=(0,18))

    def export_csv(self):
        path="traffic_violations_export.csv"
        rows=self.db.execute("SELECT violation_id,registration,violation_type,vdate,location,fine,status,priority FROM violations").fetchall()
        with open(path,"w",newline="",encoding="utf-8") as f:
            writer=csv.writer(f);writer.writerow(["Violation ID","Registration","Violation Type","Date","Location","Fine","Status","Priority"])
            for r in rows: writer.writerow(list(r))
        messagebox.showinfo("Export Complete",f"Exported {len(rows)} records to:\n{path}")

if __name__ == "__main__":
    root=tk.Tk()
    app=TrafficApp(root)
    root.mainloop()
