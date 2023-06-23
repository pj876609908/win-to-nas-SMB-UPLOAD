import os
import shutil
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
# 源文件夹和目标文件夹路径
source_folder = r"I:\test"
destination_folder = r"\\10.0.0.125\Movie"
# 文件监控事件处理类
class MyHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        # 如果是文件夹事件，不做处理
        if event.is_directory:
            return
        # 如果是创建或修改事件
        if event.event_type in ['created', 'modified']:
            # 判断源文件夹中的视频文件是否与目标文件夹中的视频文件相同
            if is_video_files_different():
                # 如果不同，则执行文件复制的代码
                copy_files()
# 判断源文件夹中的视频文件是否与目标文件夹中的视频文件相同
def is_video_files_different():
    source_files = set(os.listdir(source_folder))
    destination_files = set(os.listdir(destination_folder))
    # 取两个文件夹中视频文件的交集，判断是否相同
    return source_files.intersection(destination_files) != destination_files
# 复制源文件夹中新添加的视频文件到目标文件夹中
def copy_files():
    # 获取源文件夹中的所有视频文件
    video_files = [f for f in os.listdir(source_folder) if f.endswith('.mp4')]
    # 如果没有视频文件，直接返回
    if not video_files:
        return
    # 记录日志
    logging.info('Start copying files...')
    try:
        # 遍历所有视频文件，逐个复制到目标文件夹中
        for i, file in enumerate(video_files):
            # 获取源文件和目标文件的完整路径
            src_path = os.path.join(source_folder, file)
            dst_path = os.path.join(destination_folder, file)
            # 使用shutil库复制文件
            shutil.copy2(src_path, dst_path)
            # 记录日志
            logging.info(f'{i + 1}/{len(video_files)} {file} has been copied.')
    except Exception as e:
        # 记录错误日志
        logging.error(f'Error occurred while copying files: {e}')
# 监控源文件夹变化并执行相应操作
def watch_folder():
    observer = Observer()
    event_handler = MyHandler()
    observer.schedule(event_handler, source_folder, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
# 程序入口
if __name__ == '__main__':
    # 配置日志文件
    logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # 启动文件监控进程
    watch_folder()