import os
import PySimpleGUI as sg
import hashlib
import requests
import urllib.request
import winreg
import wget
import zipfile
import io




REG_PATH = r'SOFTWARE\labrob2013\Motion Engine'
def set_reg(name, value):
    try:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0,
                                       winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(registry_key)
        return True
    except WindowsError:
        return False


def get_reg(name):
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0,
                                       winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        return None


def uploadZip():
    mainUrl = 'https://khotlenko.ru/download/engine/build-latest.zip'
    r = requests.get(mainUrl)
    return r
    """with r, zipfile.ZipFile(io.BytesIO(r.content)) as archive:
        archive.extractall(os.path.abspath(os.curdir) + r'\engine')"""
    #archive.extractall(values['text'] + r'\engine') #



def license(): #Окно с лицензией
    def hash(self, fname, algo):
        if algo == '1':
            hash = hashlib.md()
        with open(fname) as handle: #opening the file one line at a time for memory considerations
            for line in handle:
                hash.update(line.encode(encoding = 'utf-8'))
        return(hash.hexdigest())

    url = 'https://www.khotlenko.ru/download/engine/EULA.txt'
    text = requests.get("https://www.khotlenko.ru/download/engine/EULA.txt").text
    layout = [
        [sg.Multiline(size=(80, 20), disabled=True, key='line')],
        [sg.Checkbox("Agree to the license"), sg.Submit(), sg.Cancel()]
         ]
    sg.set_options(icon='logo2.ico')
    window = sg.Window('Installer', element_justification='r', size=(620, 370)).Layout(layout).Finalize()
    window.FindElement('line').Update(text)
    while True:
        event, values = window.read()
        if event in (None, 'Exit', 'Cancel'):
            raise SystemExit
        if event == 'Submit' and values[0]:
            break
    return window


# Окно, спрашивающее о выборе updat'a.
def update(version):
    def hash(self, fname, algo):
        with open(fname) as handle:
            for line in handle:
                hash.update(line.encode(encoding='utf-8'))
        return (hash.hexdigest())
    layout =[[sg.Text("Do you want to update the version?")],[sg.Submit(), sg.Cancel()]]
    window = sg.Window('Update?', element_justification='c', size=(240, 80)).Layout(layout).Finalize()
    while True:
        event, values = window.read()
        if event in (None, 'Exit', 'Cancel'):
            values['version'] = '1'
            window.close()
            break
        if event == 'Submit':
            values['version'] = '0'
            window.close()
            break


def checkVersion(values):
    ## Следующие строки отвечают за скачивание файла и считывание версии из него.
    wget.download('https://khotlenko.ru/download/engine/build.json', 'build.json')
    with open('build.json', 'r') as f:
        data = f.readlines()
        version = ''
    for i in data:
        if 'latest' in i:
            version = i[i.find(':') + 3: len(i) - 2]
    # Следующие строки отвечаю за реестр.
    if not get_reg('version'): # если в регистре нет версии, то мы создаем версию
        set_reg('version', str(version))
        set_reg('path', str(values['text']))
        values['version'] = '0'
    else:
        if get_reg('version') == version: # Если в реестре есть запись версии, и она равна последней
            values['version'] = '1'       # то ничего не делаем, иначе обновляем версию.
        else:
            update(version)
            set_reg('version', str(version))
            set_reg('path', str(values['text']))
    os.remove('build.json')


def chose(last): #Окно с выбором компонентов
    def hash(self, fname, algo):
        with open(fname) as handle:
            for line in handle:
                hash.update(line.encode(encoding = 'utf-8'))
        return(hash.hexdigest())

    layout = [
        [sg.Checkbox("VC2015-19")],
        [sg.Text(" ", size=(42, 16))],
        [sg.InputText(default_text= r'C:\ '.strip(), key="text", size=(50, 0)),
         sg.Button(size=(16, 0), button_text="Install", key="Submit")]
    ]

    window = sg.Window('Installer', layout, size= last.size, grab_anywhere=False).Finalize()
    last.close()
    while True:
        event, values = window.read()
        if event == 'Submit' and os.path.isdir(values['text']):
            values["version"] = "0"
            checkVersion(values)
            break
        if event in (None, 'Exit', 'Cancel'):
            raise SystemExit
    return window, values


def setup(second, values, upload): #Окно установки
    url = ["https://www.khotlenko.ru/download/thirdParty/VC_redist.x86_15-19.exe"]
    def hash(self, fname, algo):
        with open(fname) as handle:
            for line in handle:
                hash.update(line.encode(encoding='utf-8'))
        return (hash.hexdigest())
    layout = [ [sg.Text("", size=(0, 9))],
               [sg.Text("Thank you for installing")],
               [sg.Text("", size=(0, 7))],
               [sg.Text("",size=(50, 0)), sg.Button("Close", size=(16, 0), key="Nope")]
    ]
    window = sg.Window('Installer', layout, size=(620, 370), grab_anywhere=False, element_justification="c").Finalize()
    second.close()
    count = 0
    for i in range(1):
        sg.OneLineProgressMeter('Progress', i + 1, 2, 'single', orientation="h")
        if values['version'] == '0' and count != 1:
            with upload, zipfile.ZipFile(io.BytesIO(upload.content)) as archive:
                archive.extractall(values['text'] + r'\engine')
            count += 1
        if values[i]:
            urllib.request.urlretrieve(url[i], values['text'] + r'\ '.strip() + str(url[i])[str(url[i]).rfind('/') + 1:])
    while True:
        event, values = window.read()
        if event == 'Nope':
            raise SystemExit
            break
        if event in (None, 'Exit'):
            raise SystemExit



def main():
    """
    Разделил программу на три фунции: экран с показом лицензии, выбор компонентов и окончание установки.
    Экран с лицензией и экран с выбором компонентов возвращяют доступ к своему окну,
    чтобы следующие программы смогли сначала создать свое окно, а сразу после
    закрыть предыдущее. Это сделано для того, чтобы переход между экранами был плавным.
    Также второе окно возвращает массив со сзначеними Checkbox.
    :return:
    """
    print("Please Wait, loading the components!")
    if get_reg('version'):
        raise SystemExit
    else:
        upload = uploadZip()
        first = license()
        second, values = chose(first)
        setup(second, values, upload)


if __name__ == "__main__":
    main()


