import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from contextlib import redirect_stdout
from io import StringIO
import os

from config.config_loader import load_config
from workflows.workflow_manager import run_workflow
from security.permissions import is_action_allowed
from security.executor import execute_action
from security.audit_logger import log_action
from scheduler.schedule_config import load_schedules
from scheduler.schedule_history import load_history, save_history
from scheduler.schedule_manager import current_time, get_due_schedules

BG = '#0D0D0D'
PANEL = '#191919'
LINE = '#383838'
WHITE = '#F5F5F5'
GRAY = '#AAAAAA'
SERIF = ('Times New Roman', 20)
BODY = ('Georgia', 14)
MONO = ('Courier New', 12)
WORKFLOWS = {'Organize files': 'organize', 'Archive old files': 'archive', 'Find duplicates': 'duplicates'}


class SecureFlow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('SecureFlow')
        self.geometry('1150x780')
        self.minsize(900, 650)
        self.configure(fg_color=BG)
        self.pending = None
        self.buttons = {}
        self.sidebar = ctk.CTkFrame(self, width=225, fg_color=PANEL, corner_radius=0)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)
        self.label(self.sidebar, 'SecureFlow.', 36).pack(pady=(35, 0))
        ctk.CTkLabel(self.sidebar, text='The art of secure automation.', font=('Baskerville', 15, 'italic'), text_color=GRAY).pack(pady=(0, 35))
        for i, name in enumerate(['Overview', 'Workflows', 'Schedules', 'Activity', 'Settings'], 1):
            self.buttons[name] = self.button(self.sidebar, f'{i:02d}   {name}', lambda n=name: self.navigate(n), False)
            self.buttons[name].pack(fill='x', padx=15, pady=4)
        self.label(self.sidebar, 'PERSONAL WORKSPACE', font=MONO, color=GRAY).pack(side='bottom', pady=25)
        viewport = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        viewport.pack(side='left', fill='both', expand=True, padx=28, pady=24)
        self.page_canvas = tk.Canvas(viewport, bg=BG, highlightthickness=0, bd=0, yscrollincrement=1)
        scrollbar = ctk.CTkScrollbar(viewport, command=self.page_canvas.yview)
        scrollbar.pack(side='right', fill='y')
        self.page_canvas.pack(side='left', fill='both', expand=True)
        self.page_canvas.configure(yscrollcommand=scrollbar.set)
        self.content = ctk.CTkFrame(self.page_canvas, fg_color=BG, corner_radius=0)
        self.page_window = self.page_canvas.create_window((0, 0), window=self.content, anchor='nw')
        self.content.bind('<Configure>', self.update_scroll_region, add='+')
        self.page_canvas.bind('<Configure>', self.resize_page, add='+')
        self.bind_class('SecureFlowScroll', '<MouseWheel>', self.scroll_page)
        self.touchpad_command = self.register(self.scroll_touchpad)
        try:
            script = self.touchpad_command + ' %D; break'
            self.tk.call('bind', 'SecureFlowScroll', '<TouchpadScroll>', script)
            self.tk.call('bind', 'all', '<TouchpadScroll>', script)
        except tk.TclError:
            pass
        if self.tk.call('tk', 'windowingsystem') == 'x11':
            self.bind_class('SecureFlowScroll', '<Button-4>', self.scroll_page)
            self.bind_class('SecureFlowScroll', '<Button-5>', self.scroll_page)
        self.navigate('Overview')

    def update_scroll_region(self, event=None):
        self.page_canvas.configure(scrollregion=self.page_canvas.bbox('all'))

    def resize_page(self, event):
        self.page_canvas.itemconfigure(self.page_window, width=event.width)
        self.update_scroll_region()

    def install_scroll_bindings(self, widget):
        def install(path):
            tags = self.tk.splitlist(self.tk.call('bindtags', path))
            if 'SecureFlowScroll' not in tags:
                self.tk.call('bindtags', path, ('SecureFlowScroll',) + tags)
            for child in self.tk.splitlist(self.tk.call('winfo', 'children', path)):
                install(child)
        install(str(widget))

    def scroll_touchpad(self, raw_delta):
        delta = int(raw_delta) & 0xFFFF
        if delta >= 0x8000:
            delta -= 0x10000
        if not delta:
            return
        self.update_scroll_region()
        bounds = self.page_canvas.bbox('all')
        if not bounds:
            return
        height = max(1, bounds[3] - bounds[1])
        first, last = self.page_canvas.yview()
        if last - first < 1:
            self.page_canvas.yview_moveto(max(0, min(1, first - delta / height)))
        else:
            widget = self.winfo_containing(*self.winfo_pointerxy())
            if isinstance(widget, tk.Text):
                try:
                    widget.yview_scroll(-delta, 'pixels')
                except tk.TclError:
                    widget.yview_scroll(-1 if delta > 0 else 1, 'units')

    def scroll_page(self, event):
        delta = getattr(event, 'delta', 0)
        number = getattr(event, 'num', None)
        if number == 4:
            direction = -1
        elif number == 5:
            direction = 1
        elif delta:
            direction = -1 if delta > 0 else 1
        else:
            return
        widget = event.widget
        if isinstance(widget, tk.Text):
            first, last = widget.yview()
            if (direction < 0 and first > 0) or (direction > 0 and last < 1):
                widget.yview_scroll(direction, 'units')
                return 'break'
        self.page_canvas.yview_scroll(direction * 32, 'units')
        return 'break'

    def label(self, parent, text, size=20, font=None, color=WHITE):
        return ctk.CTkLabel(parent, text=text, font=font or ('Times New Roman', size), text_color=color, anchor='w', justify='left')

    def button(self, parent, text, command, primary=True):
        return ctk.CTkButton(parent, text=text, command=command, font=BODY, corner_radius=0, height=40, fg_color=WHITE if primary else PANEL, text_color=BG if primary else WHITE, hover_color='#CCCCCC' if primary else LINE)

    def card(self):
        frame = ctk.CTkFrame(self.content, fg_color=PANEL, border_width=1, border_color=LINE, corner_radius=0)
        frame.pack(fill='x', pady=6)
        return frame

    def heading(self, title, subtitle):
        self.label(self.content, title, 42).pack(anchor='w')
        self.label(self.content, subtitle, font=('Baskerville', 20, 'italic'), color=GRAY).pack(anchor='w', pady=(0, 18))

    def textbox(self, height=240):
        box = ctk.CTkTextbox(self.content, height=height, fg_color=PANEL, text_color=WHITE, font=MONO, corner_radius=0, wrap='word', border_width=1, border_color=LINE)
        box.pack(fill='x', pady=10)
        return box

    def write(self, box, text):
        box.configure(state='normal')
        box.delete('1.0', 'end')
        box.insert('1.0', text)
        box.configure(state='disabled')

    def navigate(self, page):
        if self.pending is not None:
            if not messagebox.askyesno('Discard preview?', 'Cancel the current preview and leave this page?', parent=self):
                return
            self.cancel()
        for child in self.content.winfo_children():
            child.destroy()
        for name, button in self.buttons.items():
            button.configure(fg_color=WHITE if name == page else PANEL, text_color=BG if name == page else WHITE, hover_color='#CCCCCC' if name == page else LINE)
        try:
            getattr(self, 'show_' + page.lower())()
        except Exception as error:
            self.label(self.content, str(error), font=BODY).pack(anchor='w')
        self.install_scroll_bindings(self)
        self.update_idletasks()
        self.update_scroll_region()
        self.page_canvas.yview_moveto(0)

    def logs(self):
        path = Path('activity.log')
        return path.read_text(encoding='utf-8', errors='replace').splitlines() if path.exists() else []

    def show_overview(self):
        self.heading('Your workspace.', 'A little order in the everyday.')
        logs = self.logs()
        due = get_due_schedules(load_schedules(), load_history())
        stats = [('Files moved (logged)', sum(x.split(' | ', 2)[1:2] == ['SUCCESS'] for x in logs)), ('Blocked actions (logged)', sum(x.split(' | ', 2)[1:2] == ['BLOCKED'] for x in logs)), ('Schedules due', len(due))]
        for name, count in stats:
            card = self.card()
            self.label(card, str(count), 36).pack(side='left', padx=20, pady=12)
            self.label(card, name, font=BODY, color=GRAY).pack(side='left', padx=12)
        self.label(self.content, 'Quick actions', 28).pack(anchor='w', pady=(20, 8))
        for name in WORKFLOWS:
            self.button(self.content, name, lambda n=name: self.open_workflow(n), False).pack(fill='x', pady=4)
        self.label(self.content, 'Recent activity', 28).pack(anchor='w', pady=(20, 0))
        self.write(self.textbox(160), '\n'.join(reversed(logs[-8:])) or 'No activity recorded yet.')

    def open_workflow(self, name):
        self.navigate('Workflows')
        self.choice.set(name)

    def show_workflows(self):
        self.heading('Workflows.', 'Preview first. Proceed with intention.')
        self.choice = ctk.StringVar(value='Organize files')
        self.menu = ctk.CTkOptionMenu(self.content, values=list(WORKFLOWS), variable=self.choice, fg_color=PANEL, button_color=LINE, font=BODY, corner_radius=0)
        self.menu.pack(fill='x', pady=8)
        self.label(self.content, 'Workspace: ' + load_config()['allowed_folder'], font=BODY, color=GRAY).pack(anchor='w', pady=8)
        self.label(self.content, 'Archive age in days', font=BODY).pack(anchor='w')
        self.days = ctk.CTkEntry(self.content, fg_color=PANEL, border_color=LINE, corner_radius=0)
        self.days.insert(0, '30')
        self.days.pack(fill='x', pady=8)
        self.preview_button = self.button(self.content, 'Preview workflow', self.manual_preview)
        self.preview_button.pack(anchor='w', pady=10)
        self.preview_controls()

    def preview_controls(self):
        self.output = self.textbox(280)
        self.write(self.output, 'Select a workflow to preview.')
        self.approve = self.button(self.content, 'Approve and execute', self.execute)
        self.approve.pack(anchor='w', pady=5)
        self.approve.configure(state='disabled')
        self.cancel_button = self.button(self.content, 'Cancel preview', self.cancel, False)
        self.cancel_button.pack(anchor='w', pady=5)
        self.cancel_button.configure(state='disabled')

    def manual_preview(self):
        try:
            workflow = WORKFLOWS[self.choice.get()]
            days = int(self.days.get()) if workflow == 'archive' else 30
            if days < 1:
                raise ValueError('Archive age must be a positive whole number.')
            self.preview(workflow, days)
        except Exception as error:
            messagebox.showerror('Preview failed', str(error), parent=self)

    def preview(self, workflow, days=30, schedule=None):
        if self.pending is not None:
            return
        folder = load_config()['allowed_folder']
        if not Path(folder).is_dir():
            raise ValueError('Configured workspace does not exist.')
        actions = run_workflow(workflow, folder, days)
        if workflow == 'duplicates':
            self.write(self.output, '\n\n'.join(f"Original: {a['original']}\nDuplicate: {a['duplicate']}" for a in actions) or 'No duplicates found.')
            if schedule:
                self.record_schedule(schedule)
            return
        allowed, blocked = [], []
        for action in actions:
            (allowed if is_action_allowed(action, folder) else blocked).append(action)
        warnings = []
        for action in blocked:
            self.audit(action, 'BLOCKED', warnings)
        lines = [f'{len(allowed)} permitted / {len(blocked)} blocked']
        for status, group in [('ALLOWED', allowed), ('BLOCKED', blocked)]:
            lines.extend(f"{status}\n{a['source']}\n  → {a['destination']}" for a in group)
        self.write(self.output, '\n\n'.join(lines + warnings))
        if not allowed:
            if schedule:
                self.record_schedule(schedule)
            return
        self.pending = (allowed, folder, schedule)
        self.approve.configure(state='normal')
        self.cancel_button.configure(state='normal')
        self.preview_button.configure(state='disabled')
        if hasattr(self, 'menu') and self.menu.winfo_exists():
            self.menu.configure(state='disabled')
            self.days.configure(state='disabled')

    def audit(self, action, status, warnings):
        try:
            log_action(action, status)
        except OSError as error:
            warnings.append(f'Audit logging failed: {error}')

    def reset_preview(self):
        self.pending = None
        self.approve.configure(state='disabled')
        self.cancel_button.configure(state='disabled')
        self.preview_button.configure(state='normal')
        if hasattr(self, 'menu') and self.menu.winfo_exists():
            self.menu.configure(state='normal')
            self.days.configure(state='normal')

    def execute(self):
        if self.pending is None:
            return
        actions, folder, schedule = self.pending
        if not messagebox.askyesno('Confirm execution', f'Move {len(actions)} approved file(s)?', parent=self):
            return
        results = []
        count = 0
        try:
            if load_config()['allowed_folder'] != folder:
                raise ValueError('Workspace configuration changed. Generate a new preview.')
            for action in actions:
                capture = StringIO()
                try:
                    with redirect_stdout(capture):
                        count += bool(execute_action(action, folder))
                except Exception as error:
                    results.append(str(error))
                results.append(capture.getvalue())
            if schedule:
                self.record_schedule(schedule)
        except Exception as error:
            results.append(str(error))
        self.reset_preview()
        self.write(self.output, f'{count} of {len(actions)} files moved.\n\n' + '\n'.join(results))

    def cancel(self):
        if self.pending is None:
            return
        actions, folder, schedule = self.pending
        warnings = []
        for action in actions:
            self.audit(action, 'CANCELLED', warnings)
        if schedule:
            try:
                self.record_schedule(schedule)
            except Exception as error:
                warnings.append(str(error))
        self.reset_preview()
        self.write(self.output, 'Cancelled. No files moved.\n' + '\n'.join(warnings))

    def record_schedule(self, schedule):
        history = load_history()
        history[schedule['name']] = current_time()
        save_history(history)

    def show_schedules(self):
        self.heading('Schedules.', 'Make time for what matters.')
        schedules = load_schedules()
        history = load_history()
        due = get_due_schedules(schedules, history)
        for schedule in schedules:
            name = schedule['name']
            last = history.get(name)
            status = 'Disabled' if not schedule['enabled'] else 'Due' if schedule in due else 'Waiting'
            card = self.card()
            self.label(card, name.replace('_', ' ').title(), 25).pack(anchor='w', padx=16, pady=(12, 0))
            self.label(card, f"{status} · Every {schedule['interval_minutes']} minutes", font=BODY, color=GRAY).pack(anchor='w', padx=16)
            self.label(card, 'Last processed: ' + (last.astimezone().strftime('%Y-%m-%d %H:%M') if last else 'Never'), font=MONO, color=GRAY).pack(anchor='w', padx=16, pady=(4, 12))
        self.schedule_choice = ctk.StringVar(value=due[0]['name'] if due else 'No schedules due')
        ctk.CTkOptionMenu(self.content, values=[s['name'] for s in due] or ['No schedules due'], variable=self.schedule_choice, fg_color=PANEL, button_color=LINE, corner_radius=0).pack(fill='x', pady=10)
        self.preview_button = self.button(self.content, 'Preview due schedule', self.schedule_preview)
        self.preview_button.pack(anchor='w')
        if not due:
            self.preview_button.configure(state='disabled')
        self.preview_controls()
        self.button(self.content, 'Refresh schedules', lambda: self.navigate('Schedules'), False).pack(anchor='w', pady=8)

    def schedule_preview(self):
        try:
            due = get_due_schedules(load_schedules(), load_history())
            schedule = next((s for s in due if s['name'] == self.schedule_choice.get()), None)
            if schedule is None:
                raise ValueError('This schedule is no longer due. Refresh schedules.')
            self.preview(schedule['workflow'], schedule.get('days_old', 30), schedule)
        except Exception as error:
            messagebox.showerror('Schedule preview failed', str(error), parent=self)

    def show_activity(self):
        self.heading('Activity.', 'Every action leaves a trace.')
        self.search = ctk.CTkEntry(self.content, placeholder_text='Search paths or activity...', fg_color=PANEL, border_color=LINE, corner_radius=0)
        self.search.pack(fill='x', pady=8)
        self.filter = ctk.StringVar(value='ALL')
        ctk.CTkOptionMenu(self.content, values=['ALL', 'SUCCESS', 'BLOCKED', 'FAILED', 'CANCELLED'], variable=self.filter, command=lambda _: self.refresh_logs(), fg_color=PANEL, button_color=LINE, corner_radius=0).pack(anchor='w', pady=8)
        self.button(self.content, 'Refresh / search', self.refresh_logs).pack(anchor='w', pady=8)
        self.log_box = self.textbox(440)
        self.search.bind('<Return>', lambda _: self.refresh_logs())
        self.refresh_logs()

    def refresh_logs(self):
        try:
            query = self.search.get().lower()
            status = self.filter.get()
            lines = [line for line in reversed(self.logs()) if query in line.lower() and (status == 'ALL' or line.split(' | ', 2)[1:2] == [status])]
            self.write(self.log_box, '\n'.join(lines) or 'No matching activity.')
        except Exception as error:
            self.write(self.log_box, str(error))

    def show_settings(self):
        self.heading('Settings.', 'Boundaries are a form of protection.')
        settings = load_config()
        for name, value in [('Allowed directory', settings['allowed_folder']), ('Allowed extensions', ', '.join(settings['allowed_extensions'])), ('Maximum file size', f"{settings['max_file_size_mb']} MB"), ('File moves', 'Explicit approval required'), ('Scheduling', 'Manual due-workflow checks'), ('Configuration file', 'config/settings.json')]:
            card = self.card()
            self.label(card, name, 24).pack(anchor='w', padx=18, pady=(12, 0))
            self.label(card, value, font=BODY, color=GRAY).pack(anchor='w', padx=18, pady=(4, 12))
        self.button(self.content, 'Reload configuration', lambda: self.navigate('Settings')).pack(anchor='w', pady=12)

    def close(self):
        if self.pending is not None:
            if not messagebox.askyesno('Exit SecureFlow', 'Cancel the pending preview and exit?', parent=self):
                return
            self.cancel()
        self.destroy()


def main():
    os.chdir(Path(__file__).resolve().parents[1])
    ctk.set_appearance_mode('dark')
    app = SecureFlow()
    app.protocol('WM_DELETE_WINDOW', app.close)
    app.mainloop()


if __name__ == '__main__':
    main()
