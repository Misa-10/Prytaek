import tkinter as tk
import configparser
import os
from pynput.keyboard import Key, Listener
import pyautogui
import time
import pytesseract
from PIL import Image,ImageOps,ImageGrab
import cv2
import numpy as np



################################################################
#                                                              #
#                    Script                                    #
#                                                              #
################################################################

counter = 1

def create_ini_file():
    config_name = config_name_entry.get()
    if config_name:
        config = configparser.ConfigParser()
        with open('./configurations/deplacement/'+config_name + '.ini', 'w') as configfile:
            config.write(configfile)
        log_status(f"Le fichier {config_name}.ini a été créé.")
        update_file_list()
    else:
        log_status("Veuillez entrer un nom de configuration valide.")

def update_file_list():
    # Clear the listbox
    file_listbox.delete(0, tk.END)
    # Get a list of all .ini files in the current directory
    ini_files = [f for f in os.listdir('./configurations/deplacement') if f.endswith('.ini')]
    # Add each file to the listbox
    for f in ini_files:
        file_listbox.insert(tk.END, f)

def select_ini_file(event):
    # Get the name of the selected file
    selection = file_listbox.get(file_listbox.curselection())
    # Set the config name entry to the selected file's name
    config_name_entry.delete(0, tk.END)
    # Display a message indicating which configuration is being used
    log_status(f"Vous utilisez la configuration : {selection}")

def delete_ini_file():
    selection = file_listbox.get(file_listbox.curselection())
    os.remove('./configurations/deplacement/'+selection)
    update_file_list()
    log_status(f"Le fichier {selection} a été supprimé.")
    
def update_selected_file():
    global counter
    # Check if an item in the listbox is selected
    if file_listbox.curselection():
        # Get the current position of the mouse
        x, y = pyautogui.position()
        # Get the name of the selected file
        selection = file_listbox.get(file_listbox.curselection())
        # Update the selected file with the mouse position
        config = configparser.ConfigParser()
        config.read('./configurations/deplacement/'+selection)
        config[f"{counter}"] = {'x': f"{x}", 'y': f"{y}"}
        with open('./configurations/deplacement/'+selection, 'w') as configfile:
            config.write(configfile)
        # Display a message indicating that the file has been updated
        log_status(f"Le fichier {selection} a été mis à jour avec la position du curseur.")
        # Increment the counter
     
        counter += 1
    else:
            # Display a message indicating that no file has been selected
             log_status(f"Veuillez sélectionner un fichier dans la liste.")
            
def process_selected_file():
    if file_listbox.curselection():
        # Get the name of the selected file
        selection = file_listbox.get(file_listbox.curselection())
        # Read the selected file
        config = configparser.ConfigParser()
        config.read('././configurations/deplacement/'+selection)
        # Get the initial coordinates
        current_coordinate = extract_coordinates()
        # Move the mouse to each position specified in the file
        for section in config.sections():
            x = int(config[section]['x'])
            y = int(config[section]['y'])
            # Move the mouse to the position
            pyautogui.moveTo(x, y)
            # Perform a left click
            pyautogui.click(button='left')
            # Wait for a short time to allow the click to complete
            time.sleep(0.1)
            log_status(f"Moved mouse to ({x}, {y})")
            # Continuously check the coordinates until they change
            while current_coordinate == extract_coordinates():
                time.sleep(0.001)
            # Update the current coordinates
            current_coordinate = extract_coordinates()
        # Display a message indicating that the file has been processed
        log_status(f"Le fichier {selection} a été traité.")
    else:
        # Display a message indicating that no file has been selected
        log_status("Veuillez sélectionner un fichier dans la liste.")
     


def extract_coordinates():
    

    # Take a screenshot of the top left of the screen
    start_time_extract_coordinates = time.time()
    screenshot = ImageGrab.grab(bbox=(0, 0, 500, 300))
    rgb_image = screenshot.convert('RGB')
    rgb_image.save('my_image.jpg', format='JPEG')

    # Find white pixels and create a mask
    white_tolerance = 50  # adjust this as needed
    mask = Image.new('1', screenshot.size, 0)
    for x in range(screenshot.width):
        for y in range(screenshot.height):
            r, g, b = rgb_image.getpixel((x, y))
            if abs(r - 255) <= white_tolerance and abs(g - 255) <= white_tolerance and abs(b - 255) <= white_tolerance:
                mask.putpixel((x, y), 1)
    # convert the mask image to mode "L"
    mask = mask.convert("L")
    # Apply the mask to the original image to keep only white pixels
    result = ImageOps.colorize(mask, (0, 0, 0), (255, 255, 255))

    # Save the result as a JPEG file
    result.save('my_image2.jpg', 'JPEG')

    # Use pytesseract to read text from the image
    string = pytesseract.image_to_string(result)
    
    # Find the start index of the coordinates string
    start_index = string.find("Coordonnées :") + len("Coordonnées : ")

    # Find the end index of the coordinates string
    end_index = string.find("\n", start_index)

    # Extract the coordinates string
    coordinates_string = string[start_index:end_index]

    # Split the coordinates string into a list of two strings
    coordinates_list = coordinates_string.split(", ")

    # Convert the coordinate strings to integers
    x_coord = int(coordinates_list[0])
    y_coord = int(coordinates_list[1])

    # print the time taken to execute the script
    end_time_extract_coordinates = time.time()
    log_status(f"Execution time (extract_coordinates): {end_time_extract_coordinates - start_time_extract_coordinates:.2f} seconds")


    # Delete the temporary files
    os.remove('my_image.jpg')
    os.remove('my_image2.jpg')
    print(x_coord, y_coord)
    # Return the coordinates as a tuple
    return [x_coord, y_coord]


def on_press(key):
    if key == Key.shift:
        update_selected_file()
    elif key == Key.ctrl_l:
        process_selected_file()
    
           
        

################################################################
#                                                              #
#                    Interface                                 #
#                                                              #
################################################################


# Create the GUI
root = tk.Tk()
root.title("Création de fichier INI")
root.geometry("600x500")

# Configuration name label and entry
config_name_label = tk.Label(root, text="Nom de la configuration:")
config_name_label.pack()
config_name_entry = tk.Entry(root)
config_name_entry.pack()

# Create file button
create_button = tk.Button(root, text="Créer fichier", command=create_ini_file)
create_button.pack()

# File listbox and delete button
file_frame = tk.Frame(root)
file_frame.pack(fill=tk.BOTH, expand=True)

file_listbox = tk.Listbox(file_frame)
file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
update_file_list()
file_listbox.bind("<<ListboxSelect>>", select_ini_file)

delete_button = tk.Button(file_frame, text="Supprimer fichier", command=delete_ini_file)
delete_button.pack(side=tk.BOTTOM)

# Status text box
status_text = tk.Text(root, height=5)
status_text.pack(fill=tk.BOTH, expand=True)

def log_status(message):
    # Insert the message at the end of the text box
    status_text.insert(tk.END, message + '\n')
    # Scroll the text box to show the latest message
    status_text.see(tk.END)
    
# Mouse listener
listener = Listener(on_press=on_press)
listener.start()


# Run the GUI
root.mainloop()
