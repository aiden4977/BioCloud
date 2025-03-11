import os
import json
import shutil
import traceback
import glob
import subprocess
import numpy as np
from celery import shared_task
from .logger import LoggerTest
from .utils import generate_random_string
from .task_utils.mapping import handle_mapping_input, handle_input_list, handle_drug_paired_input
from .task_utils.auroch import handle_auroch_input, extract_pod5, write_config
from .task_utils.pod5_ploter import handle_pod5ploter_input
from AurochOnline.settings import POD5_BIN_PATH, PYTHON_BIN, DATADIR, POD5_PLOTER_PATH, POD5_PYTHON
from .models import JobUniversal

#2024-11-14
# @shared_task
# def running_tasks_count():
#     """
#     返回当前正在运行的任务数量
#     """
#     #return len(running_tasks)
#     return 4


@shared_task
def execute_auroch(id):
    from AurochOnline.settings import AUROCH_BIN_PATH
    import ast
    job = JobUniversal.objects.get(id=id)
    print(f'接收到{id}')
    job.status = 'running'
    job.save()

    work_dir = job.workDir
    work_input_dir = f'{work_dir}/input/'
    parameters = ast.literal_eval(job.parameters)
    
    try:
        #mkdir
        resubmit = os.path.exists(work_input_dir)
        os.makedirs(work_dir, exist_ok=True)
        os.makedirs(work_input_dir, exist_ok=True)
        print(f"Directory {work_dir} created.",parameters)
        log = LoggerTest('Auroch',f'{work_dir}/log')
        
        #handle pod5
        log.logger.info(f'正在准备输入文件{work_dir}')
        log.logger.info(f'{parameters},{type(parameters)}')
        if not resubmit:
            parameters['inputFile'] = handle_auroch_input(input = parameters['inputFile'], 
                                                outdir = work_input_dir,
                                                log = log)
                
        #write in config
        log.logger.info(f'正在设置运行参数')
        write_config(para = parameters, 
                    out = f'{work_dir}/config.txt')
        log.logger.info(f'{parameters}')
        
        #run
        log.logger.info(f'显卡已准备')

        
        log.logger.info(f'开始Auroch')
        result = subprocess.run([f'{AUROCH_BIN_PATH} config.txt >>log 2>>log'], 
                                shell=True,
                                cwd=work_dir, 
                                capture_output=True, 
                                text=True)
       
        
        #update status
        if result.returncode == 0:
            job.status = 'success'
            log.logger.info(f'Auroch运行完成')
        else:
            job.status = 'failed'
            log.logger.info(f'Auroch失败\n{result.stderr}')
            
    except Exception as e:
        log.logger.error(traceback.format_exc())
        log.logger.error(f'Auroch已停止:{e}')
        job.status = 'failed'

    job.save()


@shared_task
def execute_pod5_plotter(id):
    job = JobUniversal.objects.get(id=id)
    print(f'接收到{id}')
    job.status = 'running'
    job.save()
    
    parameters = json.loads(job.parameters)
    sampleName = job.sampleName
    work_dir = job.workDir
    work_input_dir = f'{work_dir}/input/'
    try:
        #mkdir
        os.makedirs(work_dir, exist_ok=True)
        os.makedirs(f'{work_input_dir}', exist_ok=True)
        os.makedirs(f'{work_dir}/result_{sampleName}', exist_ok=True)
        log = LoggerTest('pod5_plotter',f'{work_dir}/log')
        
        #move pod5
        input_pod5_list = handle_pod5ploter_input(
            parameters['pod5File'],
            outdir = work_input_dir,
            log = log)
                
        input_command = f'--inDir {work_input_dir}'
        output_command = f'--outDir {work_dir}/result_{sampleName}'
        min_Len_command = f'--minLen {np.float64(parameters['filter']) * 5000}' if parameters['filter'] else f'--minLen 1'
        #run
        if parameters['Workflow'] == 'merge' or parameters['Workflow'] == 'merge and plot':
            pod5_list = glob.glob(f'{work_input_dir}/*pod5')
            if  len(pod5_list) == 1:
                os.system(f'cp {pod5_list[0]} {work_dir}/result_{sampleName}/{sampleName}.pod5')
                log.logger.info(f"Pod5文件数量为1，跳过合并")
            else:
                log.logger.info(f"输入路径为{input_pod5_list}")
                result = subprocess.run([f'{POD5_BIN_PATH} merge {input_pod5_list} -o {work_dir}/result_{sampleName}/{sampleName}.pod5 >>log 2>>log'], 
                                        shell=True,
                                        cwd=work_dir, 
                                        capture_output=True, 
                                        text=True)
                log.logger.info(f"{len(pod5_list)}个Pod5文件合并完成")
            input_command = f'--inFiles {work_dir}/result_{sampleName}/{sampleName}.pod5'
        
        if parameters['Workflow'] == 'plot' or parameters['Workflow'] == 'merge and plot':
            result = subprocess.run([f'{POD5_PYTHON} {POD5_PLOTER_PATH} {input_command} {min_Len_command} {output_command} >>log 2>>log'], 
                                    shell=True,
                                    cwd=work_dir, 
                                    capture_output=True, 
                                    text=True)
            log.logger.info(f"任务结束")
        #job.log = result.stdout
        
        #update status
        if result.returncode == 0:
            job.status = 'success'
            print('job.status = success')
        else:
            job.status = 'failed'
            print('job.status = failed')
            print(f"\nError: {result.stderr}")
        
    except Exception as e:
        print(f'shared_task错误:{e}')
        job.status = 'failed'

    job.save()

