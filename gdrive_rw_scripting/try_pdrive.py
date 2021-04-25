from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
gauth = GoogleAuth()
gauth.LocalWebserverAuth()

from pydrive.drive import GoogleDrive
drive = GoogleDrive(gauth)

file = drive.CreateFile({'title': 'My Awesome File.txt'})
file.SetContentString('Hello World!') # this writes a string directly to a file
file.Upload()