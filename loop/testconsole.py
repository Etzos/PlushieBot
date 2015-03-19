import tkinter as tk
from writer import read_log, write_log, full_message


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid(sticky="nsew")
        self.createWidgets()
        # Set Window info
        w = self.winfo_toplevel()
        w.title("PlushieBot Loopback Server")
        # Set check loop
        self.after(500, self._get_log)

    def createWidgets(self):
        self.log_container = tk.Frame(self,
                                      bd=2,
                                      relief=tk.SUNKEN)
        self.log_container.grid(column=0,
                                row=0,
                                columnspan=2,
                                sticky="wsew")

        self.log_scroll = tk.Scrollbar(self.log_container)
        self.log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.log = tk.Text(self.log_container,
                           relief=tk.FLAT,
                           yscrollcommand=self.log_scroll.set,
                           width=120,
                           height=35)
        self.log.insert(tk.INSERT, "Welcome to the PlushieBot test console.\nThis needs to be run in tandem "
                        "with the PlushieBot console in order to work properly.\nNOTE: The first field is "
                        "the username (prepend the word 'from' in order to make a whisper),\nthe second the "
                        "message itself. The time used should be your current system time.\n\n")
        self.log["state"] = tk.DISABLED
        self.log.pack()

        self.log_scroll["command"] = self.log.yview

        self.name_entry = tk.Entry(self,
                                   width=8)
        self.name_entry.grid(column=0,
                             row=1,
                             sticky="nsew")

        self.entry = tk.Entry(self,
                              width=30)
        self.entry.grid(column=1,
                        row=1,
                        sticky="nswe")
        self.entry.bind("<Return>", self._send_msg)

    def insert_log(self, text, forcedown=True):
        self.log["state"] = tk.NORMAL
        self.log.insert(tk.END, text)
        if forcedown:
            self.log.yview(tk.MOVETO, 1.0)
        self.log["state"] = tk.DISABLED

    def _send_msg(self, event):
        text = self.entry.get()
        if not text:
            return
        name = self.name_entry.get()
        if not name:
            name = "Guest"
        msg = full_message(name, text, False)
        write_log("input.log", [msg])
        self.entry.delete(0, tk.END)

    def _get_log(self):
        r = read_log("output.log", True)
        msgs = "\n".join(map(lambda x: x.replace("&gt;", ">").strip("\n"), r))
        if msgs:
            self.insert_log(msgs + "\n", True)
        self.after(500, self._get_log)

root = tk.Tk()
app = Application(master=root)
app.mainloop()
