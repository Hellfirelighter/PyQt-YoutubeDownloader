from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication
# pip install git+https://github.com/pytube/pytube
from pytube import YouTube, Channel, Playlist
from GUI import Ui_MainWindow
import os
import sys
import subprocess

qss = """
QProgressBar:horizontal
{
    border: 1px solid #000;
    border-radius: 5px;
    text-align: center;
    padding: 2px;
    background: transparent;
}

QProgressBar::chunk:horizontal
{
    background-color: #d10000;
    border-radius: 2px;
}

QComboBox
{
    selection-background-color: #4d4d4d;
    font-weight: bold;
    border-style: solid;
    border: 1px solid #d10000;
    border-radius: 5;
    padding: 3px;
}

QComboBox:hover:hover
{
    border: 2px solid #d10000;
}

QComboBox QAbstractItemView
{
    border: 2px solid darkgray;
    selection-background-color: #4d4d4d;
}

QComboBox::drop-down
{
     subcontrol-origin: padding;
     subcontrol-position: top right;
     width: 15px;

     border-left-width: 0px;
     border-left-color: darkgray;
     border-left-style: solid;
     border-top-right-radius: 3px;
     border-bottom-right-radius: 3px;
}

QWidget
{
	background-color: #252525;
	color: #fff;
	border-color: #000000;
}

QLabel
{
	background-color: transparent;
	color: #fff;
	font-weight: bold;
	border-color: #000000;
}

QPushButton
{
	background-color: #d10000;
	color: #fff;
	font-weight: bold;
	border: 1px solid #d10000;  
	border-radius: 2px;
	padding: 5px;
}

QPushButton::hover
{
	background-color: #ad0000;
	color: #fff;
}


QPushButton::pressed
{
	background-color: #e00000;
	color: #fff;
}

QToolButton
{
	background-color: transparent;
	color: #000000;
	border-style: solid;
	border-color: #000000;
}

QToolButton::hover
{
	background-color: #d10000;
	color: #000000;
	border-radius: 15px;
	border-color: #d10000;
}

QToolButton::pressed
{
	background-color: #d10000;
	color: #000000;
	border-style: solid;
	border-width: 0px;
}

QLineEdit{
	background-color: #4d4d4d;
	color: #fff;
	font-weight: bold;
	border-style: solid;
	border-radius: 5px;
	padding: 5px;
}
"""


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.urls = []

        def extractFormats(obj):
            lst = []
            try:
                for stream in obj.streams:
                    only = ''
                    if not stream.is_progressive: only = '-only'
                    if stream.type == 'video':
                        lst.append(
                            f'{stream.type}{only}    {stream.resolution}    {stream.fps} fps    {int(stream.filesize / (1024 * 1024))} MB')
                    else:
                        lst.append(f'{stream.type}{only}    {stream.abr}    {int(stream.filesize / (1024 * 1024))} MB')
                self.ui.listFormat.addItems(lst)
            except Exception as _ex:
                # pass
                print(repr(_ex))

        def downloadUrllist(lst):
            for i, url in enumerate(lst):
                self.setWindowTitle(f'YouTube DownLoader {i+1}/{len(lst)}')                    
                yt = YouTube(url, on_progress_callback=onProgress, on_complete_callback=onComplete)
                i = self.ui.listFormat.currentIndex()
                # винести окремим потоком
                yt.streams[i].download()
            self.urls.clear()
            dlg = QtWidgets.QMessageBox.information(self, 'Done!', 'file(s) was successfully downloaded',
                                                    buttons=QtWidgets.QMessageBox.Close)

        def onPaste():
            url = self.ui.inputUrl.text()
            self.ui.listFormat.clear()
            if url.startswith('https://www.youtube.com/c'):
                c = Channel(url)
                extractFormats(c.videos[0])
                self.urls = c.video_urls
            elif url.startswith('https://www.youtube.com/playlist?list='):
                p = Playlist(url)
                extractFormats(p.videos[0])
                self.urls = p.video_urls
            else:
                yt = YouTube(url)
                extractFormats(yt)
                self.urls.append(url)

        def onStart():
            downloadUrllist(self.urls)

        def onOpen():
            subprocess.Popen(r'explorer "{dir}"'.format(dir=os.path.dirname(sys.argv[0]).replace('/', '\\')))

        def onComplete(stream, file_path):
            self.ui.progressBar.setValue(0)

        def onProgress(stream, chunk, bytes_remaining):
            size = stream.filesize
            p = int(float(abs(bytes_remaining - size) / size) * float(100))
            self.ui.progressBar.setValue(p)
            QApplication.processEvents()

        self.ui.btnStart.clicked.connect(onStart)
        self.ui.btnOpen.clicked.connect(onOpen)
        self.ui.inputUrl.textChanged.connect(onPaste)


def main():
    app = QtWidgets.QApplication(sys.argv)
    # app.setStyle('Fusion')
    app.setStyleSheet(qss)

    application = ApplicationWindow()
    application.setWindowTitle("YouTube DownLoader")

    application.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