@shared_task
def execute_covid(id):
    import json
    import shutil
    job = JobUniversal.objects.get(id=id)
    print(f'接收到{id}')
    job.status = 'running'
    job.save()
    from AurochOnline.settings import PYTHON_BIN, COVID19_PATH
    
    parameters = json.loads(job.parameters)
    sampleName = job.sampleName
    workDir = job.workDir
    fullLen = parameters['fullLen']
    inputFile = parameters['inputFile']
    minQ = parameters['minQ']
    minL = parameters['minL']
    try:
        #mkdir
        os.makedirs(workDir, exist_ok=True)
        os.makedirs(f'{workDir}/input/', exist_ok=True)
        os.makedirs(f'{workDir}/result/', exist_ok=True)
        print(f"Directory {workDir} created.")
        
        #move fastq and write file list
        f = open(f'{workDir}/result/info.txt','w')
        basename_list = []
        for path in inputFile:
            #remove duplicate name
            basename,file_type = os.path.splitext(os.path.basename(path))
            if basename in basename_list:
                random_code = generate_random_string(4)
                basename = f'{basename}_{random_code}'
            basename_list.append(basename)
            
            shutil.move(path, f'{workDir}/input/')
            f.write(f'{basename}\t{workDir}/input/{basename}{file_type}\n')
        f.close()
        
        length_type = 'complete' if fullLen == 'true' else 'part'
        is_fasta = '' if inputFile[0].endswith(('fastq', 'fq', 'fastq.gz', 'fq.gz')) else '-f'
        input_command = f'{workDir}/result/ -b --type {length_type} {is_fasta} -q {minQ} -l {minL}'
        
        #run
        print(f'{PYTHON_BIN} {COVID19_PATH} {input_command}>>log 2>>log')
        result = subprocess.run([f'{PYTHON_BIN} {COVID19_PATH} {input_command} >>log 2>>log'], 
                                shell=True,
                                cwd=workDir, 
                                capture_output=True, 
                                text=True)
        
        #update status
        report_path = f'{workDir}/result/10.Report/Covid19_Report.html'
        if result.returncode == 0 and os.path.exists(report_path):
            shutil.copy(report_path, f'{workDir}/Covid_Report.html')
            job.status = 'success'
            print('job.status = success')
        else:
            job.status = 'failed'
            print('job.status = failed')
            print(f"\nError: {result.stderr}")
        
    except Exception as e:
        print(f'shared_task错误:{e}')
        job.status = 'failed'

    job.save()

@shared_task
def mkdir(id):
    pwd='/home/aiden/workdir/01.django_project/xiaoqi_library_system/WORKDIR'
    path = os.path.join(pwd,str(id))
    os.makedirs(path,exist_ok=True)
    return 1

