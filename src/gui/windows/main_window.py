import tkinter as tk
import tkinter.filedialog as fd
import gui.widgets
import event
import webbrowser
import os


class MainWindow:
    def __init__(self, parent_view, tk_root):
        self.parent_view = parent_view
        self.tk_root = tk_root

        tk_root.title('HexSheets')
        tk_root.geometry('800x600')

        menu_bar = tk.Menu(tk_root)
        tk_root.configure(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New...", command=self._new_file)
        file_menu.add_command(label="Open...", command=self._open_file)
        file_menu.add_command(label="Save...", command=self._save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=tk_root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        menu_bar.add_command(label='Help', command=self._help)

        tk_root.rowconfigure(0, weight=1)
        tk_root.columnconfigure(0, weight=1)
        mainframe = tk.Frame(tk_root)
        mainframe.grid(sticky='nsew')
        mainframe.rowconfigure(1, weight=1)
        mainframe.columnconfigure(0, weight=1)

        top_bar = tk.Frame(mainframe)
        top_bar.grid(column=0, row=0, sticky='nsew')
        top_bar.columnconfigure(0, weight=1)

        # TODO: Add buttons on the tool bar
        '''
        tool_bar = tk.Frame(top_bar)
        tk.Button(tool_bar, text='Test').pack(side=tk.LEFT)
        tool_bar.grid(column=0, row=0, sticky='we')
        '''

        formula_bar = tk.Frame(top_bar)
        formula_bar.grid(column=0, row=1, sticky='we')
        tk.Label(formula_bar, text='Formula:').pack(side=tk.LEFT)

        self.formula_box = tk.Entry(formula_bar)
        self.formula_box.pack(fill=tk.X)
        self.parent_view.add_observer('formula_box', self.update_formula_box)

        self.spreadsheet = gui.widgets.HexCells(mainframe, hex_rows=20, hex_columns=20, select_command=self.select_cell)
        self.spreadsheet.grid(column=0, row=1, sticky='nsew')
        self.parent_view.add_observer('cell_values', self.spreadsheet.set_cell_values)

        self._formula_boxes = [
            self.formula_box,
            self.spreadsheet.hidden_entry
        ]
        vcmd = (self.tk_root.register(self._enter_formula), '%W', '%P')
        for box in self._formula_boxes:
            box.config(vcmd=vcmd)
            box.bind("<FocusIn>", lambda e: e.widget.config(validate='key'))
            box.bind("<FocusOut>", lambda e: e.widget.config(validate='none'))

        self.status_bar = tk.Label(mainframe, relief=tk.GROOVE, anchor=tk.W)
        self.status_bar.grid(column=0, row=2, sticky=(tk.W, tk.E))
        self.parent_view.add_observer('status_bar', self.update_status_bar)

    def update_status_bar(self, text):
        self.status_bar.config(text=text)

    def _enter_formula(self, widget, new_text):
        for box in self._formula_boxes:
            if box != self.tk_root.nametowidget(widget):
                box.delete(0, tk.END)
                box.insert(0, new_text)
        self.parent_view.add_event(event.Event('FormulaChanged', {'formula': new_text}))

        return True

    def update_formula_box(self, text):
        for box in self._formula_boxes:
            validation = box.cget('validate')
            box.config(validate='none')
            box.delete(0, tk.END)
            box.insert(0, text)
            box.config(validate=validation)

    def select_cell(self, address):
        self.parent_view.add_event(event.Event('CellSelected', {'address': address}))

    def _new_file(self):
        self.parent_view.add_event(event.Event('NewFile'))

    def _open_file(self):
        open_file_name = fd.askopenfilename(filetypes=(('HexSheets', '*.hxs'),
                                                       ('All Files', '*.*')))
        self.parent_view.add_event(event.Event('OpenFile', {'filename': open_file_name}))

    def _save_file(self):
        save_file_name = fd.asksaveasfilename(defaultextension='hxs',
                                              filetypes=(('HexSheets', '*.hxs'),
                                                         ('All Files', '*.*')))
        self.parent_view.add_event(event.Event('SaveFile', {'filename': save_file_name}))

    def _help(self):
        webbrowser.open_new(os.getcwd() + '/docs/index.html')
