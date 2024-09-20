import tkinter as tk
from tkinter import Text, ttk, colorchooser, messagebox
import subprocess
import sys
import io
import os
import platform
import socket
from datetime import datetime, timedelta
import uuid

def get_system_info():
    try:
        # Get CPU usage
        cpu_usage = float(subprocess.check_output("wmic cpu get loadpercentage").decode().strip().split('\n')[1])
        
        # Get RAM usage
        free_memory_kb = float(subprocess.check_output("wmic os get freephysicalmemory").decode().strip().split('\n')[1])
        total_memory_bytes = float(subprocess.check_output("wmic computersystem get totalphysicalmemory").decode().strip().split('\n')[1])
        
        # Convert KB to Bytes for free_memory
        free_memory_bytes = free_memory_kb * 1024
        
        # Calculate RAM usage percentage
        ram_usage = 100 * (1 - (free_memory_bytes / total_memory_bytes))
        
        # Get OS information
        os_info = platform.system() + " " + platform.release()
        
        # Get boot time
        boot_time_str = subprocess.check_output("wmic os get lastbootuptime").decode().strip().split('\n')[1]
        
        # Remove timezone offset part: '+120' from the string
        boot_time_str = boot_time_str[:-4]  # Assuming offset part is always last 4 characters including '+'
        
        # Parse datetime
        boot_time = datetime.strptime(boot_time_str, "%Y%m%d%H%M%S.%f")
        
        # Optionally adjust for timezone offset if needed (can be removed if not necessary)
        timezone_offset = timedelta(minutes=120)
        boot_time -= timezone_offset
        
        current_time = datetime.now()
        uptime = str(current_time - boot_time)
        system_time = current_time.strftime("%H:%M:%S")
        system_date = current_time.strftime("%Y-%m-%d")
        
        return cpu_usage, ram_usage, os_info, uptime, system_time, system_date
    
    except Exception as e:
        print(f"Error retrieving system information: {e}")
        return None

# Call the function and print results
result = get_system_info()
if result:
    cpu_usage, ram_usage, os_info, uptime, system_time, system_date = result
    version = f'''
      ______ __  __    _____ _          _ _ 
     |  ____|  \/  |  / ____| |        | | |
     | |__  | \  / | | (___ | |__   ___| | |
     |  __| | |\/| |  \___ \| '_ \ / _ \ | |
     | |    | |  | |  ____) | | | |  __/ | |
     |_|    |_|  |_| |_____/|_| |_|\___|_|_|
                                        
        | > Version: 1.1
        | > CPU Usage: {cpu_usage}%
        | > RAM Usage: {ram_usage:.2f}%
        | > OS: {os_info}
        | > Uptime: {uptime}
        | > Time: {system_time}
        | > Date: {system_date}
    '''
else:
    version = 'Error'

settings_file = r"C:\FMShell\settings\color.sett"

