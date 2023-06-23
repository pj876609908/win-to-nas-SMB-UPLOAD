import os
import shutil
import time
import progressbar
# 仅复制视频文件的扩展名
video_extensions = ['.mp4', '.mkv', '.avi', '.rmvb', '.mov']
source_folder = r'I:\test'
destination_folder = r'\\10.0.0.125\Movie'
log_file = os.path.join(source_folder, 'copy_log.txt')
# 如果日志文件不存在，则创建一个新的日志文件并写入表头
if not os.path.exists(log_file):
    with open(log_file, 'w') as f:
        f.write('Copy Log\n\n')
def is_video_file(file_name):
    # 判断文件是否为视频文件，仅判断扩展名
    return os.path.splitext(file_name)[1] in video_extensions
def is_file_exists(file_path):
    # 判断文件是否存在
    return os.path.exists(file_path)
def copy_file(source_file, destination_file):
    # 复制文件，并返回复制结果和用时
    start_time = time.time()
    try:
        shutil.copy2(source_file, destination_file)
        result = 'Success'
    except Exception as e:
        result = 'Error: {}'.format(str(e))
    end_time = time.time()
    elapsed_time = end_time - start_time
    return result, elapsed_time
def add_log(log_file, content):
    # 将日志记录到文件中
    with open(log_file, 'a') as f:
        f.write(content + '\n')
def copy_files():
    # 列出源文件夹中所有视频文件
    video_files = [f for f in os.listdir(source_folder) if is_video_file(f)]
    # 遍历视频文件，逐个复制
    with progressbar.ProgressBar(max_value=len(video_files), widgets=[
        'Copying: ', progressbar.Percentage(), ' ',
        progressbar.Bar(), ' ', progressbar.ETA()
    ]) as bar:
        for i, file_name in enumerate(video_files):
            source_file = os.path.join(source_folder, file_name)
            destination_file = os.path.join(destination_folder, file_name)
            # 如果目标文件夹中已经有同名文件，则跳过该文件
            if is_file_exists(destination_file):
                add_log(log_file, 'Skipped: {} (Already exists)'.format(file_name))
                continue
            # 复制文件，并记录日志
            result, elapsed_time = copy_file(source_file, destination_file)
            if result == 'Success':
                add_log(log_file, 'Success: {} (Time: {:.2f}s)'.format(file_name, elapsed_time))
            else:
                add_log(log_file, 'Error: {} (Time: {:.2f}s)'.format(file_name, elapsed_time))
            # 更新进度条
            bar.update(i + 1)
if __name__ == '__main__':
    # 执行文件复制
    copy_files()
