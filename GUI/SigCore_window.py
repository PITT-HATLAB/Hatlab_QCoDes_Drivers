# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 18:45:41 2018

@author: Hatlab_3
"""
import h5py
import numpy as np
import tkinter as tk
from tkinter import filedialog as tkFileDialog
import datetime
import os
from instrumentserver.client import Client
from functools import partial
import ctypes
import pathlib
apppath=pathlib.Path(__file__).parent.resolve()
appid = u'Hatlab.GeneratorGui.1.0.0' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
SAVE_CONFIG_DIR = r"M:\code\project\temp\InstrumentControl\GeneratorSettings\Pump_condition\\"


def advanced_input_label(window_name, keys, units, row_init=0, column_init=0, grid=None, entry_init=None, width=20):
    '''
    window_name: Tk window name
    keys: list of all the input entry name
    units: the units of the input
    '''
    label_set = []
    entry_set = []
    unit_set = []
    if grid == None:
        for i in range(len(keys)):
            '''
            There are three parts you need to combine:
            1. name of parameter (list)
            2. input entry of parameter
            3. units (list)
            '''
            label_temp = tk.Label(window_name, text=keys[i])
            label_temp.grid(row=i + row_init, column=column_init)
            label_set.append(label_temp)
            entry_temp = tk.Entry(window_name, width=width)
            entry_temp.grid(row=i + row_init, column=column_init + 1)
            if entry_init != None:
                entry_temp.insert(0, str(entry_init[i]))
            entry_set.append(entry_temp)
            unit_temp = tk.Label(window_name, text=units[i])
            unit_temp.grid(row=i + row_init, column=column_init + 2)
            unit_set.append(unit_temp)
    else:
        num = 0
        for row in range(int(grid[0])):
            for column in range(int(grid[1])):
                label_temp = tk.Label(window_name, text=keys[num])
                label_temp.grid(row=row + row_init, column=3 * column + column_init)
                label_set.append(label_temp)
                entry_temp = tk.Entry(window_name, width=width)
                entry_temp.grid(row=row + row_init, column=3 * column + column_init + 1)
                if entry_init != None:
                    entry_temp.insert(0, str(entry_init[num]))
                entry_set.append(entry_temp)
                unit_temp = tk.Label(window_name, text=units[num])
                unit_temp.grid(row=row + row_init, column=3 * column + column_init + 2)
                unit_set.append(unit_temp)
                num += 1
    return label_set, entry_set, unit_set


def wrong_window(Output):
    temp = tk.Toplevel()
    temp.title("Something Wrong, mortal!!!")
    temp.geometry('300x100+500+300')

    def trick_window():
        temp = tk.Toplevel()
        temp.title("Something Wrong, mortal!!!")
        temp.geometry('300x100+500+300')
        label = tk.Label(temp, text="You're so bad!")
        label.grid(row=0)
        button2 = tk.Button(temp, text="Close", command=temp.destroy)
        button2.grid(row=1)

    label = tk.Label(temp, text=Output, wraplength=300)
    label.grid(row=0)
    button1 = tk.Button(temp, text="Ha?", command=trick_window)
    button1.grid(row=1)
    button2 = tk.Button(temp, text="Fine, I got it", command=temp.destroy)
    button2.grid(row=2)
    return


def SigCore_window(params, cli:Client):
    fridge_date = params.get('fridge_date', "20XXXXXX")
    save_date = params.get('save_date', datetime.date.today().strftime('%Y%m%d'))
    directory = SAVE_CONFIG_DIR + save_date + "\\"
    instr_list = cli.list_instruments()
    allGens = {}
    for instr_name, instr_type in instr_list.items():
        driver_cls_name = instr_type.__name__
        if driver_cls_name in ['SignalCore_SC5511A', 'SignalCore_SC5506A', 'Keysight_N5183B', 'N51x1']:
            allGens[instr_name] = cli.get_instrument(instr_name)

    try:
        os.makedirs(directory)
    except WindowsError:
        pass
    except:
        raise
    print(directory)
    window_h = len(allGens) * 23 + 120
    temp = tk.Tk()
    temp.geometry(f'1050x{int(window_h)}+500+300')
    temp.title('Generator Control')
    try:
        temp.iconbitmap(str(apppath) +'\\icons\\SigCoreWindow.ico')
        # import base64
        # with open("SigCoreWindow.ico", "rb") as image_file:
            # image_data_base64_encoded_string = base64.b64encode(image_file.read())
        # print(image_data_base64_encoded_string)
        # temp.iconbitmap(tk.PhotoImage(data="""iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAIA
        # AAAlC+aJAAAA/0lEQVR4nO3Zyw7CMAxEUdP//+W2rCqBoJA2noclS1kn9yjLeex7xKY76+
        # wNS+l6KSCjXgdIqhcB8uoVgNR6OiC7ngsA1BMBmHoWAFZPASDr8QBwPRiAr0cCKPUwAKse
        # AyDWAwDc+mwAvT4VoKjPA4jqkwC6+gyAtD7WSYC6fu4HDOonAB71dwE29bcATvXXAWb1Fw
        # F+9VcAlvXDANf6MYBx/QDAu/4fwL7+J6BC/TmgSP0JoE79N0Cp+g9Atfp3QMH6F0DN+gNQ
        # tj62WErXB2PgQNZLAb3U6wC91OsAvdTrAL3U6wC91OsAvdTrAL3U6wC91OsAvdTrAL3Uz7
        # z+BNmX4gqbppsaAAAAAElFTkSuQmCC"""))
        # temp.iconbitmap(tk.PhotoImage(file="SigCoreWindow.ico"))
        # temp.iconbitmap(tk.PhotoImage(data="""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"""))
    except Exception as e:
        print(e)
        pass
    def get_one_gen(idx):
        gen = list(allGens.values())[idx]
        SC_entry_set[idx * 4].delete(0, tk.END)
        SC_entry_set[idx * 4].insert(0, int(gen.output_status()))
        SC_entry_set[idx * 4 + 1].delete(0, tk.END)
        SC_entry_set[idx * 4 + 1].insert(0, np.round(gen.frequency() * 1e-9, 9))
        SC_entry_set[idx * 4 + 2].delete(0, tk.END)
        SC_entry_set[idx * 4 + 2].insert(0, gen.power())
        SC_entry_set[idx * 4 + 3].delete(0, tk.END)
        SC_entry_set[idx * 4 + 3].insert(0, int(gen.reference_source()))

    def set_one_gen(idx):
        gen = list(allGens.values())[idx]
        gen.output_status(int(SC_entry_set[idx * 4 ].get()))
        gen.frequency(np.round(float(SC_entry_set[idx * 4  + 1].get()) * 1e9))
        gen.power(float(SC_entry_set[idx * 4  + 2].get()))
        gen.reference_source(int(SC_entry_set[idx * 4  + 3].get()))

    def get_all_value():
        i = 0
        for gen_name, gen in allGens.items():
            SC_entry_set[i].delete(0, tk.END)
            SC_entry_set[i].insert(0, int(gen.output_status()))
            SC_entry_set[i + 1].delete(0, tk.END)
            SC_entry_set[i + 1].insert(0, np.round(gen.frequency() * 1e-9, 9))
            SC_entry_set[i + 2].delete(0, tk.END)
            SC_entry_set[i + 2].insert(0, gen.power())
            SC_entry_set[i + 3].delete(0, tk.END)
            SC_entry_set[i + 3].insert(0, int(gen.reference_source()))
            i += 4

    def set_all_value():
        i = 0
        for gen_name, gen in allGens.items():
            gen.output_status(int(SC_entry_set[i].get()))
            gen.frequency(np.round(float(SC_entry_set[i + 1].get()) * 1e9))
            gen.power(float(SC_entry_set[i + 2].get()))
            gen.reference_source(int(SC_entry_set[i + 3].get()))
            i += 4


    def save_window():
        def save_data():
            data = h5py.File(directory + save_name.get(), 'w-')

            for keys, values in setting.items():
                data.create_dataset(keys, data=values)
            data.close()
            save_win.destroy()
            return None

        setting = {}
        i=0
        for gen_name, gen in allGens.items():
            setting.update({gen_name + ' status': SC_entry_set[i * 4].get()})
            setting.update({gen_name + ' frequency': SC_entry_set[i * 4 + 1].get()})
            setting.update({gen_name + ' power': SC_entry_set[i * 4 + 2].get()})
            setting.update({gen_name + ' refernce': SC_entry_set[i * 4 + 3].get()})
            i+=1

        save_win = tk.Toplevel()
        save_win.geometry('250x100+500+300')
        save_win.title('Filename')

        tk.Label(save_win, text='Dear Hatlab, what is the filename?').grid(row=0, column=0, columnspan=5)
        save_name = tk.Entry(save_win, width=20)
        save_name.grid(row=1, column=0, columnspan=5)
        tk.Button(save_win, text='Save', command=save_data, bg='white').grid(row=2, column=2)
        return

    def save_setting():
        save_window()
        return

    def load_window():
        def load_data():
            filename = tkFileDialog.askopenfilename(initialdir=directory, title="Select file",
                                                    filetypes=(("All files", "*.*"), ("all files", "*.*")))
            load_name.delete(0, tk.END)
            load_name.insert(0, filename)
            setting = {}
            i=0
            for gen_name, gen in allGens.items():
                setting.update({gen_name + ' status': SC_entry_set[i * 4]})
                setting.update({gen_name + ' frequency': SC_entry_set[i * 4 + 1]})
                setting.update({gen_name + ' power': SC_entry_set[i * 4 + 2]})
                setting.update({gen_name + ' refernce': SC_entry_set[i * 4 + 3]})
                i += 1

            try:
                data = h5py.File(load_name.get(), 'r')
                for keys in data.keys():
                    try:
                        setting[keys].delete(0, tk.END)
                        setting[keys].insert(0, data[keys][()])
                    except:
                        raise
            except IOError:
                wrong_window("Sorry, there is no original setting")
            data.close()
            set_all_value()
            load_win.destroy()
            return

        load_win = tk.Toplevel()
        load_win.geometry('300x100+500+300')
        load_win.title('Load File')

        tk.Label(load_win, text='Dear Hatlab, what setting you want to load?').grid(row=0, column=0, columnspan=5)
        load_name = tk.Entry(load_win, width=20)
        load_name.grid(row=1, column=0, columnspan=5)
        tk.Button(load_win, text='Browse and Load', command=load_data, bg='white').grid(row=2, column=2)
        return

    def load_setting():
        load_window()
        return


    row_num = 0
    Cooldown_date_label = tk.Label(temp, text=' Cooldown Date(YYYYMMDD)  :')
    Cooldown_date_label.grid(row=row_num, column=0, columnspan=2)
    tk.Label(temp, text=fridge_date, width=20).grid(row=row_num, column=2, columnspan=2)
    Save_date_label = tk.Label(temp, text='  Save Date  :  ')
    Save_date_label.grid(row=row_num, column=4, columnspan=2)
    tk.Label(temp, text=save_date, width=20).grid(row=row_num, column=6, columnspan=2)
    row_num += 1

    SigCore_keys = []
    SigCore_units = []
    for i, gen_name in enumerate(allGens.keys()):
        temp_list1 = [gen_name + ' status: ', 'Frequency', 'Power: ', 'Ref: ']
        SigCore_keys += temp_list1
        temp_units1 = ['0/1', 'GHz', 'dBm', '0/1 (0:Internal, 1:External)']
        SigCore_units += temp_units1
    SC_label_set, SC_entry_set, SC_unit_set = advanced_input_label(temp, SigCore_keys, SigCore_units, row_init=row_num,
                                                                   grid=(len(allGens), 4), width=16)


    for i in range(len(allGens)):
       tk.Button(temp, text = 'Get', width = 8, command = partial(get_one_gen, i), bg = "#FFF661").grid(row = 1 + i, column = 12)
       tk.Button(temp, text = 'Set', width = 8, command = partial(set_one_gen, i), bg = '#61EF94').grid(row = 1 + i, column = 13)


    row_num += len(allGens)

    tk.Button(temp, text='Get All', command=get_all_value, width=15, bg="#FFA959").grid(row=row_num, column=2,                                                                                       columnspan=2)
    tk.Button(temp, text='Set All', command=set_all_value, width=15, bg="#6FBEFB").grid(row=row_num, column=6,                                                                                     columnspan=2)
    row_num += 1
    tk.Button(temp, text='Save Setting', command=save_setting, width=15, bg='#FD5051').grid(row=row_num, column=2,                                                                                     columnspan=2)
    tk.Button(temp, text='Load Setting', command=load_setting, width=15, bg='#9063E9').grid(row=row_num, column=6,                                                                                           columnspan=2)
    row_num += 1

    get_all_value()

    temp.mainloop()



if __name__ == '__main__':
    params = {'fridge_date': '20201224',
              'save_date': datetime.date.today().strftime('%Y%m%d')}
    cli = Client()
    SigCore_window(params, cli)