@shared_task
def execute_mapping(id):
    from AurochOnline.settings import PYTHON_BIN, META_GENOMIC_PATH
    import ast
    job = JobUniversal.objects.get(id=id)
    print(f'接收到{id}')
    job.status = 'running'
    job.save()

    work_dir = job.workDir
    work_input_dir = f'{work_dir}/input/'
    work_result_dir = f'{work_dir}/result/'
    parameters = ast.literal_eval(job.parameters)
    try:
        #mkdir
        os.makedirs(work_dir, exist_ok=True)
        os.makedirs(work_input_dir, exist_ok=True)
        os.makedirs(work_result_dir, exist_ok=True)
        print(f"Directory {work_dir} created.",parameters)
        log = LoggerTest('Meta',f'{work_dir}/log')
        
        #handle input
        log.logger.info(f'正在准备输入文件')
        log.logger.info(f'{parameters},{type(parameters)},{bool(parameters['mergeFastq'])}')
        handle_mapping_input(input = parameters['inputFile'], 
                                outdir = work_input_dir,
                                merge = parameters['mergeFastq'],
                                log = log)
        #write file list
        log.logger.info(f'准备文件清单')
        handle_input_list(fastq_dir = work_input_dir,
                          file_path = f'{work_result_dir}/info.txt', log = log)
        
        
        input_command = f'{work_result_dir} -b -q {parameters['minQ']} -l {parameters['minL']} -a {parameters['minScore']} -s {parameters['minSimilarity']} -e {parameters['minEval']} -c 10'
        #run
        log.logger.info(f'开始病原比对流程')
        print(f'{PYTHON_BIN} {META_GENOMIC_PATH} {input_command}>>log 2>>log')
        result = subprocess.run([f'{PYTHON_BIN} {META_GENOMIC_PATH} {input_command} >>log 2>>log'], 
                                shell=True,
                                cwd=work_dir, 
                                capture_output=True, 
                                text=True)
        #update status
        if result.returncode == 0:
            job.status = 'success'
            log.logger.info(f'病原运行完成')
        else:
            job.status = 'failed'
            log.logger.info(f'病原比对失败\n{result.stderr}')
            
    except Exception as e:
        log.logger.error(traceback.format_exc())
        log.logger.error(f'病原比对已停止:{e}')
        job.status = 'failed'

    job.save()
    
@shared_task
def execute_sewage(id):
    from AurochOnline.settings import PYTHON_BIN, SEWAGE_PATH
    import ast
    job = JobUniversal.objects.get(id=id)
    print(f'接收到{id}')
    job.status = 'running'
    job.save()

    work_dir = job.workDir
    work_input_dir = f'{work_dir}/input/'
    work_result_dir = f'{work_dir}/result/'
    parameters = ast.literal_eval(job.parameters)

    try:
        #mkdir
        os.makedirs(work_dir, exist_ok=True)
        os.makedirs(work_input_dir, exist_ok=True)
        os.makedirs(work_result_dir, exist_ok=True)
        print(f"Directory {work_dir} created.",parameters)
        log = LoggerTest('Sewage',f'{work_dir}/log')
        
        #handle input
        log.logger.info(f'正在准备输入文件')
        log.logger.info(f'{parameters},{type(parameters)},{bool(parameters['mergeFastq'])}')
        handle_mapping_input(input = parameters['inputFile'], 
                                outdir = work_input_dir,
                                merge = parameters['mergeFastq'],
                                log = log)
        #write file list
        log.logger.info(f'准备文件清单')
        handle_input_list(fastq_dir = work_input_dir,
                          file_path = f'{work_result_dir}/info.txt', log = log)
        
        
        input_command = f'{work_result_dir} -b -q {parameters['minQ']} -l {parameters['minL']} -a {parameters['minScore']} -s {parameters['minSimilarity']} -e {parameters['minEval']} -c 10'
        #run
        log.logger.info(f'开始新冠污水比对流程')
        print(f'{PYTHON_BIN} {SEWAGE_PATH} {input_command}>>log 2>>log')
        result = subprocess.run([f'{PYTHON_BIN} {SEWAGE_PATH} {input_command} >>log 2>>log'], 
                                shell=True,
                                cwd=work_dir, 
                                capture_output=True, 
                                text=True)
        
        #update status
        if result.returncode == 0:
            job.status = 'success'
            log.logger.info(f'新冠污水运行完成')
        else:
            job.status = 'failed'
            log.logger.info(f'新冠污水比对失败\n{result.stderr}')
            
    except Exception as e:
        log.logger.error(traceback.format_exc())
        log.logger.error(f'新冠污水比对已停止:{e}')
        job.status = 'failed'

    job.save()

