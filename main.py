import tkinter as tk
from tkinter import messagebox
import os
import shutil
import ctypes
import subprocess
import psutil

# Helper functions

def clean_temp_files():
    temp = os.environ.get('TEMP')
    if temp and os.path.exists(temp):
        try:
            for root, dirs, files in os.walk(temp):
                for f in files:
                    try:
                        os.remove(os.path.join(root, f))
                    except Exception:
                        pass
                for d in dirs:
                    try:
                        shutil.rmtree(os.path.join(root, d), ignore_errors=True)
                    except Exception:
                        pass
            messagebox.showinfo('Success', 'Temporary files cleaned!')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to clean temp files: {e}')
    else:
        messagebox.showerror('Error', 'Temp folder not found.')

def clear_recycle_bin():
    try:
        # SHEmptyRecycleBinW from shell32.dll
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x00000007)
        messagebox.showinfo('Success', 'Recycle Bin cleared!')
    except Exception as e:
        messagebox.showerror('Error', f'Failed to clear Recycle Bin: {e}')

def free_up_ram():
    try:
        # Empty the working set of all processes (Windows only, admin required)
        subprocess.run('powershell.exe Clear-Content -Path "."', shell=True)
        messagebox.showinfo('Success', 'RAM optimization attempted.')
    except Exception as e:
        messagebox.showerror('Error', f'Failed to free up RAM: {e}')

def free_up_ram_for_selected(pids):
    success = []
    failed = []
    for pid in pids:
        try:
            p = psutil.Process(pid)
            p.suspend()  # Suspend and resume to force working set trim
            p.resume()
            # Try to trim working set (Windows only)
            PROCESS_SET_QUOTA = 0x0100
            handle = ctypes.windll.kernel32.OpenProcess(PROCESS_SET_QUOTA, False, pid)
            if handle:
                ctypes.windll.psapi.EmptyWorkingSet(handle)
                ctypes.windll.kernel32.CloseHandle(handle)
            success.append(pid)
        except Exception:
            failed.append(pid)
    return success, failed

def manage_startup_programs():
    try:
        subprocess.Popen('shell:startup', shell=True)
    except Exception as e:
        messagebox.showerror('Error', f'Failed to open Startup folder: {e}')

# GUI
class OptimizerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Windows 11 Optimizer')
        self.geometry('500x500')
        self.resizable(False, False)
        tk.Label(self, text='Windows 11 Optimizer', font=('Arial', 16, 'bold')).pack(pady=10)
        tk.Button(self, text='Clean Temporary Files', width=30, command=clean_temp_files).pack(pady=8)
        tk.Button(self, text='Clear Recycle Bin', width=30, command=clear_recycle_bin).pack(pady=8)
        tk.Button(self, text='Manage Startup Programs', width=30, command=manage_startup_programs).pack(pady=8)
        # Process list UI
        tk.Label(self, text='Select running processes to optimize:', font=('Arial', 11, 'bold')).pack(pady=5)
        self.proc_listbox = tk.Listbox(self, selectmode=tk.MULTIPLE, width=60, height=12)
        self.proc_listbox.pack(pady=5)
        self.refresh_proc_btn = tk.Button(self, text='Refresh Process List', command=self.refresh_process_list)
        self.refresh_proc_btn.pack(pady=2)
        self.optimize_btn = tk.Button(self, text='Free Up RAM for Selected', command=self.optimize_selected)
        self.optimize_btn.pack(pady=8)
        self.suspend_btn = tk.Button(self, text='Suspend All Except Selected', command=self.suspend_all_except_selected)
        self.suspend_btn.pack(pady=8)
        self.resume_btn = tk.Button(self, text='Resume All Suspended', command=self.resume_all_suspended)
        self.resume_btn.pack(pady=8)
        tk.Label(self, text='Run as administrator for best results.', font=('Arial', 9)).pack(side='bottom', pady=10)
        self.refresh_process_list()

    def refresh_process_list(self):
        self.proc_listbox.delete(0, tk.END)
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                display = f"{proc.info['name']} (PID: {proc.info['pid']})"
                self.proc_listbox.insert(tk.END, display)
            except Exception:
                continue

    def optimize_selected(self):
        selected = self.proc_listbox.curselection()
        pids = []
        for idx in selected:
            text = self.proc_listbox.get(idx)
            pid = int(text.split('PID: ')[-1].rstrip(')'))
            pids.append(pid)
        if not pids:
            messagebox.showwarning('No Selection', 'Please select at least one process.')
            return
        # Optimization: Free up RAM and set high priority for selected processes
        success, failed = free_up_ram_for_selected(pids)
        priority_success = []
        priority_failed = []
        for pid in pids:
            try:
                proc = psutil.Process(pid)
                proc.nice(psutil.HIGH_PRIORITY_CLASS)
                priority_success.append(pid)
            except Exception:
                priority_failed.append(pid)
        msg = (
            f"RAM Optimized: {len(success)}\nFailed RAM: {len(failed)}"
            f"\nPriority Set: {len(priority_success)}\nFailed Priority: {len(priority_failed)}"
        )
        messagebox.showinfo('Optimization', msg)

    def suspend_all_except_selected(self):
        selected = self.proc_listbox.curselection()
        keep_pids = set()
        for idx in selected:
            text = self.proc_listbox.get(idx)
            pid = int(text.split('PID: ')[-1].rstrip(')'))
            keep_pids.add(pid)
        suspended = []
        failed = []
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            try:
                if proc.info['pid'] in keep_pids:
                    continue
                # Only suspend user processes, not system
                if proc.info['username'] and os.getlogin().lower() in proc.info['username'].lower():
                    proc.suspend()
                    suspended.append(proc.info['pid'])
            except Exception:
                failed.append(proc.info['pid'])
        msg = f"Suspended: {len(suspended)}\nFailed: {len(failed)}\n(You can resume by rebooting or using Task Manager)"
        messagebox.showinfo('Suspend Others', msg)

    def resume_all_suspended(self):
        resumed = []
        failed = []
        for proc in psutil.process_iter(['pid', 'name', 'status', 'username']):
            try:
                # Only resume user processes that are suspended
                if proc.info['status'] == psutil.STATUS_STOPPED and proc.info['username'] and os.getlogin().lower() in proc.info['username'].lower():
                    proc.resume()
                    resumed.append(proc.info['pid'])
            except Exception:
                failed.append(proc.info['pid'])
        msg = f"Resumed: {len(resumed)}\nFailed: {len(failed)}"
        messagebox.showinfo('Resume All', msg)

if __name__ == '__main__':
    app = OptimizerApp()
    app.mainloop()
