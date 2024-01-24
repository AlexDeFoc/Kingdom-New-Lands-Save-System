from tkinter import *
from tkinter.font import Font
import pickle
import sqlite3
import os
import shutil
import time
from pathvalidate import sanitize_ltsv_label as sanitize_Name

#GITHUB Version

# SAVE ELEMENTS
def get_time(*args):
    for i in args:
        if i == "day":
            i = time.localtime().tm_mday
            
        elif i == "hour":
            i = time.localtime().tm_hour
            
        elif i == "minute":
            i = time.localtime().tm_min
            
    return i

class Save_Data:
    def __init__(self):
        self.name = user_INPUT()
        self.day = get_time('day')
        self.hour = get_time('hour')
        self.minute = get_time('minute')
    
    def get_name(self):
        return self.name
    
    def get_day(self):
        return self.day
    def get_hour(self):
        return self.hour
    def get_minute(self):
        return self.minute

    
MAIN_PATH = os.path.join(os.path.expandvars('%USERPROFILE%'), 'AppData', 'LocalLow', 'noio', 'Kingdom')
SAVES_PATH = os.path.join(os.path.expandvars('%USERPROFILE%'), 'AppData', 'LocalLow', 'noio', 'Kingdom', 'Saves')

components_name = {'main': 'storage_v34_AUTO.dat',
                    'unlocks': 'unlocks'}

root = Tk()
root.title('Kingdom New Lands - Save/Load App')
root.geometry("600x600")

# Creating our font
app_font = Font(
    family="Brush Script MT",
    size=30,
    weight="bold")

# Create frame
app_frame = Frame(root)
app_frame.pack(pady=10)

# Create listbox
item_list = Listbox(app_frame,
                    font=app_font,
                    width=25,
                    height=5,
                    bg="SystemButtonFace",
                    bd=0,
                    fg="#464646",
                    highlightthickness=0,
                    selectbackground="#a6a6a6",
                    activestyle="none"
                    )

item_list.pack(side=LEFT, fill=BOTH)

# Create scrollbar
item_scrollbar = Scrollbar(app_frame)
item_scrollbar.pack(side=RIGHT, fill=BOTH)

# Add scrollbar
item_list.config(yscrollcommand=item_scrollbar.set)
item_scrollbar.config(command=item_list.yview)

# Error label
error_label = Label(root, text="")
error_label.pack()

# Entry box to add items to the list
user_input = StringVar()
save_entry = Entry(root, font=("Helvetica", 24), width=30, textvariable=user_input)
save_entry.pack(pady=20)
save_entry.focus()

# Create a button frame
button_frame = Frame(root)
button_frame.pack(pady=20)


# CONSTANTS
new_user_status = False


# FUNCTIONS

# New user detection:
# Creation of detection file
def app_config():
    if os.path.exists("configurator"):
        new_user_status = False
    else:
        with open("configurator", 'w') as config:
            config.write("")
    
    

# Utility Functions
def in_LIST(item):
    isContained = item in item_list.get(0, END)
    return isContained

def len_LIST():
    return item_list.index(END)

def value_ITEM(index):
    return item_list.get(index)

def user_INPUT():
    #Sanitize user_input
    # return sanitize_name(save_entry.get(), "")
    return sanitize_Name(save_entry.get(), "")

def is_user_EMPTY():
    if user_INPUT() == "":
        return True


def Select(event):
    global b
    try:
        b = item_list.selection_get()
        selection_VAR.set(b)
    except TclError as e:
        # print(e)
        # print("Please select something")
        pass
    
selection_VAR = StringVar()
selection_VAR.set("No selection")

def value_SELECT():
    result = selection_VAR.get()
    return result

def index_SELECT():
    return item_list.curselection()[0]

item_list.bind("<<ListboxSelect>>", Select)


# App interface : Functions
# Add item to list
def add_item():
    if not is_user_EMPTY():
        if not in_LIST(user_INPUT()):
            item_list.insert(END, user_INPUT())

# Remove item from list
def remove_item():
    try:
        item_list.delete(index_SELECT())
        revert_log()
    except IndexError:
        generate_log("Select to delete")

# Clear text_entry
def clear_entry():
    save_entry.delete(0, END)
    save_entry.focus()

# Under the hood of the app - #1 Saving items, #2 Deleting items, #3 Loading items
# Export list state to file
def save_list_state():
    # Dummy list
    d_list = []
    
    # Add item names to a list
    for i in range(len_LIST()):
        d_list.insert(i, value_ITEM(i))
    
    # Write list to file
    with open ("save_list", "wb") as file:
        pickle.dump(d_list, file)

