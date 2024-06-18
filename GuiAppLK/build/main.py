import asyncio
from database import MovieDatabase
from widget import *

#Setup window
window = Tk()
window.geometry("1280x800")
window.configure(bg="#FFFFFF")
window.title("Movies Database")
window_icon = PhotoImage(file=relative_to_assets("image_1.png"))
window.iconphoto(False, window_icon)


#functions for search and clear buttons
def clear_action():
    for widget in widgets:
        if isinstance(widget, EntryWidget):
            widget.entry.delete(0, 'end')
        elif isinstance(widget, TextWidget):
            widget.text.delete("1.0", "end")
    print("Clear button clicked")

def search_action(component):
    # Retrieve input values from the filter bar
    title = widgets[0].text.get("1.0", "end-1c").strip()
    genre = widgets[1].entry.get().strip()
    language = widgets[2].entry.get().strip()
    release_date_from = widgets[3].entry.get().strip()
    release_date_to = widgets[4].entry.get().strip()

    #Call API and save to DB
    db = MovieDatabase()
    asyncio.run(db.fetch_and_save_data(title, genre, language, release_date_from, release_date_to))
    
    if isinstance(component, TreeviewWidget):
        movies = db.get_movies()
        component.populate(movies)
    else:
        for chart in component:
            chart.refresh_chart()

#Kind of navigation  
def charts_nav():
    main()
 
def table_nav():
    table()