@shared_task
def execute_drugvir(id):
    from AurochOnline.settings import PYTHON_BIN, DRUGVIR_PATH
    import ast
    job = JobUniversal.objects.get(id=id)
    print(f'接收到{id}')
    job.status = 'running'
    job.save()

    work_dir = job.workDir
    work_input_dir = f'{work_dir}/input/'
    work_result_dir = f'{work_dir}/result/'
    parameters = ast.literal_eval(job.parameters)

    try:
        #mkdir
        os.makedirs(work_dir, exist_ok=True)
        os.makedirs(work_input_dir, exist_ok=True)
        os.makedirs(work_result_dir, exist_ok=True)
        print(f"Directory {work_dir} created.",parameters)
        log = LoggerTest('Drugvir',f'{work_dir}/log')
        
        #handle input
        log.logger.info(f'正在准备输入文件')
        log.logger.info(f'{parameters},{type(parameters)},{bool(parameters['mergeFastq'])}')

        if parameters['sequencing'] == 'paired-end':
            handle_drug_paired_input(parameters = parameters,
                                     file_path = f'{work_result_dir}/info.txt',
                                     log = log)


        else:
            handle_mapping_input(input = parameters['input_file'], 
                                outdir = work_input_dir,
                                merge = parameters['mergeFastq'],
                                log = log)
        #write file list
            log.logger.info(f'准备文件清单')
            handle_input_list(fastq_dir = work_input_dir,
                            file_path = f'{work_result_dir}/info.txt', log = log)
        
        amrfinder_plus = '-p' if f'{parameters['amrfinder_plus']}' == 'true' else ''

        input_command = f'{work_result_dir} -b -q {parameters['qual']} -l {parameters['length']} -a {parameters['alignmentscore']} -s {parameters['similarity']} -e {parameters['e_value']} -seq {parameters['sequencing']} -dr {parameters['drugresist_db']} -vf {parameters['virfactor_db_set']} {amrfinder_plus}'
        #run
        log.logger.info(f'开始致病菌耐药毒力比对流程')
        print(f'{PYTHON_BIN} {DRUGVIR_PATH} {input_command}>>log 2>>log')
        result = subprocess.run([f'{PYTHON_BIN} {DRUGVIR_PATH} {input_command} >>log 2>>log'], 
                                shell=True,
                                cwd=work_dir, 
                                capture_output=True, 
                                text=True)

        #update status
        report_path = f'{work_dir}/result/10.Report/Drugvir_report.html'
        if result.returncode == 0 and os.path.exists(report_path):
            shutil.copy(report_path, f'{work_dir}/Drugvir_report.html')
            job.status = 'success'
            print('job.status = success')
        else:
            job.status = 'failed'
            print('job.status = failed')
            print(f"\nError: {result.stderr}")


    except Exception as e:
        log.logger.error(traceback.format_exc())
        log.logger.error(f'致病菌耐药毒力比对已停止:{e}')
        job.status = 'failed'

    job.save()

@shared_task
def execute_map256(id):
    from AurochOnline.settings import PYTHON_BIN, MAP256_PATH
    import ast
    job = JobUniversal.objects.get(id=id)
    print(f'接收到{id}')
    job.status = 'running'
    job.save()

    work_dir = job.workDir
    work_input_dir = f'{work_dir}/input/'
    work_result_dir = f'{work_dir}/result/'
    parameters = ast.literal_eval(job.parameters)
    
    try:
        # 创建工作目录
        os.makedirs(work_dir, exist_ok=True)
        os.makedirs(work_input_dir, exist_ok=True)
        os.makedirs(work_result_dir, exist_ok=True)
        log = LoggerTest('Map256',f'{work_dir}/log')
        
        # 处理输入文件
        log.logger.info(f'正在准备输入文件')
        input_files = handle_map256_input(
            input_files=parameters['inputFile'],
            outdir=work_input_dir,
            log=log
        )
        
        # 构建命令参数
        input_command = f'--input {" ".join(input_files)}'
        output_command = f'--output {work_result_dir}'
        model_command = f'--model {parameters["model"]}' if 'model' in parameters else ''
        
        # 运行Map256评估
        log.logger.info(f'开始Map256评估')
        result = subprocess.run(
            [f'{PYTHON_BIN} {MAP256_PATH} {input_command} {output_command} {model_command} >>log 2>>log'],
            shell=True,
            cwd=work_dir,
            capture_output=True,
            text=True
        )
        
        # 更新任务状态
        if result.returncode == 0:
            job.status = 'success'
            log.logger.info(f'Map256评估完成')
        else:
            job.status = 'failed'
            log.logger.error(f'Map256评估失败\n{result.stderr}')
            
    except Exception as e:
        log.logger.error(traceback.format_exc())
        log.logger.error(f'Map256评估已停止:{e}')
        job.status = 'failed'
    
    job.save()