"""Event edit dialog."""

import customtkinter as ctk
from datetime import datetime, timedelta
from typing import Optional, Any
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

    def __init__(self, master: Any, title: str, start_date: datetime, all_day: bool, description: str = ""):
        self.master = master
        self.result: Optional[EditedEvent] = None
        self._title = title
        self._start_date = start_date
        self._all_day = all_day
        self._description = description
        
        # Set theme (global setting, safe to call multiple times)
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

    def show(self) -> Optional[EditedEvent]:
        """Show the dialog and return edited event."""
        if self.master:
            self.window = ctk.CTkToplevel(self.master)
        else:
            # Fallback if no master provided (though should be avoided in new architecture)
            self.window = ctk.CTk()
            
        self.window.title("Add to Google Calendar")
        self.window.geometry("500x550")
        self.window.resizable(False, False)

        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 500) // 2
        y = (self.window.winfo_screenheight() - 550) // 2
        self.window.geometry(f"500x550+{x}+{y}")

        # Keep on top and force focus
        self.window.attributes('-topmost', True)
        self.window.lift()
        self.window.focus_force()
        
        # Ensure it stays on top briefly then releases
        self.window.after(100, lambda: self.window.attributes('-topmost', False))
        self.window.after(100, lambda: self.window.attributes('-topmost', True))

        self._create_widgets()

        # Make modal
        self.window.grab_set()
        self.window.wait_window()
        
        return self.result

    def _create_widgets(self):
        """Create dialog widgets."""
        main_frame = ctk.CTkFrame(self.window, corner_radius=10)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(main_frame, text="Title", font=("Roboto", 14, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        self.title_var = ctk.StringVar(value=self._title)
        title_entry = ctk.CTkEntry(main_frame, textvariable=self.title_var, width=400, font=("Roboto", 12))
        title_entry.pack(fill="x", padx=20, pady=(0, 10))
        title_entry.focus_set()
        
        # Date frame
        date_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        date_frame.pack(fill="x", padx=20, pady=(0, 10))

        # Start date
        ctk.CTkLabel(date_frame, text="Date", font=("Roboto", 14, "bold")).pack(anchor="w", pady=(0, 5))
        
        date_row = ctk.CTkFrame(date_frame, fg_color="transparent")
        date_row.pack(fill="x")

        self.year_var = ctk.StringVar(value=str(self._start_date.year))
        self.month_var = ctk.StringVar(value=str(self._start_date.month))
        self.day_var = ctk.StringVar(value=str(self._start_date.day))

        ctk.CTkEntry(date_row, textvariable=self.year_var, width=60).pack(side="left")
        ctk.CTkLabel(date_row, text="/").pack(side="left", padx=5)
        ctk.CTkEntry(date_row, textvariable=self.month_var, width=40).pack(side="left")
        ctk.CTkLabel(date_row, text="/").pack(side="left", padx=5)
        ctk.CTkEntry(date_row, textvariable=self.day_var, width=40).pack(side="left")

        # All day checkbox
        self.all_day_var = ctk.BooleanVar(value=self._all_day)
        ctk.CTkCheckBox(
            date_row, text="All day", variable=self.all_day_var,
            command=self._toggle_time, font=("Roboto", 12)
        ).pack(side="left", padx=(30, 0))

        # Time frame
        self.time_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.time_frame.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(self.time_frame, text="Time", font=("Roboto", 14, "bold")).pack(anchor="w", pady=(0, 5))

        time_row = ctk.CTkFrame(self.time_frame, fg_color="transparent")
        time_row.pack(fill="x")

        # Start time
        self.start_hour_var = ctk.StringVar(value=str(self._start_date.hour).zfill(2))
        self.start_min_var = ctk.StringVar(value=str(self._start_date.minute).zfill(2))

        ctk.CTkLabel(time_row, text="Start:", font=("Roboto", 12)).pack(side="left")
        ctk.CTkEntry(time_row, textvariable=self.start_hour_var, width=40).pack(side="left", padx=(5, 0))
        ctk.CTkLabel(time_row, text=":").pack(side="left", padx=2)
        ctk.CTkEntry(time_row, textvariable=self.start_min_var, width=40).pack(side="left")

        # End time (default 1 hour later)
        end_time = self._start_date + timedelta(hours=1)
        self.end_hour_var = ctk.StringVar(value=str(end_time.hour).zfill(2))
        self.end_min_var = ctk.StringVar(value=str(end_time.minute).zfill(2))

        ctk.CTkLabel(time_row, text="End:", font=("Roboto", 12)).pack(side="left", padx=(20, 0))
        ctk.CTkEntry(time_row, textvariable=self.end_hour_var, width=40).pack(side="left", padx=(5, 0))
        ctk.CTkLabel(time_row, text=":").pack(side="left", padx=2)
        ctk.CTkEntry(time_row, textvariable=self.end_min_var, width=40).pack(side="left")

        # Toggle time visibility
        self._toggle_time()

        # Description
        ctk.CTkLabel(main_frame, text="Description", font=("Roboto", 14, "bold")).pack(anchor="w", padx=20, pady=(0, 5))
        self.desc_text = ctk.CTkTextbox(main_frame, height=100, font=("Roboto", 12))
        self.desc_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        if self._description:
            self.desc_text.insert("1.0", self._description)

        # Buttons
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkButton(
            btn_frame, text="Add to Calendar", command=self._submit,
            width=150, height=40, font=("Roboto", 13, "bold")
        ).pack(side="right")
        
        ctk.CTkButton(
            btn_frame, text="Cancel", command=self._cancel,
            width=100, height=40, fg_color="transparent", border_width=2,
            text_color=("gray10", "#DCE4EE"), font=("Roboto", 13)
        ).pack(side="right", padx=(0, 10))

        # Bind Enter key
        self.window.bind('<Return>', lambda e: self._submit())
        self.window.bind('<Escape>', lambda e: self._cancel())

    def _toggle_time(self):
        """Toggle time fields visibility."""
        if self.all_day_var.get():
            for child in self.time_frame.winfo_children():
                child.pack_forget()
        else:
            ctk.CTkLabel(self.time_frame, text="Time", font=("Roboto", 14, "bold")).pack(anchor="w", pady=(0, 5))
            time_row = ctk.CTkFrame(self.time_frame, fg_color="transparent")
            time_row.pack(fill="x")
            
            ctk.CTkLabel(time_row, text="Start:", font=("Roboto", 12)).pack(side="left")
            ctk.CTkEntry(time_row, textvariable=self.start_hour_var, width=40).pack(side="left", padx=(5, 0))
            ctk.CTkLabel(time_row, text=":").pack(side="left", padx=2)
            ctk.CTkEntry(time_row, textvariable=self.start_min_var, width=40).pack(side="left")
            
            ctk.CTkLabel(time_row, text="End:", font=("Roboto", 12)).pack(side="left", padx=(20, 0))
            ctk.CTkEntry(time_row, textvariable=self.end_hour_var, width=40).pack(side="left", padx=(5, 0))
            ctk.CTkLabel(time_row, text=":").pack(side="left", padx=2)
            ctk.CTkEntry(time_row, textvariable=self.end_min_var, width=40).pack(side="left")

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
                description=self.desc_text.get("1.0", "end-1c").strip(),
                cancelled=False
            )
        except ValueError:
            self.result = None

        self.window.destroy()

    def _cancel(self):
        """Cancel the dialog."""
        self.result = EditedEvent(
            title="", start_date=datetime.now(), end_date=datetime.now(),
            all_day=True, description="", cancelled=True
        )
        self.window.destroy()


def show_edit_dialog(master: Any, title: str, start_date: datetime, all_day: bool, description: str = "") -> Optional[EditedEvent]:
    """Show edit dialog and return result."""
    dialog = EventEditDialog(master, title, start_date, all_day, description)
    return dialog.show()

