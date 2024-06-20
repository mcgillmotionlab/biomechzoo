import PySimpleGUI as sg
from processing import process_data, plot_data, update_ensembler_lines, filter_data, normalize_data, partition_data, remove_outliers
from settings import Settings
from events import EventTracker
from utils import sort_files

def main():
    # Initialize settings and event tracker
    settings = Settings()
    event_tracker = EventTracker()

    # Layout for the left section (File Upload)
    left_layout = [
        [sg.Text("File Upload Section")],
        [sg.Input(), sg.FileBrowse()],
        [sg.Button("Upload")]
    ]

    # Layout for the center section (Plot Display)
    center_layout = [
        [sg.Text("Plot Display Section")],
        [sg.Canvas(size=(400, 400), key="Canvas", expand_x=True, expand_y=True)]
    ]

    # Layout for the right section (Scrollable Settings)
    right_layout = [
        [sg.Text("Settings Section")],
        [sg.Column([[sg.Text(f"Setting {i+1}"), sg.Input(key=f"Setting{i+1}")] for i in range(20)], size=(200, 400), scrollable=True, vertical_scroll_only=True, expand_y=True, expand_x=True)]
    ]

    # Combine the layouts into the main layout
    layout = [
        [sg.Column(left_layout, size=(200, None), expand_x=True, expand_y=True), sg.VSeparator(), 
         sg.Column(center_layout, size=(400, None), expand_x=True, expand_y=True), sg.VSeparator(), 
         sg.Column(right_layout, size=(200, None), scrollable=True, vertical_scroll_only=True, expand_x=True, expand_y=True)]
    ]

    # Create the window
    window = sg.Window("BioMechZoo Ensembler GUI", layout, resizable=True, finalize=True)
    window.Maximize()

    # Event loop to process events and get values of the inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break

        if event == "Upload":
            # Example data processing and plotting
            data = 0  # Replace with actual data from file upload
            x, y = process_data(data)
            plot_data(x, y)
            event_tracker.log_event({"event": "upload", "data": values})  # Log the event

            # Example usage of other processing functions
            filtered_data = filter_data(data)
            normalized_data = normalize_data(data)
            partitioned_data = partition_data(data, 0, len(data)//2)
            cleaned_data = remove_outliers(data)
            update_ensembler_lines("path", "file", "fld", settings.settings)

        # Example of updating settings
        for i in range(20):
            key = f"Setting{i+1}"
            if key in values:
                settings.update_setting(key, values[key])

    window.close()

if __name__ == "__main__":
    main()
