import os
import shutil
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from processing import process_data, plot_data, update_ensembler_lines, filter_data, normalize_data, partition_data, remove_outliers
from settings import Settings
from events import EventTracker
from utils import sort_files
import numpy as np

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

def update_plot(fig, ax, data):
    ax.clear()
    ax.plot(data['x'], data['y'])
    ax.set_xlabel("Time")
    ax.set_ylabel("Value")
    fig.canvas.draw()

def organize_folder(path, method):
    if method == "Participants":
        organize_by_participants(path)
    elif method == "Conditions":
        organize_by_conditions(path)
    elif method == "Other":
        organize_by_other(path)

def organize_by_participants(path):
    for filename in os.listdir(path):
        if not os.path.isdir(os.path.join(path, filename)):
            participant = filename.split('_')[0]  # Assuming filenames start with participant ID
            participant_folder = os.path.join(path, participant)
            os.makedirs(participant_folder, exist_ok=True)
            shutil.move(os.path.join(path, filename), os.path.join(participant_folder, filename))

def organize_by_conditions(path):
    for filename in os.listdir(path):
        if not os.path.isdir(os.path.join(path, filename)):
            condition = filename.split('_')[1]  # Assuming condition is the second part of the filename
            condition_folder = os.path.join(path, condition)
            os.makedirs(condition_folder, exist_ok=True)
            shutil.move(os.path.join(path, filename), os.path.join(condition_folder, filename))

def organize_by_other(path):
    for filename in os.listdir(path):
        if not os.path.isdir(os.path.join(path, filename)):
            other_folder = os.path.join(path, 'Other')
            os.makedirs(other_folder, exist_ok=True)
            shutil.move(os.path.join(path, filename), os.path.join(other_folder, filename))

def create_section(name, layout, key):
    return [
        [sg.Button(f"{name}", key=f"{key}_TOGGLE", button_color=('white', 'blue'))],
        [sg.HorizontalSeparator(color='black')],
        [sg.pin(sg.Column(layout, key=key, visible=False))],
        [sg.HorizontalSeparator(color='black')]
    ]

def save_selected_figures(selected_figs, save_path):
    for fig, fig_num in selected_figs:
        fig.savefig(os.path.join(save_path, f"figure_{fig_num}.png"))

def create_center_layout(resize_option):
    center_layout = [[sg.Text("Plot Display Section")]]
    row = []
    for i, (fig, ax, canvas_key, checkbox_key) in enumerate(figures):
        row.append(sg.Checkbox("", key=checkbox_key, visible=False))
        row.append(sg.Canvas(size=(400, 400), key=canvas_key, expand_x=True, expand_y=True))
        if (i + 1) % resize_option == 0:
            center_layout.append(row)
            row = []
    if row:
        center_layout.append(row)
    return center_layout

