from tkinter import *
from tkinter import ttk
import sqlite3
from datetime import datetime
import os

root = Tk()
root.title("John Lloyd Parking Lot")
root.geometry("1000x800")
root.config(bg="#A9B6C2") 

font_style = ("Segoe UI", 12)
button_font = ("Segoe UI", 12, "bold")

db_path = "E:/PARKING LOT SYSTEM/parking_lot_system.db"

def initialize_database():
    if not os.path.exists(db_path):  
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS parking_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_number TEXT,
            owner_name TEXT,
            contact_number TEXT,
            vehicle_type TEXT,
            parking_status TEXT,
            date TEXT,
            time TEXT,
            exit_time TEXT,
            time_consume TEXT
        )''')
        conn.commit()
        conn.close()

def add_exit_time_column():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("PRAGMA table_info(parking_records)")
    columns = c.fetchall()
    column_names = [column[1] for column in columns]
    if "exit_time" not in column_names:
        c.execute("ALTER TABLE parking_records ADD COLUMN exit_time TEXT")
        conn.commit()
    conn.close()

# Function to add the `time_consume` column if it doesn't exist already
def add_time_consume_column():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("PRAGMA table_info(parking_records)")
    columns = c.fetchall()
    column_names = [column[1] for column in columns]
    if "time_consume" not in column_names:
        c.execute("ALTER TABLE parking_records ADD COLUMN time_consume TEXT")
        conn.commit()
    conn.close()

def add_record():
    if vehicle_number.get() == "" or owner_name.get() == "" or contact_number.get() == "" or vehicle_type.get() == "" or parking_status.get() == "":
        return

    current_date = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime('%H:%M:%S')

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("INSERT INTO parking_records (vehicle_number, owner_name, contact_number, vehicle_type, parking_status, date, time, exit_time, time_consume) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ",
              (vehicle_number.get(), owner_name.get(), contact_number.get(), vehicle_type.get(), parking_status.get(), current_date, current_time, None, None))
    conn.commit()

    vehicle_number.delete(0, END)
    owner_name.delete(0, END)
    contact_number.delete(0, END)
    vehicle_type.set('')
    parking_status.set('')

    conn.close()

def delete_record():
    try:
        record_id = int(edit_id.get())
    except ValueError:
        return
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM parking_records WHERE id=?", (record_id,))
    conn.commit()
    conn.close()
    edit_id.delete(0, END)

# Function to edit an existing record based on ID
def edit_record():
    try:
        record_id = int(edit_id.get())
    except ValueError:
        return

    editor = Toplevel(root)
    editor.title("Update Record")
    editor.geometry("400x450")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT * FROM parking_records WHERE id=?", (record_id,))
    record = c.fetchone()

    if not record:
        editor.destroy()
        return

    ttk.Label(editor, text="Vehicle Number", font=font_style).grid(row=0, column=0, padx=20, pady=10, sticky=W)
    vehicle_number_editor = ttk.Entry(editor, width=30)
    vehicle_number_editor.grid(row=0, column=1, pady=10)
    vehicle_number_editor.insert(0, record[1])

    ttk.Label(editor, text="Owner Name", font=font_style).grid(row=1, column=0, padx=20, pady=10, sticky=W)
    owner_name_editor = ttk.Entry(editor, width=30)
    owner_name_editor.grid(row=1, column=1, pady=10)
    owner_name_editor.insert(0, record[2])

    ttk.Label(editor, text="Contact Number", font=font_style).grid(row=2, column=0, padx=20, pady=10, sticky=W)
    contact_number_editor = ttk.Entry(editor, width=30)
    contact_number_editor.grid(row=2, column=1, pady=10)
    contact_number_editor.insert(0, record[3])

    ttk.Label(editor, text="Vehicle Type", font=font_style).grid(row=3, column=0, padx=20, pady=10, sticky=W)
    vehicle_type_label = ttk.Label(editor, text=record[4], font=font_style)
    vehicle_type_label.grid(row=3, column=1, pady=10)

    ttk.Label(editor, text="Parking Status", font=font_style).grid(row=4, column=0, padx=20, pady=10, sticky=W)
    parking_status_editor = ttk.Combobox(editor, width=28, values=["Parked", "Exit"])
    parking_status_editor.grid(row=4, column=1, pady=10)
    parking_status_editor.set(record[5])

    def save_update():
        if parking_status_editor.get() == "Exit":
            exit_time = datetime.now().strftime('%H:%M:%S')
            parked_time = datetime.strptime(record[7], '%H:%M:%S')
            time_diff = datetime.strptime(exit_time, '%H:%M:%S') - parked_time
            time_consumed = str(time_diff)
        else:
            exit_time = None
            time_consumed = None

        c.execute("""UPDATE parking_records SET
                        vehicle_number = ?, owner_name = ?, contact_number = ?, parking_status = ?, exit_time = ?, time_consume = ?
                        WHERE id = ?""",
                  (vehicle_number_editor.get(), owner_name_editor.get(), contact_number_editor.get(), parking_status_editor.get(), exit_time, time_consumed, record_id))
        conn.commit()
        conn.close()
        editor.destroy()

    ttk.Button(editor, text="Save Changes", command=save_update, width=15).grid(row=5, column=0, columnspan=2, pady=20)

    editor.mainloop()

def view_records():
    view_window = Toplevel(root)
    view_window.title("View Records")
    view_window.geometry("900x600")

    columns = ("id", "vehicle_number", "owner_name", "contact_number", "vehicle_type", "parking_status", "date", "time", "exit_time", "time_consume")
    tree = ttk.Treeview(view_window, columns=columns, show="headings", height=20)

    for col in columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col, anchor=CENTER, width=100)

    tree.pack(fill=BOTH, expand=True, padx=20, pady=20)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM parking_records")
    records = c.fetchall()

    for record in records:
        tree.insert("", END, values=record)

    conn.close()

ttk.Label(root, text="Vehicle Plate Number", font=font_style, background="#ffffff").grid(row=0, column=0, padx=20, pady=10, sticky=W)
vehicle_number = ttk.Entry(root, width=30)
vehicle_number.grid(row=0, column=1, pady=10)

ttk.Label(root, text="Owner Name", font=font_style, background="#ffffff").grid(row=1, column=0, padx=20, pady=10, sticky=W)
owner_name = ttk.Entry(root, width=30)
owner_name.grid(row=1, column=1, pady=10)

ttk.Label(root, text="Contact Number", font=font_style, background="#ffffff").grid(row=2, column=0, padx=20, pady=10, sticky=W)
contact_number = ttk.Entry(root, width=30)
contact_number.grid(row=2, column=1, pady=10)

ttk.Label(root, text="Vehicle Type", font=font_style, background="#ffffff").grid(row=3, column=0, padx=20, pady=10, sticky=W)
vehicle_type = ttk.Combobox(root, width=28, values=["Truck", "SUV", "Sedan", "Motor", "EV", "Bike"])
vehicle_type.grid(row=3, column=1, pady=10)

ttk.Label(root, text="Parking Status", font=font_style, background="#ffffff").grid(row=4, column=0, padx=20, pady=10, sticky=W)
parking_status = ttk.Combobox(root, width=28, values=["Parked", "Exit"])
parking_status.grid(row=4, column=1, pady=10)

ttk.Label(root, text="Edit/Delete by ID", font=font_style, background="#ffffff").grid(row=5, column=0, padx=20, pady=10, sticky=W)
edit_id = ttk.Entry(root, width=30)
edit_id.grid(row=5, column=1, pady=10)

style = ttk.Style()
style.configure("Add.TButton", font=button_font, padding=6, background="#4CAF50", foreground="black")
style.configure("Edit.TButton", font=button_font, padding=6, background="#FF9800", foreground="black")
style.configure("Delete.TButton", font=button_font, padding=6, background="#F44336", foreground="black")
style.configure("Show.TButton", font=button_font, padding=6, background="#2196F3", foreground="black")

ttk.Button(root, text="Check-in Vehicle", command=add_record, style="Add.TButton").grid(row=6, column=0, pady=20, padx=10, sticky=W)
ttk.Button(root, text="Update Vehicle Info", command=edit_record, style="Edit.TButton").grid(row=6, column=1, pady=20, padx=10, sticky=W)
ttk.Button(root, text="Delete Vehicle Record", command=delete_record, style="Delete.TButton").grid(row=6, column=2, pady=20, padx=10, sticky=W)
ttk.Button(root, text="View Parking Log", command=view_records, style="Show.TButton").grid(row=6, column=3, pady=20, padx=10, sticky=W)

initialize_database()
add_exit_time_column()
add_time_consume_column()

root.mainloop()
