import os
import shutil
import glob     
from AurochOnline.settings import  DATADIR     

def move_pod5_files(source_directory):
    for root, dirs, files in os.walk(source_directory):
        for file in files:
            if file.endswith('.pod5') and not root == source_directory:
                source_path = os.path.join(root, file)
                destination_path = os.path.join(source_directory, file)
                shutil.move(source_path, destination_path)
                print(root)
                print(f"Moved {source_path} to {destination_path}")
                
def extract_pod5(path, outdir, log):
    import zipfile
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(f'{outdir}/')
        move_pod5_files(f'{outdir}/')
    pod5_files = glob.glob(f'{outdir}/*pod5')                        
    log.logger.info(f"解压识别到{len(pod5_files)}个Pod5")
       
def handle_pod5ploter_input(input, outdir, log):
    final_path = outdir
    if ',' in input:
        log.logger.info('开始准备Pod5')
        for pod5 in input.split(','):
            if pod5.endswith('.pod5'):
                shutil.move(f'{DATADIR}/{pod5.strip()}', outdir)
    elif input.endswith('zip'):
        log.logger.info(f"开始解压并合并Zip文件")
        extract_pod5(f'{DATADIR}/{input}', outdir, log)
    elif input.endswith('pod5') :
        shutil.move(os.path.join(DATADIR, input), outdir)
    else:
        raise Exception('输入文件格式必须为Pod5/Zip')
    log.logger.info(f"Pod5文件就绪")
    return final_path
