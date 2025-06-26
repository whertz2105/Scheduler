import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

# Data structures
employees = {}
shifts = []
assignments = {}

DAYS = ["Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Monday", "Tuesday"]

class SchedulerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Work Scheduler")
        self.geometry("1000x600")
        self.create_widgets()

    def create_widgets(self):
        menu = tk.Menu(self)
        self.config(menu=menu)
        emp_menu = tk.Menu(menu, tearoff=0)
        emp_menu.add_command(label="Add Employee", command=self.add_employee)
        emp_menu.add_command(label="Remove Employee", command=self.remove_employee)
        menu.add_cascade(label="Employees", menu=emp_menu)

        shift_menu = tk.Menu(menu, tearoff=0)
        shift_menu.add_command(label="Add Shift", command=self.add_shift)
        menu.add_cascade(label="Shifts", menu=shift_menu)

        self.schedule_frame = tk.Frame(self)
        self.schedule_frame.pack(fill=tk.BOTH, expand=True)
        self.build_table()

    def build_table(self):
        for widget in self.schedule_frame.winfo_children():
            widget.destroy()

        # Headers
        tk.Label(self.schedule_frame, text="Shifts").grid(row=0, column=0)
        for c, day in enumerate(DAYS, start=1):
            tk.Label(self.schedule_frame, text=day).grid(row=0, column=c)

        # Shift rows
        for r, shift in enumerate(shifts, start=1):
            row = r
            tk.Label(self.schedule_frame, text=f"{shift['name']}\n{shift['start']}-{shift['end']}").grid(row=row, column=0)
            for c in range(1, len(DAYS)+1):
                key = (shift['name'], c-1)
                var = tk.StringVar()
                opts = [name for name, jobs in employees.items() if shift['job'] in jobs]
                drop = ttk.Combobox(self.schedule_frame, textvariable=var, values=opts, state='readonly')
                drop.grid(row=row, column=c)
                drop.bind('<<ComboboxSelected>>', lambda e, k=key, v=var: assignments.__setitem__(k, v.get()))
        self.bottom_table()

    def bottom_table(self):
        rows_offset = len(shifts)+1
        tk.Label(self.schedule_frame, text="Projected Sales").grid(row=rows_offset, column=0)
        tk.Label(self.schedule_frame, text="Projected Labor ($)").grid(row=rows_offset+1, column=0)
        tk.Label(self.schedule_frame, text="Projected % Labor").grid(row=rows_offset+2, column=0)
        self.sales_vars = []
        self.labor_vars = []
        self.percent_vars = []
        for c in range(1, len(DAYS)+1):
            sv = tk.DoubleVar(value=0.0)
            lv = tk.DoubleVar(value=0.0)
            pv = tk.DoubleVar(value=0.0)
            self.sales_vars.append(sv)
            self.labor_vars.append(lv)
            self.percent_vars.append(pv)
            tk.Entry(self.schedule_frame, textvariable=sv, width=10).grid(row=rows_offset, column=c)
            tk.Label(self.schedule_frame, textvariable=lv).grid(row=rows_offset+1, column=c)
            tk.Label(self.schedule_frame, textvariable=pv).grid(row=rows_offset+2, column=c)
        calc_btn = tk.Button(self.schedule_frame, text="Calculate", command=self.calculate)
        calc_btn.grid(row=rows_offset+3, column=0, columnspan=len(DAYS)+1, pady=10)

    def calculate(self):
        # Reset labor totals
        for lv in self.labor_vars:
            lv.set(0.0)
        for (shift_name, day_idx), emp_name in assignments.items():
            if emp_name:
                shift = next(s for s in shifts if s['name'] == shift_name)
                pay = employees[emp_name][shift['job']]
                hours = shift['hours']
                cost = pay * hours
                current = self.labor_vars[day_idx].get()
                self.labor_vars[day_idx].set(current + cost)
        for idx in range(len(DAYS)):
            sales = self.sales_vars[idx].get()
            labor = self.labor_vars[idx].get()
            if sales > 0:
                self.percent_vars[idx].set(round((labor / sales) * 100, 2))
            else:
                self.percent_vars[idx].set(0.0)

    def add_employee(self):
        name = simpledialog.askstring("Employee", "Name")
        if not name:
            return
        job = simpledialog.askstring("Job Title", "Job title")
        if not job:
            return
        try:
            rate = float(simpledialog.askstring("Pay Rate", "Pay rate"))
        except (TypeError, ValueError):
            return
        if name not in employees:
            employees[name] = {}
        employees[name][job] = rate
        self.build_table()

    def remove_employee(self):
        if not employees:
            return
        options = list(employees.keys())
        name = simpledialog.askstring("Remove", f"Enter name to remove\nOptions: {', '.join(options)}")
        if name in employees:
            del employees[name]
        self.build_table()

    def add_shift(self):
        name = simpledialog.askstring("Shift", "Shift name")
        if not name:
            return
        job = simpledialog.askstring("Job Title", "Job title for this shift")
        if not job:
            return
        start = simpledialog.askstring("Start Time", "Start time (e.g., 06:00)")
        end = simpledialog.askstring("End Time", "End time (e.g., 14:00)")
        try:
            hours = float(simpledialog.askstring("Hours", "Hours"))
        except (TypeError, ValueError):
            hours = 0.0
        shifts.append({'name': name, 'job': job, 'start': start, 'end': end, 'hours': hours})
        self.build_table()

if __name__ == '__main__':
    app = SchedulerApp()
    app.mainloop()
