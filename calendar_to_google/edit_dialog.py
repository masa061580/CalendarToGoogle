"""Event edit dialog."""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass


@dataclass
class EditedEvent:
    """Edited event data."""
    title: str
    start_date: datetime
    end_date: datetime
    all_day: bool
    description: str
    cancelled: bool = False


class EventEditDialog:
    """Dialog for editing event before adding to calendar."""

    def __init__(self, title: str, start_date: datetime, all_day: bool, description: str = ""):
        self.result: Optional[EditedEvent] = None
        self._title = title
        self._start_date = start_date
        self._all_day = all_day
        self._description = description

    def show(self) -> Optional[EditedEvent]:
        """Show the dialog and return edited event."""
        self.root = tk.Tk()
        self.root.title("Add to Google Calendar")
        self.root.geometry("450x400")
        self.root.resizable(False, False)

        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - 450) // 2
        y = (self.root.winfo_screenheight() - 400) // 2
        self.root.geometry(f"450x400+{x}+{y}")

        # Keep on top
        self.root.attributes('-topmost', True)

        self._create_widgets()

        self.root.mainloop()
        return self.result

    def _create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(main_frame, text="Title:", font=('', 10, 'bold')).pack(anchor=tk.W)
        self.title_var = tk.StringVar(value=self._title)
        title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=50, font=('', 11))
        title_entry.pack(fill=tk.X, pady=(0, 10))
        title_entry.focus_set()
        title_entry.select_range(0, tk.END)

        # Date frame
        date_frame = ttk.Frame(main_frame)
        date_frame.pack(fill=tk.X, pady=(0, 10))

        # Start date
        ttk.Label(date_frame, text="Date:", font=('', 10, 'bold')).pack(anchor=tk.W)

        date_row = ttk.Frame(date_frame)
        date_row.pack(fill=tk.X)

        self.year_var = tk.StringVar(value=str(self._start_date.year))
        self.month_var = tk.StringVar(value=str(self._start_date.month))
        self.day_var = tk.StringVar(value=str(self._start_date.day))

        ttk.Entry(date_row, textvariable=self.year_var, width=6).pack(side=tk.LEFT)
        ttk.Label(date_row, text="/").pack(side=tk.LEFT)
        ttk.Entry(date_row, textvariable=self.month_var, width=4).pack(side=tk.LEFT)
        ttk.Label(date_row, text="/").pack(side=tk.LEFT)
        ttk.Entry(date_row, textvariable=self.day_var, width=4).pack(side=tk.LEFT)

        # All day checkbox
        self.all_day_var = tk.BooleanVar(value=self._all_day)
        ttk.Checkbutton(
            date_row, text="All day", variable=self.all_day_var,
            command=self._toggle_time
        ).pack(side=tk.LEFT, padx=(20, 0))

        # Time frame
        self.time_frame = ttk.Frame(main_frame)
        self.time_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(self.time_frame, text="Time:", font=('', 10, 'bold')).pack(anchor=tk.W)

        time_row = ttk.Frame(self.time_frame)
        time_row.pack(fill=tk.X)

        # Start time
        self.start_hour_var = tk.StringVar(value=str(self._start_date.hour).zfill(2))
        self.start_min_var = tk.StringVar(value=str(self._start_date.minute).zfill(2))

        ttk.Label(time_row, text="Start:").pack(side=tk.LEFT)
        ttk.Entry(time_row, textvariable=self.start_hour_var, width=4).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(time_row, text=":").pack(side=tk.LEFT)
        ttk.Entry(time_row, textvariable=self.start_min_var, width=4).pack(side=tk.LEFT)

        # End time (default 1 hour later)
        end_time = self._start_date + timedelta(hours=1)
        self.end_hour_var = tk.StringVar(value=str(end_time.hour).zfill(2))
        self.end_min_var = tk.StringVar(value=str(end_time.minute).zfill(2))

        ttk.Label(time_row, text="  End:").pack(side=tk.LEFT, padx=(15, 0))
        ttk.Entry(time_row, textvariable=self.end_hour_var, width=4).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(time_row, text=":").pack(side=tk.LEFT)
        ttk.Entry(time_row, textvariable=self.end_min_var, width=4).pack(side=tk.LEFT)

        # Toggle time visibility
        self._toggle_time()

        # Description
        ttk.Label(main_frame, text="Description:", font=('', 10, 'bold')).pack(anchor=tk.W)
        self.desc_text = tk.Text(main_frame, height=5, width=50, font=('', 10))
        self.desc_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        if self._description:
            self.desc_text.insert(tk.END, self._description)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="Cancel", command=self._cancel, width=12).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="Add to Calendar", command=self._submit, width=15).pack(side=tk.RIGHT)

        # Bind Enter key
        self.root.bind('<Return>', lambda e: self._submit())
        self.root.bind('<Escape>', lambda e: self._cancel())

    def _toggle_time(self):
        """Toggle time fields visibility."""
        if self.all_day_var.get():
            for child in self.time_frame.winfo_children():
                child.pack_forget()
        else:
            ttk.Label(self.time_frame, text="Time:", font=('', 10, 'bold')).pack(anchor=tk.W)
            time_row = ttk.Frame(self.time_frame)
            time_row.pack(fill=tk.X)
            ttk.Label(time_row, text="Start:").pack(side=tk.LEFT)
            ttk.Entry(time_row, textvariable=self.start_hour_var, width=4).pack(side=tk.LEFT, padx=(5, 0))
            ttk.Label(time_row, text=":").pack(side=tk.LEFT)
            ttk.Entry(time_row, textvariable=self.start_min_var, width=4).pack(side=tk.LEFT)
            ttk.Label(time_row, text="  End:").pack(side=tk.LEFT, padx=(15, 0))
            ttk.Entry(time_row, textvariable=self.end_hour_var, width=4).pack(side=tk.LEFT, padx=(5, 0))
            ttk.Label(time_row, text=":").pack(side=tk.LEFT)
            ttk.Entry(time_row, textvariable=self.end_min_var, width=4).pack(side=tk.LEFT)

    def _submit(self):
        """Submit the form."""
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get())
            day = int(self.day_var.get())

            if self.all_day_var.get():
                start = datetime(year, month, day)
                end = start
            else:
                start_hour = int(self.start_hour_var.get())
                start_min = int(self.start_min_var.get())
                end_hour = int(self.end_hour_var.get())
                end_min = int(self.end_min_var.get())

                start = datetime(year, month, day, start_hour, start_min)
                end = datetime(year, month, day, end_hour, end_min)

                if end <= start:
                    end = start + timedelta(hours=1)

            self.result = EditedEvent(
                title=self.title_var.get() or "New Event",
                start_date=start,
                end_date=end,
                all_day=self.all_day_var.get(),
                description=self.desc_text.get("1.0", tk.END).strip(),
                cancelled=False
            )
        except ValueError:
            self.result = None

        self.root.destroy()

    def _cancel(self):
        """Cancel the dialog."""
        self.result = EditedEvent(
            title="", start_date=datetime.now(), end_date=datetime.now(),
            all_day=True, description="", cancelled=True
        )
        self.root.destroy()


def show_edit_dialog(title: str, start_date: datetime, all_day: bool, description: str = "") -> Optional[EditedEvent]:
    """Show edit dialog and return result."""
    dialog = EventEditDialog(title, start_date, all_day, description)
    return dialog.show()
