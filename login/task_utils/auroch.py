import os
import shutil
import glob, gzip
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
        

def handle_auroch_input(input, outdir, log):
    final_path = outdir
    if ',' in input : #处理多个文件
        if input.endswith('pod5'):
            log.logger.info('开始准备多个Pod5')
            for pod5 in input.split(','):
                if pod5.endswith('.pod5'):
                    shutil.move(f'{DATADIR}/{pod5.strip()}', outdir)
                    
        elif input.endswith('fastq') or input.endswith('fastq.gz'):
            log.logger.info('开始准备多个Fastq')
            final_path = os.path.join(outdir, 'merged.fastq') 
            with open(final_path, 'wb') as outfile:
                for path in input.split(','):
                    path = path.strip()
                    log.logger.info(f'合并{path}')
                    full_path = f'{DATADIR}/{path}'
                    if path.endswith('.gz'):
                        with gzip.open(full_path, 'rb') as infile:
                            outfile.write(infile.read())
                    else:
                        with open(full_path, 'rb') as infile:
                            outfile.write(infile.read())
        else:
            raise Exception(f"输入多个文件时，仅支持Pod5/Fastq/Fastq，请检查输入：{input}")
    else:  #处理单个文件
        log.logger.info('开始处理单个文件')
        if input.endswith('zip'):
            log.logger.info(f"开始解压并合并Zip文件")
            extract_pod5(f'{DATADIR}/{input}', outdir, log)
        elif input.endswith('pod5'):
            shutil.move(os.path.join(DATADIR, input), outdir)
            final_path = os.path.join(outdir)
        elif input.endswith('fastq'):
            shutil.move(os.path.join(DATADIR, input), outdir)
            final_path = os.path.join(outdir, input)
        elif input.endswith('fastq.gz'):
            final_path = os.path.join(outdir, input.replace('fastq.gz','fastq'))
            from_path = os.path.join(DATADIR, input)
            with open(final_path, 'wb') as outfile:
                with gzip.open(from_path, 'rb') as infile:
                    outfile.write(infile.read())
        else:
            raise Exception('输入文件格式必须为Pod5/Zip/Fastq.')
    return final_path

def write_config(para, out, bool_key_list = ['generateConsensus']):
    from AurochOnline.settings import AUROCH_TEST_INFO_PATH, AUROCH_REF_DICT
    for key in bool_key_list:
        if para.get(key) in ['true', 'false']:
            para[key] = para[key] == 'true'
            
    if para['referenceSequence'] in AUROCH_REF_DICT.keys():
        shortname = para['referenceSequence']
        para['referenceSequence'] = AUROCH_REF_DICT[shortname]
        
    with open(out, 'w') as config_file:
        config_file.write(f'name={para['sampleName']}\n')
        config_file.write(f'ref={para['referenceSequence']}\n')
        config_file.write(f'fq={para['inputFile']}\n')
        config_file.write(f'testInfo={AUROCH_TEST_INFO_PATH}\n')
        config_file.write(f'minL={para['minL']}\n')
        config_file.write(f'minQ={para['minQ']}\n')
        config_file.write(f'consense={para['generateConsensus']}\n')
        if para.get('basecallModels'):
            config_file.write(f'model={para['basecallModels']}\n')
            