def main():
    db = MovieDatabase()
    global widgets
    widgets = []

    canvas = Canvas(
        window,
        bg="#FFFFFF",
        height=800,
        width=1280,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.place(x=0, y=0)

    base_widget = BaseWidget(canvas)
    base_widget.create_rectangle(0.0, 0.0, 1280.0, 800.0, fill="#601881")
    base_widget.create_rectangle(0.0, 0.0, 1280.0, 84.0, fill="#561EF3")

    base_widget.create_text(527.0, 16.0, "Language:")
    base_widget.create_text(701.0, 16.0, "Released Date - From:")
    base_widget.create_text(874.0, 16.0, "Released Date - To:")

    title_widget = TextWidget(canvas, 189.0, 33.0, 140.0, 26.0, "entry_1.png", 259.0, 47.0)
    genre_widget = EntryWidget(canvas, 363.0, 33.0, 140.0, 26.0, "entry_1.png", 433.0, 47.0)
    language_widget = EntryWidget(canvas, 536.0, 33.0, 140.0, 26.0, "entry_1.png", 606.0, 47.0)
    from_widget = DateEntryWidget(canvas, 700.0, 33.0, 140.0, 26.0, "entry_1.png", 780.0, 47.0)
    to_widget = DateEntryWidget(canvas, 873.0, 33.0, 140.0, 26.0, "entry_1.png", 953.0, 47.0)

    widgets.extend([title_widget, genre_widget, language_widget, from_widget, to_widget])

    base_widget.create_text(179.0, 16.0, "Title:")
    base_widget.create_text(353.0, 16.0, "Genre:")
    base_widget.create_text(13.0, 63.0, "Movies Database", fill="#000000")

    image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
    canvas.create_image(56.0, 36.0, image=image_1)

    main_chart_rect = FormattedRectangle(canvas, "main_chart.png", 634.0, 329.0)
    chart_left_rect = FormattedRectangle(canvas, "small_chart.png", 207.0, 664.0)
    chart_mid_rect = FormattedRectangle(canvas, "small_chart.png", 634.0, 664.0)
    chart_right_rect = FormattedRectangle(canvas, "small_chart.png", 1061.0, 664.0)
    
    chart_main_widget = ChartWidget(canvas, 50, 125, 1150, 400, "Top 15 Movies by Popularity")
    chart_left_widget = ChartWidget(canvas, 55, 555, 300, 210, "Top Movies by Vote Count")
    chart_mid_widget = ChartWidget(canvas, 480, 555, 300, 210, "Top Movies by Vote Average")
    chart_right_widget = ChartWidget(canvas, 910, 555, 300, 210, "Top  Genres")
    
    chart_main = MainChart(7.5, 4.5, "#320C9D", chart_main_widget)
    chart_left = LeftChart(3.5, 2.2, "#8D12B8", chart_left_widget)
    chart_mid = MidChart(3.5, 2.2, "#8D12B8", chart_mid_widget)
    chart_right = RightChart(3.5, 2.2, "#8D12B8", chart_right_widget)
    
    chart_main.load_data() 
    chart_left.load_data() 
    chart_mid.load_data()  
    chart_right.load_data()  
    
    chart_main.create_chart() 
    chart_left.create_chart() 
    chart_mid.create_chart()  
    chart_right.create_chart()  

    charts = [chart_main, chart_left, chart_mid, chart_right]
    
    clear_btn = ButtonWidget(canvas, 1047.0, 31.0, 78.0, 30.0, "clear_btn.png", clear_action)
    search_btn = ButtonWidget(canvas, 1144.0, 31.0, 78.0, 30.0, "search_btn.png", search_action, charts)
    charts_btn = ButtonWidget(canvas, 0.0, 84.0, 55.0, 22.0, "charts_btn.png", charts_nav)
    table_btn = ButtonWidget(canvas, 55.0, 84.0, 55.0, 22.0, "table_btn.png", table_nav)
    
    window.resizable(False, False)
    window.mainloop()

def table():
    db = MovieDatabase()
    global widgets
    widgets = []

    canvas = Canvas(
        window,
        bg="#FFFFFF",
        height=800,
        width=1280,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )
    canvas.place(x=0, y=0)

    base_widget = BaseWidget(canvas)
    base_widget.create_rectangle(0.0, 0.0, 1280.0, 800.0, fill="#601881")
    base_widget.create_rectangle(0.0, 0.0, 1280.0, 84.0, fill="#561EF3")

    base_widget.create_text(527.0, 16.0, "Language:")
    base_widget.create_text(701.0, 16.0, "Released Date - From:")
    base_widget.create_text(874.0, 16.0, "Released Date - To:")

    title_widget = TextWidget(canvas, 189.0, 33.0, 140.0, 26.0, "entry_1.png", 259.0, 47.0)
    genre_widget = EntryWidget(canvas, 363.0, 33.0, 140.0, 26.0, "entry_1.png", 433.0, 47.0)
    language_widget = EntryWidget(canvas, 536.0, 33.0, 140.0, 26.0, "entry_1.png", 606.0, 47.0)
    from_widget = DateEntryWidget(canvas, 700.0, 33.0, 140.0, 26.0, "entry_1.png", 780.0, 47.0)
    to_widget = DateEntryWidget(canvas, 873.0, 33.0, 140.0, 26.0, "entry_1.png", 953.0, 47.0)

    widgets.extend([title_widget, genre_widget, language_widget, from_widget, to_widget])

    base_widget.create_text(179.0, 16.0, "Title:")
    base_widget.create_text(353.0, 16.0, "Genre:")
    base_widget.create_text(13.0, 63.0, "Movies Database", fill="#000000")

    image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
    canvas.create_image(56.0, 36.0, image=image_1)
    table_rect = FormattedRectangle(canvas, "table_rect.png", 640.0, 415.0)
    
    columns = ("Title", "Genre", "Language", "Release date", "Popularity", "Vote average", "Vote count")
    column_widths = {"title": 150, "genre": 100, "language": 50, "release_date": 100, "popularity": 50, "vote_average": 50, "vote_count":50}
    tree_widget = TreeviewWidget(canvas, 90.0, 140.0, 1100.0, 540.0, columns, column_widths)
    movies = db.get_movies()
    tree_widget.populate(movies)
    
    clear_btn = ButtonWidget(canvas, 1047.0, 31.0, 78.0, 30.0, "clear_btn.png", clear_action)
    search_btn = ButtonWidget(canvas, 1144.0, 31.0, 78.0, 30.0, "search_btn.png", search_action, tree_widget)
    charts_btn = ButtonWidget(canvas, 0.0, 84.0, 55.0, 22.0, "charts_btn.png", charts_nav)
    table_btn = ButtonWidget(canvas, 55.0, 84.0, 55.0, 22.0, "table_btn.png", table_nav)
    
    window.resizable(False, False)
    window.mainloop()

if __name__ == "__main__":
    table()