# Clear items & save_file
def del_list_file():
    try:
        item_list.delete(0, END)
        os.remove("save_list")
    except FileNotFoundError as e:
        print("Save_list file doesnt exist")

# Loading items into the list
def load_item():
    if os.path.exists("save_list"):
        # Open save file and store data into a dummy list
        with open("save_list", 'rb') as file:
            d_list = pickle.load(file)
        
        # Delete present list
        item_list.delete(0, END)
        
        # Getting the data from the db
        # Connect to db
        conn = sqlite3.connect('saves.db')

        # Create a cursor
        c = conn.cursor()
        
        # Get the data
        c.execute("SELECT name FROM saves")
        data = c.fetchall()
        
        # for i in range(len_LIST()):
        for index in range(len(d_list)):
            item_list.insert(END, data[index][0])
        
        # Commit changes
        conn.commit()

        # Close Connection
        conn.close()

# IRL of the app - #1 Move data, #2 Delete specific data, #3 Delete all data (data = save_components)   
def move_data():
    
    data_name = user_INPUT()
    
    if not os.path.exists(SAVES_PATH):
        os.mkdir(SAVES_PATH)
        
    # Make the folder for the data
    if not os.path.exists(os.path.join(SAVES_PATH, data_name)) and not user_INPUT == "":
        os.mkdir(os.path.join(SAVES_PATH, data_name))
        
        # Copy the data into the new folder
        for key in components_name.keys():
            shutil.copy(os.path.join(MAIN_PATH, components_name.get(key)), os.path.join(SAVES_PATH, data_name))
            
        revert_log()
    elif is_user_EMPTY():
        generate_log("Enter a name")
    else:
        print("Folder already present")
    
    
        

# Deleting a specific data folder
def del_data():
    data_name = value_SELECT()
    filepath = os.path.join(SAVES_PATH, data_name)
    if os.path.exists(filepath):
        shutil.rmtree(filepath)

# Deleting the saves directory
def del_all_data():
    if os.path.exists(SAVES_PATH):
        shutil.rmtree(SAVES_PATH)

# Load the data from the selected folder
def load_data():
    data_name = value_SELECT()
    
    if data_name == "No selection":
        generate_log("Select a save to load")
    
    if not data_name == "No selection" and os.path.exists(os.path.join(SAVES_PATH, data_name)) == True:
        for key in components_name.keys():
            shutil.copy(os.path.join(SAVES_PATH, data_name, components_name[key]), os.path.join(MAIN_PATH))
            print("Loaded: " + components_name[key])
        revert_log()


# Database part of the app - #1 Create db, #2 Add item to db, #3 Delete item from db, #4 Delete db
#Creating db
def create_db():
    if new_user_status == True or not os.path.exists("saves.db"):
        #Connect to db
        conn = sqlite3.connect('saves.db')

        # Create a cursor
        c = conn.cursor()

        # Insert into table
        c.execute("""CREATE TABLE saves (
            name text,
            day integer,
            hour integer,
            minute integer)""")

        # Commit changes
        conn.commit()

        # Close Connection
        conn.close()    

# Save item to db
def add_i_db():
    new_save = Save_Data()
    
    # Connect to db
    conn = sqlite3.connect('saves.db')

    # Create a cursor
    c = conn.cursor()
    
    # Deposit the instance values
    name_value = new_save.get_name()
    day_value = new_save.get_day()
    hour_value = new_save.get_hour()
    minute_value = new_save.get_minute()
    
    # Add values to db
    if not is_user_EMPTY():
        if in_LIST(user_INPUT()):
            match = user_INPUT()
            c.execute("UPDATE saves SET day = '{}', hour = '{}', minute = '{}' WHERE name = '{}'".format(new_save.get_day(), new_save.get_hour(), new_save.get_minute(), match))
            # print("Item replaced")
        else:
            c.execute("INSERT INTO saves VALUES (:name, :day, :hour, :minute)",
            {
                'name': name_value,
                'day': day_value,
                'hour': hour_value,
                'minute': minute_value
            }
            )
            # print("New Item added")
            
    # Commit changes
    conn.commit()

    # Close Connection
    conn.close()
    
    # # Connect to db
    # conn = sqlite3.connect('saves.db')

    # # Create a cursor
    # c = conn.cursor()
    
    # c.execute("SELECT * FROM saves")
    # t = c.fetchall()
    # print(t)
    
    # # Commit changes
    # conn.commit()

    # # Close Connection
    # conn.close()

