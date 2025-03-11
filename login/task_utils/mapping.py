import glob
import os
import subprocess
import shutil
from AurochOnline.settings import  DATADIR
import sys

def extract_zip(path, outdir,log):
    import zipfile
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(f'{outdir}/')
    try:
        pod5_files = glob.glob(f'{outdir}/*fq')
        if len(pod5_files):
            log.logger.info(f"解压识别到{len(pod5_files)}个fq")
        else:
            os.system(f'mv {outdir}/*/*fq {outdir}/')
    except:
        try:
            os.system(f'mv {outdir}/*/*/*fq {outdir}/')
        except:
            log.logger.error(f"错误：压缩包中未找到fq")
            sys.exit(0)
            
def merge_fastq(path):
        subprocess.run([f'cat {path}/*fq >>{path}/merged.final.fastq'], 
                                shell=True,
                                cwd=path, 
                                capture_output=True, 
                                text=True)
        subprocess.run([f'cat {path}/*fastq >>{path}/merged.final.fastq'], 
                            shell=True,
                            cwd=path, 
                            capture_output=True, 
                            text=True)
        # subprocess.run([f'rm $(ls {path}*fastq | grep -v merged.final.fastq)'], 
        #                     shell=True,
        #                     cwd=path, 
        #                     capture_output=True, 
        #                     text=True)
        
def handle_mapping_input(input, outdir,merge, log):
    '''
    将用户输入的Fastq文件放入工作目录下的input文件夹，随后合并
    '''
    final_path = outdir
    print()
    #多个Fastq
    if len(input) > 1:
        log.logger.info('开始准备Fastq')
        for file in input:
            if file.endswith('.fastq') or file.endswith('fq') or file.endswith('gz') or file.endswith('fasta') or file.endswith('fa'):
                shutil.move(f'{file}', outdir)
    else:
        input = input[0]
        #单个压缩包
        #log.logger.info(f"{input},haha")
        if input.endswith('zip'):
            log.logger.info(f"开始解压Zip文件")
            extract_zip(f'{DATADIR}/{input}', outdir, log)
        #单个Fastq
        elif input.endswith('fastq') or input.endswith('fq') or input.endswith('gz') or input.endswith('fasta') or input.endswith('fa'):
            final_path = os.path.join(DATADIR, input)
            shutil.move(final_path, outdir)
            log.logger.info(f"start")
        else:
            log.logger.info(f"输入数据有误，请检查文件名")
    if merge == 'true':
        merge_fastq(outdir)
        
def handle_drug_paired_input(parameters, file_path, log):
    '''
    将用户输入的Fastq文件放入工作目录下的input文件夹，随后合并
    '''
    if ',' in parameters['input_file']:
        input_file_list = parameters['input_file'].split(',')
        
    elif isinstance(parameters['input_file'], list):
        input_file_list = parameters['input_file']
        
    else:
        log.logger.info(f'{parameters['input_file']}')
        log.logger.info(f'{type(parameters['input_file'])}')
        raise Exception('输入错误：双端模式需要多个配对Fastq')
    
    to_match_list = []
    for input_file in input_file_list:
        if '_1' in input_file:
            to_match_list.append([os.path.basename(input_file).replace('_1',''),
                                    input_file,
                                    input_file.replace('_1','_2')])
        elif '_2' in input_file:
            pass
        else:
            raise Exception(f'输入错误：{input_file}匹配失败，请检查文件名')
    with open(file_path, 'w') as f:
        for name, match, to_match in to_match_list:
            if to_match in input_file_list:
                f.write(f'{name}\t{match}\t{to_match}\n')
                continue
            raise Exception(f'输入错误：{match}缺少配对文件{to_match}')

        
def handle_input_list(fastq_dir, file_path, log):
    f = open(file_path,'w')
    #print(f"{file_path}已创建")
    log.logger.info(f"{file_path}已创建")
    for path in glob.glob(f'{fastq_dir}/*fastq'):
        basename = os.path.basename(path).split('.')[0]
        f.write(f'{basename}\t{path}\n')
    for path in glob.glob(f'{fastq_dir}/*fq'):
        basename = os.path.basename(path).split('.')[0]
        f.write(f'{basename}\t{path}\n')
    for path in glob.glob(f'{fastq_dir}/*gz'):
        basename = os.path.basename(path).split('.')[0]
        f.write(f'{basename}\t{path}\n')
    for path in glob.glob(f'{fastq_dir}/*fasta'):
        basename = os.path.basename(path).split('.')[0]
        f.write(f'{basename}\t{path}\n')
    for path in glob.glob(f'{fastq_dir}/*fa'):
        basename = os.path.basename(path).split('.')[0]
        f.write(f'{basename}\t{path}\n')
    f.close()
        