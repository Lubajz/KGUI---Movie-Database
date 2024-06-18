from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, ttk
from tkcalendar import DateEntry
from pathlib import Path
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from abc import ABC, abstractmethod
import re
from database import MovieDatabase


def relative_to_assets(filename) -> Path:
    current_dir = Path(__file__).parent.resolve() 
    rel_path = os.path.join(current_dir, "assets\\" + filename) 
    return rel_path

class BaseWidget:
    def __init__(self, canvas):
        self.canvas = canvas

    def create_text(self, x, y, text, font_size=12, fill="#FFFFFF"):
        self.canvas.create_text(
            x, y,
            anchor="nw",
            text=text,
            fill=fill,
            font=("LexendDeca Regular", font_size * -1)
        )

    def create_rectangle(self, x1, y1, x2, y2, fill="#FFFFFF", outline=""):
        self.canvas.create_rectangle(
            x1, y1,
            x2, y2,
            fill=fill,
            outline=outline
        )

class EntryWidget(BaseWidget):
    def __init__(self, canvas, x, y, width, height, bg_image, image_x, image_y, bg="#D9D9D9"):
        super().__init__(canvas)
        self.image = PhotoImage(file=relative_to_assets(bg_image))
        self.canvas.create_image(image_x, image_y, image=self.image)
        self.entry = Entry(
            bd=0,
            bg=bg,
            fg="#000716",
            highlightthickness=0
        )
        self.entry.place(
            x=x,
            y=y,
            width=width,
            height=height
        )

class DateEntryWidget(BaseWidget):
    def __init__(self, canvas, x, y, width, height, bg_image, image_x, image_y):
        super().__init__(canvas)
        style = ttk.Style()
        style.configure('my.DateEntry', relief='flat')

        self.entry = DateEntry(
            bd=0,
            style='my.DateEntry',
            date_pattern='y-mm-dd'
        )
        self.entry.place(
            x=x,
            y=y,
            width=width,
            height=height
        )

class TreeviewWidget(BaseWidget):
    def __init__(self, canvas, x, y, width, height, columns, column_widths=None):
        super().__init__(canvas)
        self.columns = columns
        self.column_widths = column_widths or {col: 100 for col in columns}

        self.tree_frame = ttk.Frame(canvas.master, width=width, height=height)
        self.tree_frame.place(x=x, y=y, width=width, height=height)

        self.scrollbar = ttk.Scrollbar(self.tree_frame)
        self.scrollbar.pack(side='right', fill='y')

        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.tree.yview)

        self.setup_treeview()
        self.tree.pack(side='left', fill='both', expand=True)

    def setup_treeview(self):
        for col in self.columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=self.column_widths.get(col, 100))
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#917FB3", fieldbackground="#917FB3", foreground="white")
        style.configure("Treeview.Heading", background="#917FB3", fieldbackground="#917FB3", foreground="white")
        style.map("Treeview", background=[("selected", "#E5BEEC")])

    def populate(self, data):
        self.tree.delete(*self.tree.get_children())
        for row in data:
            self.tree.insert("", "end", values=row[1:])

class TextWidget(BaseWidget):
    def __init__(self, canvas, x, y, width, height, bg_image, image_x, image_y, bg="#D9D9D9"):
        super().__init__(canvas)
        self.image = PhotoImage(file=relative_to_assets(bg_image))
        self.canvas.create_image(image_x, image_y, image=self.image)
        self.text = Text(
            bd=0,
            bg=bg,
            fg="#000716",
            highlightthickness=0
        )
        self.text.place(
            x=x,
            y=y,
            width=width,
            height=height
        )

class FormattedRectangle(BaseWidget):
    def __init__(self, canvas, bg_image, image_x, image_y):
        super().__init__(canvas)
        self.image = PhotoImage(file=relative_to_assets(bg_image))
        self.canvas.create_image(image_x, image_y, image=self.image)

class ChartWidget(BaseWidget):
    def __init__(self, canvas, x, y, width, height, title):
        super().__init__(canvas)
        self.frame = ttk.Frame(canvas.master)
        self.frame.place(x=x, y=y, width=width, height=height)
        self.title = title
        self.fig = None

    def create_chart(self, labels, data, fig_height, fig_width, facecolor):
        self.fig = Figure(figsize=(fig_height, fig_width), facecolor=facecolor, layout="constrained")
        ax = self.fig.add_subplot()
        ax.set_facecolor(facecolor)
        ax.bar(labels, data)
        ax.set_title(self.title)
        xlabels_new = [re.sub("(.{15})", "\\1\n", label, 0, re.DOTALL) for label in labels]
        ax.set_xticklabels(xlabels_new, rotation=45, ha='right')
        ax.tick_params(labelsize=7, colors="white")
        self.fig.tight_layout()

        chart = FigureCanvasTkAgg(self.fig, master=self.frame)
        chart.draw()
        chart.get_tk_widget().pack(fill='both', expand=True)

class ButtonWidget(BaseWidget):
    def __init__(self, canvas, x, y, width, height, bg_image, command=None, *args):
        super().__init__(canvas)
        self.image = PhotoImage(file=relative_to_assets(bg_image))
        self.command = command
        self.args = args
        self.button = Button(
            image=self.image,
            borderwidth=0,
            highlightthickness=0,
            command=self._execute_command,
            relief="flat"
        )
        self.button.place(
            x=x,
            y=y,
            width=width,
            height=height
        )

    def _execute_command(self):
        if self.command:
            self.command(*self.args)

class Chart(ABC):
    def __init__(self, fig_height, fig_width, facecolor, widget):
        self.fig_height = fig_height
        self.fig_width = fig_width
        self.facecolor = facecolor
        self.data = None
        self.labels = None
        self.widget = widget
        self.fig = Figure(figsize=(fig_height, fig_width), facecolor=facecolor, layout="constrained")
        self.db = MovieDatabase()
        self.canvas = None 

    @abstractmethod
    def load_data(self):
        pass

    def create_chart(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.fig.clear()
        ax = self.fig.add_subplot()
        ax.set_facecolor(self.facecolor)
        ax.bar(self.labels, self.data)
        ax.set_title(self.widget.title)
        xlabels_new = [re.sub("(.{15})", "\\1\n", label, 0, re.DOTALL) for label in self.labels]
        ax.set_xticklabels(xlabels_new, rotation=45, ha='right')
        ax.tick_params(labelsize=7, colors="white")
        self.fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.widget.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def refresh_chart(self):
        self.load_data()
        self.create_chart()

class LeftChart(Chart):
    def load_data(self):
        movies_vote_count = self.db.get_movies_vote_count()
        self.labels = [movie[0] for movie in movies_vote_count]
        self.data = [movie[1] for movie in movies_vote_count]

class MidChart(Chart):
    def load_data(self):
        movies_vote_average = self.db.get_movies_vote_average()
        self.labels = [movie[0] for movie in movies_vote_average]
        self.data = [movie[1] for movie in movies_vote_average]

class RightChart(Chart):
    def load_data(self):
        top_genres = self.db.get_top_genres()
        self.labels = [genre[0] for genre in top_genres]
        self.data = [genre[1] for genre in top_genres]

class MainChart(Chart):
    def load_data(self):
        movies_by_popularity = self.db.get_movies_popularity()
        self.labels = [movie[0] for movie in movies_by_popularity]
        self.data = [movie[1] for movie in movies_by_popularity]
