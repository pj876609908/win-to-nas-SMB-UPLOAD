import time
import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from smb.SMBConnection import SMBConnection
# 设置本地视频文件夹和NAS共享盘的路径
video_folder = "I:\JianpianDownload"
share_folder = "\\10.0.0.125\Movie"
# 设置SMB连接的参数
smb_username = "p"
smb_password = "2020"
smb_server_name = "IMOU-SN1"
smb_server_ip = "10.0.0.125"
smb_domain = "WORKGROUP"
# 建立SMB连接
conn = SMBConnection(smb_username, smb_password, "python", smb_server_name, use_ntlm_v2=True)
conn.connect(smb_server_ip, 445)
# 将本地视频文件夹中的所有文件上传到NAS共享盘
def upload_videos():
    for file_name in os.listdir(video_folder):
        file_path = os.path.join(video_folder, file_name)
        if os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                conn.storeFile(share_folder, file_name, f)
# 监控本地视频文件夹的变化，变化后上传新的视频文件到NAS共享盘
class VideoHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        print(f"Detected new video: {event.src_path}")
        time.sleep(1)  # 等待1秒，确保文件已经完全写入磁盘
        upload_videos()
    def on_modified(self, event):
        if event.is_directory:
            return
        print(f"Detected modified video: {event.src_path}")
        time.sleep(1)  # 等待1秒，确保文件已经完全写入磁盘
        upload_videos()
# 启动文件监控器
event_handler = VideoHandler()
observer = Observer()
observer.schedule(event_handler, video_folder, recursive=True)
observer.start()
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()