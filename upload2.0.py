import os
import time
import shutil
import logging
import subprocess
import math
from tqdm import tqdm
from smb.SMBConnection import SMBConnection
from watchdog.observers import Observer
# 配置日志输出
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger()
# SMB 连接配置
smb_server_ip = "10.0.0.125"
smb_share_name = "Movie"
smb_username = "p"
smb_password = "2020"
smb_conn = SMBConnection(smb_username, smb_password, "client", "nas", use_ntlm_v2=True)
smb_conn.connect(smb_server_ip)
# 添加访问成功提示
logger.info(f"成功连接到 SMB 服务器 {smb_server_ip} 的共享文件夹 {smb_share_name}")
# 本地目录
local_path = r"I:\test"
files = os.listdir(local_path)

def get_file_size(file_path):
    """获取文件大小"""
    return os.path.getsize(file_path)
def get_file_extension(file_path):
    """获取文件扩展名"""
    return os.path.splitext(file_path)[1][1:].lower()
def upload_file(local_file_path, remote_file_path):
    """上传文件"""
    with open(local_file_path, "rb") as f:
        file_size = get_file_size(local_file_path)
        logger.info(f"开始上传文件 {local_file_path}，大小为 {file_size} 字节")
        smb_file = smb_conn.createFile(smb_share_name, remote_file_path, "w+b")
        offset = 0
        chunk_size = 8192
        with tqdm(total=file_size, unit="B", unit_scale=True, desc=local_file_path) as pbar:
            while offset < file_size:
                chunk = f.read(chunk_size)
                smb_file.write(chunk)
                offset += chunk_size
                pbar.update(chunk_size)
        smb_file.close()
        logger.info(f"文件 {local_file_path} 上传完成")
class FileEventHandler:
    """文件事件处理器"""
    def on_created(self, event):
        """当文件被创建时调用"""
        if event.is_directory:
            # 新建目录
            logger.info(f"新建目录 {event.src_path}")
        else:
            # 新建文件
            logger.info(f"检测到新文件 {event.src_path}")
            # 获取文件扩展名
            file_ext = get_file_extension(event.src_path)
            if file_ext in ["mp4", "avi", "mkv", "mov", "wmv"]:
                # 拼接远程文件路径
                local_filename = os.path.basename(event.src_path)
                remote_filename = local_filename
                remote_file_path = os.path.join(smb_share_name, remote_filename)
                # 检查远程文件是否存在
                try:
                    smb_file = smb_conn.retrieveFile(smb_share_name, remote_file_path)
                    smb_file.close()
                    logger.info(f"文件 {local_filename} 已存在于远程目录，不进行上传")
                except:
                    # 上传文件
                    try:
                        upload_file(event.src_path, remote_file_path)
                        # 上传成功后删除本地文件
                        os.remove(event.src_path)
                        logger.info(f"本地文件 {event.src_path} 删除成功")
                    except Exception as e:
                        logger.error(f"文件 {event.src_path} 上传失败：{e}")
            else:
                logger.info(f"文件 {event.src_path} 不是视频文件，不进行上传")
if __name__ == "__main__":
    # 监听本地目录
    event_handler = FileEventHandler()
    observer = Observer()
    observer.schedule(event_handler, local_path, recursive=True)
    observer.start()
    logger.info(f"开始监听本地目录 {local_path}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    # 断开 SMB 连接
    smb_conn.close()
    logger.info("SMB 连接已断开")
