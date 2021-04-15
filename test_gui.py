import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import sys

fd = ""


def on_closing():
    sys.exit("GUI Closed")


class Application(tk.Frame):
    def __init__(self, master=None, file_error=False):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.center_window()
        self.master.title("AAFree Smart Translator")
        self.master.protocol("WM_DELETE_WINDOW", on_closing)
        if file_error:
            messagebox.showwarning("Warning", "Can not find chat logs, please select your ChatLogs Directory!")

    def center_window(self):
        master = self.master
        windowWidth = master.winfo_reqwidth()
        windowHeight = master.winfo_reqheight()
        positionRight = int(master.winfo_screenwidth() / 2 - windowWidth / 2)
        positionDown = int(master.winfo_screenheight() / 2 - windowHeight / 2)
        master.geometry("+{}+{}".format(positionRight, positionDown))

    def create_widgets(self):
        self.instructions = tk.Label(self, font='Helvetica 10')
        self.instructions["text"] = "Please select your chat log directory"
        self.instructions.pack(side='top', pady=7)

        self.instructions2 = tk.Label(self, font='Helvetica 12 bold')
        self.instructions2["text"] = "Documents -> AAFreeTo -> ChatLogs"
        self.instructions2.pack(side='top', padx=7)

        self.select_button = tk.Button(self)
        self.select_button["text"] = "Select Folder"
        self.select_button["command"] = lambda: [self.getDir(), self.master.destroy()]
        # self.select_button["command"] = self.getDir
        self.select_button.pack(side="top", pady=5)

        self.quit = tk.Button(self, text="Quit", fg="red",
                              command=on_closing)
        self.quit.pack(side="bottom", pady=5)

    def getDir(self):
        global fd
        fd = filedialog.askdirectory()
        fd = fd.replace("/", "\\") + "\\\\"