def main():
    # Initialize settings and event tracker
    settings = Settings()
    event_tracker = EventTracker()

    # Layout for the left section (File Upload)
    left_layout = [
        [sg.Text("File Upload Section")],
        [sg.Input(key="Folder"), sg.FolderBrowse()],
        [sg.Button("Upload")],
        [sg.Text("Organize by")],
        [sg.Combo(["Participants", "Conditions", "Other"], key="OrganizeMethod", readonly=True)],
        [sg.Button("Organize")]
    ]

    # Initialize Matplotlib figures and axes
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    fig4, ax4 = plt.subplots(figsize=(8, 4))
    fig5, ax5 = plt.subplots(figsize=(8, 4))

    global figures
    figures = [(fig1, ax1, "Canvas1", "Checkbox1"), 
               (fig2, ax2, "Canvas2", "Checkbox2"), 
               (fig3, ax3, "Canvas3", "Checkbox3"), 
               (fig4, ax4, "Canvas4", "Checkbox4"), 
               (fig5, ax5, "Canvas5", "Checkbox5")]

    # Function to create the center layout based on the resize option
    center_layout = create_center_layout(1)  # Default to 1 image per row

    # Layouts for the right section (Scrollable Settings) with Reload Button
    initial_section_layout = [
        [sg.Text("Group"), sg.Input(key="Group")],
        [sg.Text("Condition names"), sg.Input(key="Condition names")],
        [sg.Text("Rows"), sg.Input(key="Rows")],
        [sg.Text("Columns"), sg.Input(key="Columns")],
        [sg.Text("Axis width"), sg.Input(key="Axis width")],
        [sg.Text("Axis height"), sg.Input(key="Axis height")],
        [sg.Text("Horizontal spacing"), sg.Input(key="Horizontal spacing")],
        [sg.Text("Vertical spacing"), sg.Input(key="Vertical spacing")],
        [sg.Text("Font name"), sg.Input(key="Font name")],
        [sg.Text("Font size"), sg.Input(key="Font size")],
        [sg.Text("Units"), sg.Input(key="Units")],
        [sg.Text("Figure width"), sg.Input(key="Figure width")],
        [sg.Text("Figure height"), sg.Input(key="Figure height")]
    ]

    analysis_layout = [
        [sg.Text("Coupling angles"), sg.Input(key="Coupling angles")],
        [sg.Text("Relative angles"), sg.Input(key="Relative angles")],
        [sg.Text("Continuous stats"), sg.Input(key="Continuous stats")],
        [sg.Button("Clear colorbars", key="CLEAR_COLORBARS")]
    ]

    processing_layout = [
        [sg.Text("Convert to zoo"), sg.Input(key="Convert to zoo")],
        [sg.Text("Explode channels"), sg.Input(key="Explode channels")],
        [sg.Text("Partition"), sg.Input(key="Partition")],
        [sg.Text("Normalize"), sg.Input(key="Normalize")],
        [sg.Text("Filter"), sg.Input(key="Filter")],
        [sg.Text("Custom"), sg.Input(key="Custom")]
    ]

    zoom_layout = [
        [sg.Text("Zoom on"), sg.Input(key="Zoom on")],
        [sg.Text("Zoom off"), sg.Input(key="Zoom off")],
        [sg.Text("Zoom restore"), sg.Input(key="Zoom restore")]
    ]

    events_layout = [
        [sg.Text("Clear all events"), sg.Input(key="Clear all events")],
        [sg.Text("Clear event by type"), sg.Input(key="Clear event by type")],
        [sg.Text("Delete all events"), sg.Input(key="Delete all events")],
        [sg.Text("Delete event by type"), sg.Input(key="Delete event by type")],
        [sg.Text("Delete single event"), sg.Input(key="Delete single event")],
        [sg.Text("Add other channel event"), sg.Input(key="Add other channel event")],
        [sg.Text("Add max event"), sg.Input(key="Add max event")],
        [sg.Text("Add min event"), sg.Input(key="Add min event")],
        [sg.Text("Add ROM event"), sg.Input(key="Add ROM event")],
        [sg.Text("Add gait events"), sg.Input(key="Add gait events")]
    ]

    stdev_layout = [
        [sg.Text("Visible"), sg.Input(key="Visible")],
        [sg.Text("Transparency"), sg.Input(key="Transparency")],
        [sg.Text("Stdline"), sg.Input(key="Stdline")],
        [sg.Text("Stcolor"), sg.Input(key="Stcolor")],
        [sg.Text("Stcolor within"), sg.Input(key="Stcolor within")]
    ]

    bar_graph_layout = [
        [sg.Text("Bar graph"), sg.Input(key="Bar graph")],
        [sg.Text("Bar color"), sg.Input(key="Bar color")],
        [sg.Text("Reorder bars"), sg.Input(key="Reorder bars")]
    ]

    line_layout = [
        [sg.Text("Line style"), sg.Input(key="Line style")],
        [sg.Text("Line style within"), sg.Input(key="Line style within")],
        [sg.Text("Line width"), sg.Input(key="Line width")],
        [sg.Text("Line color"), sg.Input(key="Line color")],
        [sg.Text("Line color within"), sg.Input(key="Line color within")],
        [sg.Text("Quick style"), sg.Input(key="Quick style")]
    ]

    axes_layout = [
        [sg.Text("Re-tag"), sg.Input(key="Re-tag")],
        [sg.Text("Xlabel"), sg.Input(key="Xlabel")],
        [sg.Text("Ylabel"), sg.Input(key="Ylabel")],
        [sg.Text("X limit"), sg.Input(key="X limit")],
        [sg.Text("Y limit"), sg.Input(key="Y limit")],
        [sg.Text("X ticks"), sg.Input(key="X ticks")],
        [sg.Text("Y ticks"), sg.Input(key="Y ticks")],
        [sg.Text("Axis font size"), sg.Input(key="Axis font size")],
        [sg.Text("Resize axis"), sg.Input(key="Resize axis")],
        [sg.Text("Delete single axis"), sg.Input(key="Delete single axis")],
        [sg.Text("Clear all empty axes"), sg.Input(key="Clear all empty axes")],
        [sg.Text("Clear titles"), sg.Input(key="Clear titles")],
        [sg.Text("Clear prompt"), sg.Input(key="Clear prompt")]
    ]

    insert_layout = [
        [sg.Text("Title"), sg.Input(key="Title")],
        [sg.Text("Axis ids (a, b, c, ...)"), sg.Input(key="Axis ids (a, b, c, ...)")],
        [sg.Text("Sig diff star"), sg.Input(key="Sig diff star")],
        [sg.Text("Legend"), sg.Input(key="Legend")],
        [sg.Text("Legend within"), sg.Input(key="Legend within")],
        [sg.Text("Horizontal line"), sg.Input(key="Horizontal line")],
        [sg.Text("Vertical line"), sg.Input(key="Vertical line")],
        [sg.Text("Normative PiG Kinematics"), sg.Input(key="Normative PiG Kinematics")],
        [sg.Text("Normative PiG Kinetics"), sg.Input(key="Normative PiG Kinetics")],
        [sg.Text("Normative OFM Angles"), sg.Input(key="Normative OFM Angles")],
        [sg.Text("Normative EMG"), sg.Input(key="Normative EMG")]
    ]

    ensembler_layout = [
        [sg.Text("Ensemble (SD)"), sg.Input(key="Ensemble (SD)")],
        [sg.Text("Ensemble (CI)"), sg.Input(key="Ensemble (CI)")],
        [sg.Text("Ensemble (CB)"), sg.Input(key="Ensemble (CB)")],
        [sg.Text("Ensemble (subject x condition) (SD)"), sg.Input(key="Ensemble (subject x condition) (SD)")],
        [sg.Text("Ensemble (subject x condition) (CI)"), sg.Input(key="Ensemble (subject x condition) (CI)")],
        [sg.Text("Combine data"), sg.Input(key="Combine data")],
        [sg.Text("Combine all"), sg.Input(key="Combine all")],
        [sg.Text("Combine within"), sg.Input(key="Combine within")],
        [sg.Text("Clear outliers"), sg.Input(key="Clear outliers")],
        [sg.Text("Clear all"), sg.Input(key="Clear all")]
    ]

    edit_layout = [
        [sg.Text("Edit fig names"), sg.Input(key="Edit fig names")],
        [sg.Text("Decrease fonts"), sg.Input(key="Decrease fonts")],
        [sg.Text("Increase fonts"), sg.Input(key="Increase fonts")],
        [sg.Text("Property editor on"), sg.Input(key="Property editor on")],
        [sg.Text("Property editor off"), sg.Input(key="Property editor off")],
        [sg.Combo(["1", "2", "3"], key="ResizeOption", readonly=True, default_value="1"), sg.Button("Change Column Numbers")]
    ]

    file_layout = [
        [sg.Text("Set working directory"), sg.Input(key="Set working directory")],
        [sg.Text("Load data"), sg.Input(key="Load data")],
        [sg.Text("Load single file"), sg.Input(key="Load single file")],
        [sg.Button("Save fig", key="SaveFig")],
        [sg.Text("Export"), sg.Input(key="Export")],
        [sg.Button("Exit"), sg.Button("Restart")]
    ]

    # Create the right layout with expandable sections
    right_layout = [
        [sg.Button("Reload", key="Reload")],
        [sg.Column(create_section("Initial Section", initial_section_layout, "INITIAL_SECTION"))],
        [sg.Column(create_section("Analysis", analysis_layout, "ANALYSIS"))],
        [sg.Column(create_section("Processing", processing_layout, "PROCESSING"))],
        [sg.Column(create_section("Zoom", zoom_layout, "ZOOM"))],
        [sg.Column(create_section("Events", events_layout, "EVENTS"))],
        [sg.Column(create_section("Stdev", stdev_layout, "STDEV"))],
        [sg.Column(create_section("Bar Graph", bar_graph_layout, "BAR_GRAPH"))],
        [sg.Column(create_section("Line", line_layout, "LINE"))],
        [sg.Column(create_section("Axes", axes_layout, "AXES"))],
        [sg.Column(create_section("Insert", insert_layout, "INSERT"))],
        [sg.Column(create_section("Ensembler", ensembler_layout, "ENSEMBLER"))],
        [sg.Column(create_section("Edit", edit_layout, "EDIT"))],
        [sg.Column(create_section("File", file_layout, "FILE"))]
    ]

    # Combine the layouts into the main layout
    layout = [
        [sg.Column(left_layout, size=(200, None), expand_x=True, expand_y=True), sg.VSeparator(), 
         sg.Column([[sg.Column(center_layout, size=(800, 2000), key="CenterColumn", scrollable=True, vertical_scroll_only=True, expand_x=True, expand_y=True)]], expand_x=True, expand_y=True), sg.VSeparator(), 
         sg.Column(right_layout, size=(200, 600), scrollable=True, vertical_scroll_only=True, expand_x=True, expand_y=True)]
    ]

    # Create the window
    window = sg.Window("BioMechZoo Ensembler GUI", layout, resizable=True, finalize=True)
    window.Maximize()

    figure_canvas_agg1 = draw_figure(window['Canvas1'].TKCanvas, fig1)
    figure_canvas_agg2 = draw_figure(window['Canvas2'].TKCanvas, fig2)
    figure_canvas_agg3 = draw_figure(window['Canvas3'].TKCanvas, fig3)
    figure_canvas_agg4 = draw_figure(window['Canvas4'].TKCanvas, fig4)
    figure_canvas_agg5 = draw_figure(window['Canvas5'].TKCanvas, fig5)

    def reload_plots(values):
        # Read current settings
        current_settings = {key: values[key] for key in settings.settings.keys()}
        
        # Example data processing and plotting based on current settings
        data1 = {
            'x': np.linspace(0, 10, 100),
            'y': np.sin(np.linspace(0, 10, 100))
        }
        data2 = {
            'x': np.linspace(0, 10, 100),
            'y': np.cos(np.linspace(0, 10, 100))
        }
        data3 = {
            'x': np.linspace(0, 10, 100),
            'y': np.tan(np.linspace(0, 10, 100))
        }
        data4 = {
            'x': np.linspace(0, 10, 100),
            'y': np.sin(np.linspace(0, 10, 100) * 2)
        }
        data5 = {
            'x': np.linspace(0, 10, 100),
            'y': np.cos(np.linspace(0, 10, 100) * 2)
        }
        update_plot(fig1, ax1, data1)
        update_plot(fig2, ax2, data2)
        update_plot(fig3, ax3, data3)
        update_plot(fig4, ax4, data4)
        update_plot(fig5, ax5, data5)
        event_tracker.log_event({"event": "reload", "data": current_settings})

    # Initial plot load
    window.read(timeout=1)  # Allow the GUI to initialize
    reload_plots({key: None for key in settings.settings.keys()})  # Use dummy values for the initial load

    # Variables to control the state of the Save Fig button
    save_fig_toggle = False

    # Event loop to process events and get values of the inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':
            break

        if event == "Upload":
            # Initial data processing and plotting
            reload_plots(values)
        
        if event == "Reload":
            # Reload the plots based on current settings
            reload_plots(values)

        if event == "Organize":
            folder_path = values["Folder"]
            organize_method = values["OrganizeMethod"]
            if folder_path and organize_method:
                organize_folder(folder_path, organize_method)

        if event == "SaveFig":
            save_fig_toggle = not save_fig_toggle
            for fig, ax, canvas_key, checkbox_key in figures:
                window[checkbox_key].update(visible=save_fig_toggle)
            if not save_fig_toggle:
                selected_figs = []
                for i, (fig, ax, canvas_key, checkbox_key) in enumerate(figures):
                    if values[checkbox_key]:
                        selected_figs.append((fig, i + 1))
                if selected_figs:
                    save_path = sg.popup_get_folder("Select a folder to save the figures")
                    if save_path:
                        save_selected_figures(selected_figs, save_path)

        if event == "Resize":
            resize_option = int(values["ResizeOption"])
            new_center_layout = create_center_layout(resize_option)
            window['CenterColumn'].update(visible=False)  # Hide current layout
            window['CenterColumn'].Widget.pack_forget()  # Forget current layout
            window.extend_layout(window, [[sg.Column(new_center_layout, key='CenterColumn', scrollable=True, vertical_scroll_only=True, size=(800, 2000))]])  # Add new layout
            window['CenterColumn'].update(visible=True)  # Show updated layout

            # Redraw figures in new layout
            for fig, ax, canvas_key, checkbox_key in figures:
                draw_figure(window[canvas_key].TKCanvas, fig)  # Draw new canvas

        if event.endswith("_TOGGLE"):
            section_key = event.replace("_TOGGLE", "")
            window[section_key].update(visible=not window[section_key].visible)

        # Example of updating settings
        for key, value in values.items():
            settings.update_setting(key, value)

    window.close()

if __name__ == "__main__":
    main()