# Delete item from db
def del_i_db():
    # Connect to db
    conn = sqlite3.connect('saves.db')

    # Create a cursor
    c = conn.cursor()

    # Deleting the selected item in the list from the db
    try:
        record_to_be_deleted = index_SELECT()+1
        c.execute("DELETE FROM saves WHERE oid = ?", (record_to_be_deleted,))
        
    except IndexError as e:
        # print("Please select something to delete")
        pass

    # Commit changes
    conn.commit()

    # Close Connection
    conn.close()

# Delete db
def del_db():
    if os.path.exists("saves.db"):
        # Connect to db
        conn = sqlite3.connect('saves.db')

        # Create a cursor
        c = conn.cursor()
        
        # Dropping/Erasing the db
        c.execute("DELETE FROM saves")
        
        # Commit changes
        conn.commit()

        # Close Connection
        conn.close()
        
        # Reinitialize db
        create_db()


# BUTTONS FUNCTIONS
def del_btn_functions():
    del_i_db()
    del_data()
    remove_item()
    save_list_state()

def add_btn_functions():
    add_i_db()
    add_item()
    save_list_state()
    move_data()
    clear_entry()
    
def load_btn_functions():
    load_data()
    
def del_dropdown_btn_functions():
    del_list_file()
    save_list_state()
    del_all_data()
    del_db()
    create_db()
    clear_entry()


# Display Error messages
def generate_log(log):
    error_label.config(text=log)
    
def revert_log():
    error_label.config(text="")

def about_pop_up():
    # Create window if less then max amount
    pop = Toplevel(root)
    pop.title("About app")
    pop.geometry("400x300")
    # pop.columnconfigure(0, weight=1)
    # pop.rowconfigure(0, weight=1)
    # pop.rowconfigure(1, weight=1)

    pop_version = Label(pop, text="V1.0.0.0", font=("Helvetica", 24))
    pop_version.pack(pady=15)
    pop_version.place(relx=0.5, rely=0.2, anchor=CENTER)
    
    exit_button = Button(pop, text="Exit", font=("Helvetica", 24), command=pop.destroy)
    exit_button.pack()
    exit_button.place(relx=0.5, rely=0.5, anchor=CENTER)
    
    thanks = Label(pop, text="Made by ME for the folks", font=("Helvetica", 14))
    thanks.pack(pady=15)
    thanks.place(relx=0.5, rely=0.8, anchor=CENTER)


# Startup of app
app_config()

# Create db if needed
create_db()

# Functions to run for older users
if new_user_status == False:
    load_item()

my_menu = Menu(root)
root.config(menu=my_menu)

# Add items to the menu
file_menu = Menu(my_menu, tearoff=False)
my_menu.add_cascade(label="Other options", menu=file_menu)
# Add dropdown items
file_menu.add_command(label="Delete all saves", command=del_dropdown_btn_functions)
file_menu.add_command(label="About app", command=about_pop_up)


# Add buttons
delete_button = Button(button_frame, text="Delete save", command=del_btn_functions)
add_button = Button(button_frame, text="Add save", command=add_btn_functions)
load_button = Button(button_frame, text="Load save", command=load_btn_functions)

delete_button.grid(row=0, column=0, padx=20)
add_button.grid(row=0, column=1)
load_button.grid(row=0, column=2, padx=20)


# Add bind functions
def del_btn_click(event):
    del_btn_functions()
    
def add_btn_click(event):
    add_btn_functions()
    
def about_btn_click(event):
    about_pop_up()
    
# Debug functions
def query_db(event):
    # Connect to db
    conn = sqlite3.connect('saves.db')

    # Create a cursor
    c = conn.cursor()

    # List items inside db
    c.execute("SELECT * FROM saves")
    data = c.fetchall()

    print(data)
    
    # Commit changes
    conn.commit()

    # Close Connection
    conn.close()
    
def read_save_file(event):
    if os.path.exists("save_list"):
        # Open save file and store data into a dummy list
        with open("save_list", 'rb') as file:
            d_list = pickle.load(file)
        
        # Print d_list
        print(d_list)

# Add binds
root.bind_all("<BackSpace>", del_btn_click)
root.bind_all("<Return>", add_btn_click)
root.bind_all("<Control-KeyPress-s>", add_btn_click)
root.bind_all("<Escape>", about_btn_click)
# root.bind_all("<o>", query_db) #DEBUG ONLY
# root.bind_all("<p>", read_save_file) #DEBUG ONLY


root.mainloop()