class PythonShell(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("FMShell")
    
        # Load settings
        self.terminal_color = self.load_color()
        self.text_color = self.load_text_color()
        width, height = self.load_window_size()
        self.geometry(f"{width}x{height}")

        self.configure(bg="#2E2E2E")
        self.attributes('-alpha', 0.90)
        self.attributes('-topmost', True)

        self.create_title_bar()
        self.notebook = ttk.Notebook(self, style='TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.tab_count = {"python": 0, "batch": 0, "fmshell": 0}
        self.create_tab("Python", "python")
        self.manage_frame = tk.Frame(self, bg="#1E1E1E")
        self.manage_frame.pack(fill=tk.X, padx=5, pady=5)
        self.add_tab_button = tk.Button(self.manage_frame, text="Add Python Tab", command=lambda: self.add_tab("python"), bg="#1E1E1E", fg="#00FF00", font=("Arial", 12), borderwidth=0)
        self.add_tab_button.pack(side=tk.LEFT, padx=5)
        self.add_batch_tab_button = tk.Button(self.manage_frame, text="Add Batch Tab", command=lambda: self.add_tab("batch"), bg="#1E1E1E", fg="#00FF00", font=("Arial", 12), borderwidth=0)
        self.add_batch_tab_button.pack(side=tk.LEFT, padx=5)
        self.add_fmshell_tab_button = tk.Button(self.manage_frame, text="Add FMShell Tab", command=lambda: self.add_tab("fmshell"), bg="#1E1E1E", fg="#00FF00", font=("Arial", 12), borderwidth=0)
        self.add_fmshell_tab_button.pack(side=tk.LEFT, padx=5)
        self.remove_tab_button = tk.Button(self.manage_frame, text="Remove Tab", command=self.remove_tab, bg="#1E1E1E", fg="#FF0000", font=("Arial", 12), borderwidth=0)
        self.remove_tab_button.pack(side=tk.LEFT, padx=5)
        self._offsetx = 0
        self._offsety = 0
        self.title_bar.bind('<Button-1>', self.start_move)
        self.title_bar.bind('<B1-Motion>', self.move_window)
        self.global_namespace = {}

    def create_title_bar(self):
        self.title_bar = tk.Frame(self, bg="#1E1E1E", relief='raised', bd=0)
        self.title_bar.pack(fill=tk.X)

        self.title_label = tk.Label(self.title_bar, text="FMShell", bg="#1E1E1E", fg="#FFFFFF", font=("Courier", 12))
        self.title_label.pack(side=tk.LEFT, padx=10)

        self.minimize_button = tk.Button(self.title_bar, text='➖', bg="#1E1E1E", fg="#FFFFFF", command=self.minimize, borderwidth=0, font=("Arial", 12))
        self.minimize_button.pack(side=tk.RIGHT, padx=5)

        self.maximize_button = tk.Button(self.title_bar, text='🔲', bg="#1E1E1E", fg="#00FF00", command=self.toggle_fullscreen, borderwidth=0, font=("Arial", 12))
        self.maximize_button.pack(side=tk.RIGHT, padx=5)

        self.settings_button = tk.Button(self.title_bar, text='⚙', bg="#1E1E1E", fg="#00FF00", command=self.open_settings, borderwidth=0, font=("Arial", 12))
        self.settings_button.pack(side=tk.RIGHT, padx=5)

        self.close_button = tk.Button(self.title_bar, text='✖', bg="#1E1E1E", fg="#FF0000", command=self.on_close, borderwidth=0, font=("Arial", 12))
        self.close_button.pack(side=tk.RIGHT, padx=5)

    def create_tab(self, language, mode):
        self.tab_count[mode] += 1
        tab_name = f"{language} - Tab {self.tab_count[mode]}"
        
        tab_frame = tk.Frame(self.notebook, bg=self.terminal_color)
        self.notebook.add(tab_frame, text=tab_name)

        output_area = Text(
            tab_frame,
            wrap=tk.WORD,
            font=("Courier", 12),
            bg=self.terminal_color,
            fg="#00FF00",
            insertbackground="#00FF00",
            selectbackground="#6A6A6A",
            selectforeground="#00FF00",
            borderwidth=0,
            highlightthickness=0
        )
        output_area.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        output_area.config(state=tk.DISABLED)

        input_frame = tk.Frame(tab_frame, bg=self.terminal_color)
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        prompt_label = tk.Label(
            input_frame,
            text="$~",
            font=("Courier", 12),
            fg="#00FF00",
            bg=self.terminal_color
        )
        prompt_label.pack(side=tk.LEFT, padx=(5, 0))

        entry = tk.Entry(
            input_frame,
            font=("Courier", 12),
            bg=self.terminal_color,
            fg="#FFFFFF",
            insertbackground="#00FF00",
            borderwidth=0,
            highlightthickness=0
        )
        entry.pack(fill=tk.X, padx=(5, 0), pady=5, side=tk.LEFT, expand=True)
        entry.bind("<Return>", lambda e, ea=entry, oa=output_area, m=mode: self.execute_command(ea, oa, m))

    def add_tab(self, mode):
        if mode == "python":
            self.create_tab("Python", "python")
        elif mode == "batch":
            self.create_tab("Batch", "batch")
        elif mode == "fmshell":
            self.create_tab("FMShell", "fmshell")

    def remove_tab(self):
        if len(self.notebook.tabs()) > 1:
            current_tab = self.notebook.select()
            self.notebook.forget(current_tab)

    def start_move(self, event):
        self._offsetx = event.x
        self._offsety = event.y

    def move_window(self, event):
        x = self.winfo_pointerx() - self._offsetx
        y = self.winfo_pointery() - self._offsety
        self.geometry(f'+{x}+{y}')

    def toggle_fullscreen(self):
        if not self.attributes('-fullscreen'):
            self.attributes('-fullscreen', True)
            self.maximize_button.config(text='🔲')
        else:
            self.attributes('-fullscreen', False)
            self.geometry('1000x600')
            self.maximize_button.config(text='🔲')

    def minimize(self):
        self.iconify()

    def on_close(self):
        self.destroy()

    def execute_command(self, entry, output_area, mode):
        command = entry.get().strip()
        entry.delete(0, tk.END)

        self.display_output(output_area, f"$~ {command}\n")

        try:
            if mode == "batch":
                result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
                output = result.stdout + result.stderr
                self.display_output(output_area, output)
            elif mode == "python":
                stdout = sys.stdout
                stderr = sys.stderr
                sys.stdout = io.StringIO()
                sys.stderr = io.StringIO()

                try:
                    exec(command, self.global_namespace)
                except Exception as e:
                    self.display_output(output_area, f"Error: {e}\n", 'error')
                finally:
                    output = sys.stdout.getvalue()
                    error_output = sys.stderr.getvalue()
                    self.display_output(output_area, output)
                    self.display_output(output_area, error_output)

                    sys.stdout = stdout
                    sys.stderr = stderr
            elif mode == "fmshell":
                self.execute_fmshell_command(command, output_area)
        except Exception as e:
            self.display_output(output_area, f"Execution Error: {e}\n", 'error')

    def execute_fmshell_command(self, command, output_area):
        if command == "help":
            self.display_output(output_area, "Available commands: help, ver, configureip, sysname, tasks, myname, uptime, kill, shutdown, reboot, rmdir, mkdir, ls, cd, rm, mv, chmod, echo, say, filewrite, unzip, chown, zip, nslookup, netstat, ping, curl, wget, viewfile, dir, clear, cpuusage, ramusage, rmfileline, copyfileline\n")
        
        elif command == "configureip":
            if platform.system() == "Windows":
                result = subprocess.check_output("ipconfig", shell=True).decode()
            else:
                result = subprocess.check_output("ifconfig", shell=True).decode()
            self.display_output(output_area, result)

        elif command == "sysname":
            info = [
                f"System Name: {platform.node()}",
                f"Kernel: {platform.version()}",
                f"Main Drive: {os.path.splitdrive(os.getcwd())[0]}",
                f"IPConfig:\n{self.get_ipconfig()}",
                f"Windows Version: {platform.version()}",
                f"Username: {os.getlogin()}",
                f"MAC Address: {self.get_mac_address()}",
                f"Public IP Address: {self.get_public_ip()}",
                f"Internet Connection: {'Connected' if self.is_internet_available() else 'Disconnected'}",
                f"Account Type: {self.get_account_type()}",
                f"RAM: {psutil.virtual_memory().total / (1024 ** 3):.2f} GB",
                f"CPU: {psutil.cpu_count(logical=True)} cores",
                f"Motherboard: {self.get_motherboard_info()}"
            ]
            self.display_output(output_area, "\n".join(info) + "\n")

        elif command == "tasks":
            tasks = subprocess.check_output("tasklist", shell=True).decode()
            self.display_output(output_area, tasks)

        elif command == "myname":
            self.display_output(output_area, "FMShell User\n")

        elif command == "uptime":
            uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
            self.display_output(output_area, f"Uptime: {uptime}\n")

        elif command.startswith("kill "):
            pid = command.split(" ")[1]
            try:
                subprocess.run(f"taskkill /PID {pid} /F", shell=True, check=True)
                self.display_output(output_area, f"Process {pid} terminated.\n")
            except subprocess.CalledProcessError:
                self.display_output(output_area, f"Error: Unable to terminate process {pid}.\n")

        elif command == "shutdown":
            subprocess.run("shutdown /s /t 0", shell=True)

        elif command == "reboot":
            subprocess.run("shutdown /r /t 0", shell=True)

        elif command.startswith("rmdir "):
            path = command.split(" ")[1]
            try:
                os.rmdir(path)
                self.display_output(output_area, f"Removed directory: {path}\n")
            except OSError as e:
                self.display_output(output_area, f"Error: {e}\n")

        elif command.startswith("mkdir "):
            path = command.split(" ")[1]
            try:
                os.makedirs(path)
                self.display_output(output_area, f"Created directory: {path}\n")
            except OSError as e:
                self.display_output(output_area, f"Error: {e}\n")

        elif command.startswith("ls") or command.startswith("dir"):
            path = command.split(" ")[1] if len(command.split(" ")) > 1 else "."
            try:
                result = subprocess.check_output(f"dir {path}" if platform.system() == "Windows" else f"ls {path}", shell=True).decode()
                self.display_output(output_area, result)
            except subprocess.CalledProcessError as e:
                self.display_output(output_area, f"Error: {e}\n")

        elif command.startswith("cd "):
            path = command.split(" ")[1]
            try:
                os.chdir(path)
                self.display_output(output_area, f"Changed directory to: {os.getcwd()}\n")
            except OSError as e:
                self.display_output(output_area, f"Error: {e}\n")

        elif command.startswith("rm "):
            path = command.split(" ")[1]
            try:
                os.remove(path)
                self.display_output(output_area, f"Removed file: {path}\n")
            except OSError as e:
                self.display_output(output_area, f"Error: {e}\n")

        elif command.startswith("mv "):
            src, dst = command.split(" ")[1:3]
            try:
                os.rename(src, dst)
                self.display_output(output_area, f"Moved file from {src} to {dst}\n")
            except OSError as e:
                self.display_output(output_area, f"Error: {e}\n")

        elif command.startswith("chmod "):
            mode, path = command.split(" ")[1:3]
            try:
                os.chmod(path, int(mode, 8))
                self.display_output(output_area, f"Changed mode of {path} to {mode}\n")
            except OSError as e:
                self.display_output(output_area, f"Error: {e}\n")

        elif command.startswith("echo "):
            text = command.split(" ", 1)[1]
            self.display_output(output_area, f"{text}\n")
        
        elif command.startswith("ver"):
            self.display_output(output_area, f"{version}\n")

        elif command.startswith("say "):
            text = command.split(" ", 1)[1]
            self.display_output(output_area, f"Say: {text}\n")

        elif command.startswith("filewrite "):
            path, text = command.split(" ")[1:3]
            with open(path, "a") as file:
                file.write(text + "\n")
            self.display_output(output_area, f"Added text to file: {path}\n")

        elif command.startswith("unzip "):
            path = command.split(" ")[1]
            try:
                subprocess.run(f"unzip {path}", shell=True, check=True)
                self.display_output(output_area, f"Unzipped file: {path}\n")
            except subprocess.CalledProcessError as e:
                self.display_output(output_area, f"Error: {e}\n")

        elif command.startswith("chown "):
            user, path = command.split(" ")[1:3]
            try:
                subprocess.run(f"chown {user} {path}", shell=True, check=True)
                self.display_output(output_area, f"Changed owner of {path} to {user}\n")
            except subprocess.CalledProcessError as e:
                self.display_output(output_area, f"Error: {e}\n")

        elif command.startswith("zip "):
            path = command.split(" ")[1]
            try:
                subprocess.run(f"zip {path}", shell=True, check=True)
                self.display_output(output_area, f"Zipped file: {path}\n")
            except subprocess.CalledProcessError as e:
                self.display_output(output_area, f"Error: {e}\n")

        elif command.startswith("nslookup "):
            domain = command.split(" ")[1]
            result = subprocess.check_output(f"nslookup {domain}", shell=True).decode()
            self.display_output(output_area, result)

        elif command.startswith("netstat"):
            result = subprocess.check_output("netstat", shell=True).decode()
            self.display_output(output_area, result)

        elif command.startswith("ping "):
            host = command.split(" ")[1]
            result = subprocess.check_output(f"ping {host}", shell=True).decode()
            self.display_output(output_area, result)

        elif command.startswith("curl "):
            url = command.split(" ")[1]
            result = subprocess.check_output(f"curl {url}", shell=True).decode()
            self.display_output(output_area, result)

        elif command.startswith("wget "):
            url = command.split(" ")[1]
            result = subprocess.check_output(f"wget {url}", shell=True).decode()
            self.display_output(output_area, result)

        elif command.startswith("viewfile "):
            path = command.split(" ")[1]
            try:
                with open(path, "r") as file:
                    content = file.read()
                self.display_output(output_area, content)
            except FileNotFoundError as e:
                self.display_output(output_area, f"Error: {e}\n")

        elif command.startswith("clear"):
            output_area.config(state=tk.NORMAL)
            output_area.delete(1.0, tk.END)
            output_area.config(state=tk.DISABLED)

        elif command.startswith("cpuusage"):
            cpu_usage = psutil.cpu_percent(interval=1)
            self.display_output(output_area, f"CPU Usage: {cpu_usage}%\n")

        elif command.startswith("ramusage"):
            ram_usage = psutil.virtual_memory().percent
            self.display_output(output_area, f"RAM Usage: {ram_usage}%\n")

        elif command.startswith("rmfileline "):
            path, line_number = command.split(" ")[1:3]
            line_number = int(line_number)
            with open(path, "r") as file:
                lines = file.readlines()
            if 0 < line_number <= len(lines):
                with open(path, "w") as file:
                    file.writelines(line for i, line in enumerate(lines) if i != line_number - 1)
                self.display_output(output_area, f"Removed line {line_number} from {path}\n")
            else:
                self.display_output(output_area, f"Error: Line number out of range\n")

        elif command.startswith("copyfileline "):
            path, line_number = command.split(" ")[1:3]
            line_number = int(line_number)
            with open(path, "r") as file:
                lines = file.readlines()
            if 0 < line_number <= len(lines):
                self.display_output(output_area, lines[line_number - 1])
            else:
                self.display_output(output_area, f"Error: Line number out of range\n")

        else:
            self.display_output(output_area, "Command not recognized\n", 'error')

    def display_output(self, output_area, text, style='normal'):
        # Append output text to the output area
        output_area.config(state=tk.NORMAL)
        output_area.insert(tk.END, text)
        output_area.config(state=tk.DISABLED)
        output_area.yview(tk.END)

    def get_ipconfig(self):
        try:
            if platform.system() == "Windows":
                result = subprocess.check_output("ipconfig", shell=True).decode()
            else:
                result = subprocess.check_output("ifconfig", shell=True).decode()
            return result
        except subprocess.CalledProcessError as e:
            return f"Error: {e}"

    def get_mac_address(self):
        try:
            return ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2 * 6, 2)][::-1])
        except Exception as e:
            return f"Error: {e}"

    def get_public_ip(self):
        try:
            return subprocess.check_output("curl ifconfig.me", shell=True).decode().strip()
        except subprocess.CalledProcessError as e:
            return f"Error: {e}"

    def is_internet_available(self):
        try:
            socket.create_connection(("www.google.com", 80))
            return True
        except OSError:
            return False

    def get_account_type(self):
        try:
            if platform.system() == "Windows":
                import win32api
                user = win32api.GetUserName()
                if user == "Administrator":
                    return "Administrator"
                else:
                    return "User"
            else:
                return "User"
        except ImportError:
            return "Unknown"

    def get_motherboard_info(self):
        try:
            if platform.system() == "Windows":
                import wmi
                c = wmi.WMI()
                for board in c.Win32_BaseBoard():
                    return board.Product
            elif platform.system() == "Linux":
                return subprocess.check_output("dmidecode -t 2", shell=True).decode()
            else:
                return "Unknown"
        except Exception as e:
            return f"Error: {e}"
      
    def append_output(self, output_area, output):
        output_area.config(state=tk.NORMAL)
        output_area.insert(tk.END, output + '\n')
        output_area.config(state=tk.DISABLED)
        output_area.yview(tk.END)

    def open_settings(self):
        settings_window = tk.Toplevel(self)
        settings_window.title("Settings")
        settings_window.geometry("400x400")

        tk.Label(settings_window, text="Select Terminal Color:", font=("Courier", 12)).pack(pady=5)
        tk.Button(settings_window, text="Choose Terminal Color", command=self.choose_color).pack(pady=5)
        tk.Button(settings_window, text="Reset Terminal Color", command=self.reset_color).pack(pady=5)

        tk.Label(settings_window, text="Select Text Color:", font=("Courier", 12)).pack(pady=5)
        tk.Button(settings_window, text="Choose Text Color", command=self.choose_text_color).pack(pady=5)
        tk.Button(settings_window, text="Reset Text Color", command=self.reset_text_color).pack(pady=5)

        tk.Label(settings_window, text="Set Window Size:", font=("Courier", 12)).pack(pady=5)
        tk.Button(settings_window, text="Set Window Size", command=self.choose_window_size).pack(pady=5)
        tk.Button(settings_window, text="Reset Window Size", command=self.reset_window_size).pack(pady=5)

    def choose_color(self):
        color_code = colorchooser.askcolor(title="Choose Terminal Color")[1]
        if color_code:
            self.terminal_color = color_code
            self.save_color(color_code)
            self.update_colors()
            
    def reset_color(self):
        color_file = r"C:\FMShell\settings\color.sett"
        if os.path.exists(color_file):
            os.remove(color_file)
            tk.messagebox.showinfo("Color Reset", "Terminal color has been reset to default.")
        else:
            tk.messagebox.showinfo("Color Reset", "No custom color settings found to reset.")

    def reset_text_color(self):
        text_color_file = r"C:\FMShell\settings\textcol.sett"
        if os.path.exists(text_color_file):
            os.remove(text_color_file)
            tk.messagebox.showinfo("Text Color Reset", "Text color has been reset to default.")
        else:
            tk.messagebox.showinfo("Text Color Reset", "No custom text color settings found to reset.")
            
    def reset_window_size(self):
        window_size_file = r"C:\FMShell\settings\winsize.sett"
        if os.path.exists(window_size_file):
            os.remove(window_size_file)
            tk.messagebox.showinfo("Window Size Reset", "Window Size has been reset to default.")
        else:
            tk.messagebox.showinfo("Window Size Reset", "No custom Window Size settings found to reset.")

    def load_color(self):
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as file:
                return file.read().strip()
        else:
            return "#2E2E2E"

    def save_color(self, color):
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        with open(settings_file, 'w') as file:
            file.write(color)

    def update_colors(self):
        style = ttk.Style()
        style.configure('TNotebook', background=self.terminal_color, borderwidth=0)
        style.configure('TNotebook.Tab', background=self.terminal_color, foreground=self.text_color, font=("Courier", 12))
        style.map('TNotebook.Tab', background=[('selected', '#1E1E1E')], foreground=[('selected', '#00FF00')])

        for tab in self.notebook.tabs():
            tab_frame = self.nametowidget(tab)
            for widget in tab_frame.winfo_children():
                if isinstance(widget, Text):
                    widget.config(bg=self.terminal_color, fg=self.text_color)
                elif isinstance(widget, tk.Entry):
                    widget.config(bg=self.terminal_color, fg=self.text_color)
                elif isinstance(widget, tk.Label):
                    widget.config(bg=self.terminal_color, fg=self.text_color)
            tab_frame.config(bg=self.terminal_color)

    def choose_text_color(self):
        color_code = colorchooser.askcolor(title="Choose Text Color")[1]
        if color_code:
            self.text_color = color_code
            self.save_text_color(color_code)
            self.update_colors()

    def save_text_color(self, color):
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        with open(r"C:\FMShell\settings\textcol.sett", 'w') as file:
            file.write(color)
            
    def choose_window_size(self):
        size_window = tk.Toplevel(self)
        size_window.title("Window Size")

        tk.Label(size_window, text="Enter Width:").pack(pady=5)
        width_entry = tk.Entry(size_window)
        width_entry.pack(pady=5)

        tk.Label(size_window, text="Enter Height:").pack(pady=5)
        height_entry = tk.Entry(size_window)
        height_entry.pack(pady=5)

        tk.Button(size_window, text="Apply", command=lambda: self.apply_window_size(width_entry.get(), height_entry.get())).pack(pady=10)

    def apply_window_size(self, width_str, height_str):
        try:
            width = int(width_str)
            height = int(height_str)
            self.save_window_size(width, height)
            self.geometry(f"{width}x{height}")
        except ValueError:
            tk.messagebox.showerror("Invalid Input", "Please enter valid integers for width and height.")

    def save_window_size(self, width, height):
        os.makedirs(os.path.dirname(r"C:\FMShell\settings"), exist_ok=True)
        with open(r"C:\FMShell\settings\winsize.sett", 'w') as file:
            file.write(f"{width}x{height}")

    def load_window_size(self):
        try:
            with open(r"C:\FMShell\settings\winsize.sett", 'r') as file:
                size = file.read().strip()
                width, height = map(int, size.split('x'))
                return width, height
        except:
            return 1000, 600

    def apply_settings(self):
        width, height = self.load_window_size()
        self.geometry(f"{width}x{height}")
    
    def load_text_color(self):
        try:
            with open(r"C:\FMShell\settings\textcol.sett", 'r') as file:
                return file.read().strip()
        except FileNotFoundError:
            return "#FFFFFF"


if __name__ == "__main__":
    app = PythonShell()
    app.mainloop()
