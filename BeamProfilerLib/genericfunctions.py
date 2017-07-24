
import pickle
from tkinter import Tk, filedialog
from datetime import datetime
import os

def choose_folder(initialdir='E://'):
    '''dialog box for folder selection
        info at https://tkinter.unpythonic.net/wiki/tkFileDialog
    '''
    root = Tk()
    root.withdraw()
    directory = filedialog.askdirectory(initialdir=initialdir)
    return (directory)


def choose_filename(initialdir='E://'):
    '''dialog box for folder selection
        info at https://tkinter.unpythonic.net/wiki/tkFileDialog
    '''

    root = Tk()
    root.withdraw()
    filename = filedialog.askopenfilename(initialdir=initialdir)
    return (filename)


def choose_filenames(initialdir='E://'):
    '''dialog box for folder selection
        info at https://tkinter.unpythonic.net/wiki/tkFileDialog
    '''
    root = Tk()
    root.withdraw()
    filenames = filedialog.askopenfilenames(initialdir=initialdir)
    return (filenames)


def choose_save_filename(initialdir='E://'):
    '''dialog box for folder selection
        info at https://tkinter.unpythonic.net/wiki/tkFileDialog
    '''
    root = Tk()
    root.withdraw()
    filename = filedialog.asksaveasfilename(initialdir=initialdir)
    return (filename)


# %% Generic Utilities


def file_creation_date(file):
    return datetime.fromtimestamp(
        int(os.path.getmtime(file))).strftime('%Y-%m-%d-%H.%M.%S')


def save_obj(obj, name):

    try:
        with open('obj/' + name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
    except:
        with open(name + '.pkl', 'wb') as f:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

def dictprint(dictionary):

    for x in dictionary:
        print(x)
        for y in dictionary[x]:
            print(y, ':', dictionary[x][y])