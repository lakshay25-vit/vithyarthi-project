import tkinter as tk
from tkinter import messagebox, simpledialog
import pandas as pd
import os

ELECTRICITY_RATES = {
    "India": 0.08,
}

APPLIANCE_POWER = {
    "TV": 100,
    "Fridge": 150,
    "AC": 1000,
    "Laptop": 50,
    "Washing Machine": 500,
}

class UserProfile:
    def __init__(self, name="", location="India"):
        self.name = name
        self.location = location
        self.rate = ELECTRICITY_RATES.get(location, 0.08)

    def save_profile(self, filename="user_profile.csv"):
        df = pd.DataFrame([{"name": self.name, "location": self.location}])
        df.to_csv(filename, index=False)

    @staticmethod
    def load_profile(filename="user_profile.csv"):
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            return UserProfile(df.iloc[0]["name"], df.iloc[0]["location"])
        return None

class EnergyTracker:
    def __init__(self, user_profile):
        self.user = user_profile
        self.logs = pd.DataFrame(columns=["date", "appliance", "hours_used"])
        self.load_logs()

    def load_logs(self, filename="energy_logs.csv"):
        if os.path.exists(filename):
            self.logs = pd.read_csv(filename)
            self.logs["date"] = pd.to_datetime(self.logs["date"])

    def save_logs(self, filename="energy_logs.csv"):
        self.logs.to_csv(filename, index=False)

    def add_log(self, appliance, hours_used, date=None):
        if appliance not in APPLIANCE_POWER:
            raise ValueError(f"Appliance '{appliance}' not recognized.")
        if hours_used < 0 or hours_used > 24:
            raise ValueError("Hours must be 0-24.")
        date = date or pd.Timestamp.today()
        new_log = pd.DataFrame([{"date": date, "appliance": appliance, "hours_used": hours_used}])
        self.logs = pd.concat([self.logs, new_log], ignore_index=True)
        self.save_logs()

    def calculate_cost(self, start_date=None, end_date=None):
        df = self.logs
        if start_date:
            df = df[df["date"] >= start_date]
        if end_date:
            df = df[df["date"] <= end_date]
        df["power_kwh"] = df.apply(lambda row: (APPLIANCE_POWER[row["appliance"]] * row["hours_used"]) / 1000, axis=1)
        df["cost"] = df["power_kwh"] * self.user.rate
        return df.groupby("appliance")["cost"].sum().to_dict(), df["cost"].sum()

class EnergyTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Energy Tracker")
        self.tracker = None
        self.load_or_create_profile()

    def load_or_create_profile(self):
        profile = UserProfile.load_profile()
        if profile:
            self.tracker = EnergyTracker(profile)
            self.show_main_menu()
        else:
            self.create_profile()

    def create_profile(self):
        name = simpledialog.askstring("Profile", "Name:")
        location = "India"
        if name:
            profile = UserProfile(name, location)
            profile.save_profile()
            self.tracker = EnergyTracker(profile)
            self.show_main_menu()
        else:
            messagebox.showerror("Error", "Failed.")

    def show_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text=f"Hi {self.tracker.user.name}!").pack()
        tk.Button(self.root, text="Add Log", command=self.add_log_ui).pack()
        tk.Button(self.root, text="View Costs", command=self.costs_ui).pack()
        tk.Button(self.root, text="Exit", command=self.root.quit).pack()

    def add_log_ui(self):
        appliance = simpledialog.askstring("Log", f"Appliance ({', '.join(APPLIANCE_POWER.keys())}):")
        hours = simpledialog.askfloat("Log", "Hours today:")
        try:
            self.tracker.add_log(appliance, hours)
            messagebox.showinfo("OK", "Added!")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def costs_ui(self):
        costs, total = self.tracker.calculate_cost()
        msg = f"Total Cost: ${total:.2f}\nCosts by Appliance: {costs}"
        messagebox.showinfo("Costs", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = EnergyTrackerApp(root)
    root.mainloop()

