import json
import shutil
import os
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404
from rest_framework.response import Response # 数据库交互
from rest_framework import status,generics # 数据库交互
from django.http import JsonResponse,HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from .tasks import execute_auroch, execute_pod5_plotter, execute_covid, execute_mapping, execute_sewage, execute_drugvir, execute_map256
from .serializers import JobUniversalSerializer
import re
import logging

from AurochOnline.settings import DATADIR, WORKDIR, AUROCH_MODEL, AUROCH_MODEL_DICT, HANDLE_LOG_PATH, PY38_PYTHON

#2024-11-14
#from .tasks import running_tasks_count  # 假设tasks.py中有一个方法来获取正在运行的任务

# Create your views here.
# def login(request):
#     # print('path:', path_url)
#     if request.method == 'POST':
#         path_url = request.POST['path_url']
#         name = request.POST['name']
#         password = request.POST['password']
#         try:
#             stu = Students.objects.filter(name=name, password=password)
#         except Exception as e:
#             print(e)
#         if stu:
#             try:
#                 name = Students.objects.get(name=name, password=password)
#             except Exception as e:
#                 print(e)
#             name = request.session['name'] = {"name": name.name, "photo": str(name.photo)}
#             if path_url is not None:
#                 sign_code = request.GET.get('sign_code', '')
#                 return HttpResponseRedirect(path_url + f'?sign_code={str(sign_code)}')
#             return HttpResponseRedirect('/')
#         else:
#             msg = "账号或密码错误！！"
#             return render(request, 'login/login.html', {"msg": msg})
#     else:
#         path_url = request.GET.get('path', '/')
#         return render(request, 'login/login.html', {"path_url": path_url})


# def reginter(request):
#     if request.method == 'POST':
#         name = request.POST['name']
#         password = request.POST['password']
#         phone = request.POST['phone']
#         email = request.POST['email']
#         photo = request.FILES.get('photo')
#         try:
#             stu = Students.objects.filter(is_active=True, name=name)
#         except Exception as e:
#             print(e)
#         if stu:
#             msg = '用户已存在！'
#             return render(request, 'login/register.html', {"msg": msg})
#         else:
#             try:
#                 stu = Students.objects.create(
#                     name=name,
#                     password=password,
#                     phone=phone,
#                     email=email,
#                     photo=photo
#                 )
#             except Exception as e:
#                 print(e)
#             msg = "注册成功！"
#             return render(request, 'login/login.html', {"msg": msg})

#     return render(request, 'login/register.html')


# def pswd_update(request):
#     if request.method == "POST":
#         name = request.session['name']
#         password_1 = request.POST["password_1"]
#         password_2 = request.POST["password_1"]

#         try:
#             stu = Students.objects.get(name=name['name'])
#         except Exception as e:
#             print(e)
#         if stu.password == password_1:
#             stu.password = password_2
#             stu.save()
#             return HttpResponseRedirect("/login/")
#         else:
#             msg = "账号或密码错误！"
#             return render(request, 'login/pswd_update.html', {"msg": msg})
#     else:
#         return render(request, 'login/pswd_update.html')

# def logout(request):
#     if 'name' in request.session:
#         del request.session['name']

#     return HttpResponseRedirect('/login/')

#2024-11-14 
# from django.http import JsonResponse
# from .models import Task  # 假设 Task 模型包含任务状态字段
# def get_running_tasks_count(request):
#     # 获取状态为 "running" 的任务数量
#     running_tasks_count = Task.objects.filter(status='running').count()
#     return JsonResponse({'runningTaskCount': running_tasks_count})


def index(request):
    try:
        text = Text.objects.filter(is_active=True).order_by('time')
    except Exception as e:
        print(e)
    return render(request, 'index/index.html', {"text": text})


def view_job(request):
    currentUser = request.user.username # 拿到当前登录的用户名
    return render(request, 'admin/view_job.html',{'currentUserName': currentUser})

def view_job_detail(request, pk):
    #job = get_object_or_404(JobUniversal, pk=pk)
    return render(request, 'admin/view_job_detail.html', {'taskID': pk})

def submit_auroch(request):
    return render(request, 'tasks/submit_auroch.html')

def submit_mapping(request):
    return render(request, 'tasks/submit_mapping.html')

def submit_covid(request):
    return render(request, 'tasks/submit_covid.html')

def submit_handle_log(request):
    return render(request, 'tasks/submit_handle_log.html')

def submit_pod5_plotter(request):
    return render(request, 'tasks/submit_pod5_plotter.html')

def empty(request):
    return render(request, 'tasks/empty.html')

# 新增加
def test1(request):
    return render(request, 'tasks/test1.html')

# 新增加
def test2(request):
    return render(request, 'tasks/test2.html')

# 新增加
def submit_sewage_water(request):
    return render(request, 'tasks/submit_sewage_water.html')
# 新增加
def Endurance_toxicity_analysis(request):
    return render(request, 'tasks/Endurance_toxicity_analysis.html')
    
def read_log(request, pk):
    print(pk)
    task = get_object_or_404(JobUniversal, id=pk)
    
    file_path = task.log
    content = 'log info:'
    try:
        if not os.path.exists(file_path):
            os.system(f'touch {file_path}')
            return HttpResponse(content, content_type='text/plain')
        else:
            with open(file_path, 'r', encoding='utf-8') as file:
                file.seek(0, 2)  # 将文件指针移到文件末尾
                end_pos = file.tell()

                start_pos = max(0, end_pos - 20000)
                file.seek(start_pos)

                content = file.read()
                content = '\n'.join([content, file.read()])
            return HttpResponse(content, content_type='text/plain')
    except Exception as err:
        raise Http404(f"Permission Denied {err}")
    
def read_fastq(request):
    
    import glob
    files = glob.glob(f'{DATADIR}/*.fastq') + glob.glob(f'{DATADIR}/*.fq')
    filenames = [os.path.basename(file) for file in files]
    return JsonResponse({'fastqs': filenames})

def handle_log(request):
    if request.method == 'POST':
        try:
            import pandas as pd
            logging.info('************')
            logging.info(request)
            body = json.loads(request.body.decode('utf-8'))
            input_file = body.get('inputFile')  # 获取 inputFile 字段
            input_file = 'Output.txt'
            logging.info('************',input_file)
            #inputFile = request.data.get('inputFile')
            
            
            input = f'{DATADIR}/{input_file}'
            out = f'{WORKDIR}/handle_log/'
            os.system(f'rm -rf {WORKDIR}/handle_log/*')
            os.system(f'{PY38_PYTHON} {HANDLE_LOG_PATH} --inFiles {input} --outDirs {out}')
            os.system(f'mv {input} {out}')
            # 读取 CSV 文件为 DataFrame
            summary_json = pd.read_csv(f'{out}/result_summary.csv').to_dict(orient='records')
            result_json = pd.read_csv(f'{out}/result.csv',index_col = 0).head(1000).to_dict(orient='records')
            print(summary_json)
            # 返回 JSON 响应
            #return JsonResponse()
            return JsonResponse({'summary': summary_json,
                                  'result': result_json})
        
        #,
        except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def resubmit(request, pk):
    # try:
    job = JobUniversal.objects.get(id=pk)
    if job.workfolw == 'Auroch':
        result = execute_auroch.delay(pk)
    if job.workfolw == 'Pod5Plotter':
        result = execute_pod5_plotter.delay(pk)
    # except Exception as err:
    #     return JsonResponse({'error': f'{str(err)}'}, status=400)
    return JsonResponse({'success': f'success'}, status=200)

def read_model(request):
    logging.info('aaaa')
    import glob
    files = glob.glob(f'{AUROCH_MODEL}/20*')
    model_list = []
    for file in files:
        model_name = os.path.basename(file)
        model_lable = AUROCH_MODEL_DICT.get(model_name)
        model = {'value':model_name,
                 'label':f'{model_name}({model_lable})' }
        model_list.append(model)
    return JsonResponse({'models': model_list})
    
def generate_random_string(length=4):
    """生成指定长度的随机字符串"""
    import random
    import string
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))    

class CreateJob_Auroch(generics.ListCreateAPIView):
    queryset = JobUniversal.objects.all()
    serializer_class = JobUniversalSerializer

    
    def create(self, request):
        jobArgs = {}
        jobArgs['workdir'] = WORKDIR  # 设定workdir目录路径
        jobArgs['data'] = DATADIR  # 设定data目录路径
        jobArgs['jobName'] = 'Auroch'
        jobArgs['projectName'] = 'Test'
        jobArgs['userName'] = request.user.username # TestUser
        sampleName=request.data.get('sampleName')
        # Auroch任务参数
        auroch_param = {'sampleName': request.data.get('sampleName'), 
                        'referenceSequence': request.data.get('referenceSequence'),
                        'inputFile': request.data.get('inputFile'), 
                        'minQ': request.data.get('minQ'), 
                        'minL': request.data.get('minL'), 
                        'generateConsensus': request.data.get('generateConsensus'), 
                        'basecallModels':request.data.get('basecallModels'), 
                        }
        try:
        # 数据库通用参数
            if JobUniversal.objects.filter(sampleName=sampleName).exists():
                random_suffix = generate_random_string()
                sampleName = f"{sampleName}_{random_suffix}"
            data = {
                'sampleName': sampleName,
                'workfolw': jobArgs['jobName'],
                'workDir': os.path.join(jobArgs['workdir'], sampleName),
                'projectName': jobArgs['projectName'],
                'userName': jobArgs['userName'],
                'parameters': json.dumps(auroch_param),
                'status': 'queued',
                'log': os.path.join(jobArgs['workdir'], sampleName,'log'),
            }
            # 创建模型实例
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer) # 这个函数调用之后,就会将操作写入数据库吗?

            id = serializer.instance.id
            print(f'idw为{id}')
            result = execute_auroch.delay(id)
            
        except Exception as err:
            print(f'***Error:{err}')
                    
        headers = self.get_success_headers(serializer.data)
        print(headers)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



class CreateJob_Pod5Plotter(generics.ListCreateAPIView):
    queryset = JobUniversal.objects.all()
    serializer_class = JobUniversalSerializer

    def get_full_path(self, jobArgs, filenames):
        pod5_paths = [os.path.join(jobArgs['data'],pod5FileName.strip())
        for pod5FileName in filenames.split(',')]
        return(pod5_paths)
    
    def create(self, request):
        jobArgs = {}
        jobArgs['workdir'] = WORKDIR  # 设定workdir目录路径
        jobArgs['data'] = DATADIR  # 设定data目录路径
        jobArgs['jobName'] = 'Pod5Plotter'
        jobArgs['projectName'] = 'Test'
        jobArgs['userName'] = request.user.username # TestUser
        pod5_paths = self.get_full_path(jobArgs, request.data.get('pod5Files'))
        sampleName=request.data.get('sampleName')
        
        print(pod5_paths)
        # 构建json参数
        json_param = json.dumps({'pod5File': request.data.get('pod5Files'),
                                 'Workflow':request.data.get('workflow'),
                                 'filter': request.data.get('filter')
                                 })
        try:
            # 去重，并创建模型实例的数据字典
            if JobUniversal.objects.filter(sampleName=sampleName).exists():
                random_suffix = generate_random_string()
                sampleName = f"{sampleName}_{random_suffix}"
            data = {
                'sampleName': sampleName,
                'workfolw': jobArgs['jobName'],
                'workDir': os.path.join(jobArgs['workdir'], sampleName),
                'projectName': jobArgs['projectName'],
                'userName': jobArgs['userName'],
                'parameters': json_param,
                'status': 'queued',
                'log': os.path.join(jobArgs['workdir'], sampleName, 'log'),
            }
            # 创建模型实例
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            id = serializer.instance.id
            print(f'idw为{id}')
            result = execute_pod5_plotter.delay(id)
        except Exception as err:
            print(f'任务创建失败:{err}')
                    
        headers = self.get_success_headers(serializer.data)
        print(headers)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class CreateJob_Covid(generics.ListCreateAPIView):
    queryset = JobUniversal.objects.all()
    serializer_class = JobUniversalSerializer

    def get_full_path(self, jobArgs, filenames):
        paths = [os.path.join(jobArgs['data'],FileName.strip())
        for FileName in filenames.split(',')]
        return(paths)
    
    def create(self, request):
        jobArgs = {}
        jobArgs['workdir'] = WORKDIR  # 设定workdir目录路径
        jobArgs['data'] = DATADIR  # 设定data目录路径
        jobArgs['jobName'] = 'Covid19'
        jobArgs['projectName'] = 'Test'
        jobArgs['userName'] = request.user.username # TestUser
        sampleName = request.data.get('sampleName')
        
        # 构建json参数
        json_param = json.dumps({'inputFile': self.get_full_path(jobArgs, request.data.get('inputFile')),
                                'fullLen':request.data.get('fullLen'),
                                'minQ':request.data.get('minQ'),
                                'minL':request.data.get('minL'),
                                 })
        try:
            if JobUniversal.objects.filter(sampleName=sampleName).exists():
                random_suffix = generate_random_string()
                sampleName = f"{sampleName}_{random_suffix}"
            data = {
                'sampleName': sampleName,
                'workfolw': jobArgs['jobName'],
                'workDir': os.path.join(jobArgs['workdir'], sampleName),
                'projectName': jobArgs['projectName'],
                'userName': jobArgs['userName'],
                'parameters': json_param,
                'status': 'queued',
                'log': os.path.join(jobArgs['workdir'], sampleName, 'log'),
            }
            # 创建模型实例
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            id = serializer.instance.id
            print(f'idw为{id}')
            result = execute_covid.delay(id)
        except Exception as err:
            print(f'任务创建失败:{err}')
                    
        headers = self.get_success_headers(serializer.data)
        print(headers)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class CreateJob_Mapping(generics.ListCreateAPIView):
    queryset = JobUniversal.objects.all()
    serializer_class = JobUniversalSerializer

    def get_full_path(self, jobArgs, filenames):
        paths = [os.path.join(jobArgs['data'],FileName.strip())
        for FileName in filenames.split(',')]
        return(paths)
    
    def create(self, request):
        jobArgs = {}
        jobArgs['workdir'] = WORKDIR  # 设定workdir目录路径
        jobArgs['data'] = DATADIR  # 设定data目录路径
        jobArgs['jobName'] = '病原比对流程'
        jobArgs['projectName'] = 'Test'
        jobArgs['userName'] = request.user.username # TestUser
        sampleName = request.data.get('sampleName')
        print(f'idw为{request.data.get('mergeFastq')}')
        # 构建json参数
        json_param = json.dumps({'inputFile': self.get_full_path(jobArgs, request.data.get('inputFile')),
                                'seqType':request.data.get('seqType'),
                                'mergeFastq':request.data.get('mergeFastq'),
                                'minQ':request.data.get('minQ'),
                                'minL':request.data.get('minL'),
                                'minScore':request.data.get('minScore'),
                                'minSimilarity':request.data.get('minSimilarity'),
                                'minEval':request.data.get('minEval')
                                 })
        try:
            if JobUniversal.objects.filter(sampleName=sampleName).exists():
                random_suffix = generate_random_string()
                sampleName = f"{sampleName}_{random_suffix}"
            data = {
                'sampleName': sampleName,
                'workfolw': jobArgs['jobName'],
                'workDir': os.path.join(jobArgs['workdir'], sampleName),
                'projectName': jobArgs['projectName'],
                'userName': jobArgs['userName'],
                'parameters': json_param,
                'status': 'queued',
                'log': os.path.join(jobArgs['workdir'], sampleName, 'log'),
            }
            # 创建模型实例
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            id = serializer.instance.id
            print(f'idw为{id}')
            result = execute_mapping.delay(id)
        except Exception as err:
            print(f'任务创建失败:{err}')
                    
        headers = self.get_success_headers(serializer.data)
        print(headers)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    
class CreateJob_Sewage(generics.ListCreateAPIView):
    queryset = JobUniversal.objects.all()
    serializer_class = JobUniversalSerializer

    def get_full_path(self, jobArgs, filenames):
        paths = [os.path.join(jobArgs['data'],FileName.strip())
        for FileName in filenames.split(',')]
        return(paths)
    
    def create(self, request):
        jobArgs = {}
        jobArgs['workdir'] = WORKDIR  # 设定workdir目录路径
        jobArgs['data'] = DATADIR  # 设定data目录路径
        jobArgs['jobName'] = '污水分析流程'
        jobArgs['projectName'] = 'Test'
        jobArgs['userName'] = request.user.username # TestUser
        sampleName = request.data.get('sampleName')
        print(f'idw为{request.data.get('mergeFastq')}')
        # 构建json参数
        json_param = json.dumps({'inputFile': self.get_full_path(jobArgs, request.data.get('inputFile')),
                                'seqType':request.data.get('seqType'),
                                'mergeFastq':request.data.get('mergeFastq'),
                                'minQ':request.data.get('minQ'),
                                'minL':request.data.get('minL'),
                                'minScore':request.data.get('minScore'),
                                'minSimilarity':request.data.get('minSimilarity'),
                                'minEval':request.data.get('minEval')
                                 })
        try:
            if JobUniversal.objects.filter(sampleName=sampleName).exists():
                random_suffix = generate_random_string()
                sampleName = f"{sampleName}_{random_suffix}"
            data = {
                'sampleName': sampleName,
                'workfolw': jobArgs['jobName'],
                'workDir': os.path.join(jobArgs['workdir'], sampleName),
                'projectName': jobArgs['projectName'],
                'userName': jobArgs['userName'],
                'parameters': json_param,
                'status': 'queued',
                'log': os.path.join(jobArgs['workdir'], sampleName, 'log'),
            }
            # 创建模型实例
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            id = serializer.instance.id
            print(f'idw为{id}')
            result = execute_sewage.delay(id)
        except Exception as err:
            print(f'任务创建失败:{err}')
                    
        headers = self.get_success_headers(serializer.data)
        print(headers)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    
    
    
class CreateJob_DrugVir(generics.ListCreateAPIView):
    queryset = JobUniversal.objects.all()
    serializer_class = JobUniversalSerializer

    def get_full_path(self, jobArgs, filenames):
        try:
            paths = [os.path.join(jobArgs['data'],FileName.strip())
            for FileName in filenames.split(',')]
        except Exception:
            print(f'任务创建失败:样本名有误')
        return(paths)
    
    def create(self, request):
        jobArgs = {}
        jobArgs['workdir'] = WORKDIR  # 设定workdir目录路径
        jobArgs['data'] = DATADIR  # 设定data目录路径
        jobArgs['jobName'] = '耐药毒力分析'
        jobArgs['projectName'] = 'Test'
        jobArgs['userName'] = request.user.username # TestUser
        sampleName = request.data.get('sampleName')
        # 构建json参数
        json_param = json.dumps({'input_file': self.get_full_path(jobArgs, request.data.get('input_file')),
                        'alignmentscore': request.data.get('alignmentscore'),
                        'similarity': request.data.get('similarity'),
                        'e_value': request.data.get('e_value'),
                        'qual': request.data.get('qual'),
                        'length': request.data.get('length'),
                        'sequencing': request.data.get('sequencing'),
                        'drugresist_db': request.data.get('drugresist_db'),
                        'virfactor_db_set': request.data.get('virfactor_db_set'),
                        'amrfinder_plus': request.data.get('amrfinder_plus'),
                        'mergeFastq': request.data.get('mergeFastq')
                                 })
        try:
            if JobUniversal.objects.filter(sampleName=sampleName).exists():
                random_suffix = generate_random_string()
                sampleName = f"{sampleName}_{random_suffix}"
            data = {
                'sampleName': sampleName,
                'workfolw': jobArgs['jobName'],
                'workDir': os.path.join(jobArgs['workdir'], sampleName),
                'projectName': jobArgs['projectName'],
                'userName': jobArgs['userName'],
                'parameters': json_param,
                'status': 'queued',
                'log': os.path.join(jobArgs['workdir'], sampleName, 'log'),
            }
            # 创建模型实例
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            id = serializer.instance.id
            print(f'idw为{id}')
            result = execute_drugvir.delay(id)
        except Exception as err:
            print(f'任务创建失败:{err}')
                    
        headers = self.get_success_headers(serializer.data)
        print(headers)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    
    
class JobUniversalRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = JobUniversal.objects.all()
    serializer_class = JobUniversalSerializer
    
    def destroy(self, request, *args, **kwargs):
        primary_id = self.kwargs.get('pk')
        task = get_object_or_404(JobUniversal, id=primary_id)
        self.perform_destroy(task)
        os.system(f'rm -r {task.workDir}')
        return Response(status=status.HTTP_204_NO_CONTENT)

        
@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        if uploaded_file.name.endswith('txt'):
            uploaded_file.name = 'Output.txt'
        fs = FileSystemStorage(location=DATADIR)  # 设置文件存储路径
        if os.path.exists(f'{DATADIR}/{uploaded_file.name}'):
            os.remove(f'{DATADIR}/{uploaded_file.name}')
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_url = fs.url(filename)
        return JsonResponse({'file_url': file_url}, status=200)
    return JsonResponse({'error': 'No file uploaded'}, status=400)


def find_auroch_path(workdir):
    import glob
    replot_path = glob.glob(f'{workdir}/*/*html')
    if isinstance(replot_path,list):
        replot_path = replot_path[0]
    dir_path = replot_path.split('/')[-2]
    return(dir_path)





def serve_html(request, pk):
    # 构造 HTML 文件的完整路径
    job = JobUniversal.objects.get(id=pk)
    if job.workfolw=='Auroch':
        dirName = find_auroch_path(job.workDir)
        print(f'*%{job.workDir}/{dirName}')
        reportPath = os.path.join(job.workDir,dirName,'AurochReport.html')
    if job.workfolw=='Covid19':
        reportPath = os.path.join(job.workDir,'Covid_Report.html')
    if job.workfolw=='病原比对流程':
        reportPath = os.path.join(job.workDir,'Mapping_Report.html')
    if job.workfolw=='耐药毒力分析':
        reportPath = os.path.join(job.workDir,'Drugvir_report.html')
        
    try:
        with open(reportPath, 'r') as file:
            html_content = file.read()
        return HttpResponse(html_content, content_type='text/html')
    except FileNotFoundError:
        return HttpResponse('File not found.', status=404)

def download_zip(request, pk):
    job = JobUniversal.objects.get(id=pk)
    if job.workfolw == 'Auroch':
        dirName = find_auroch_path(job.workDir)
        reportDirPath = os.path.join(job.workDir,dirName)
        zip_file_path = os.path.join(job.workDir, 'AurochReport.zip')
        
    elif job.workfolw == 'Pod5Plotter':
        reportDirPath = os.path.join(job.workDir, f'result_{job.sampleName}')
        zip_file_path = os.path.join(job.workDir, f'result_{job.sampleName}.zip')
    
    elif job.workfolw in ['Covid19','病原比对流程','污水分析流程','耐药毒力分析']:
        reportDirPath = os.path.join(job.workDir, f'result/10.Report/')
        zip_file_path = os.path.join(job.workDir, f'result_{job.sampleName}.zip')
        
        
    # 将文件夹压缩成zip
    if not os.path.isdir(reportDirPath):
        return HttpResponse('结果文件不存在，请检查是否被移动或删除', status=404)
    if not os.path.exists(zip_file_path):
        shutil.make_archive(base_name=zip_file_path[:-4], 
                            format='zip', 
                            root_dir=reportDirPath)
    
    # 读取zip文件内容
    with open(zip_file_path, 'rb') as zip_file:
        response = HttpResponse(zip_file.read(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={job.sampleName}.zip'
    
    return response

def download_fastq(request, pk):
    job = JobUniversal.objects.get(id=pk)
    if job.workfolw == 'Auroch':
        import gzip
        dirName = find_auroch_path(job.workDir)

        reportDirPath = os.path.join(job.workDir,dirName)
        fastq_file_path = os.path.join(reportDirPath, '01.Raw/filtered.fastq')
        zip_file_path = os.path.join(reportDirPath, '01.Raw/filtered.fastq.gz')
        
    # 将文件夹压缩成zip
    if not os.path.isfile(fastq_file_path):
        return HttpResponse(f'{reportDirPath}结果文件不存在，请检查是否被移动或删除', status=404)
    if not os.path.exists(zip_file_path):
        with open(fastq_file_path, 'rb') as f_in:
            with gzip.open(zip_file_path, 'wb') as f_out:
                f_out.writelines(f_in)
    
    # 读取zip文件内容
    with open(zip_file_path, 'rb') as zip_file:
        response = HttpResponse(zip_file.read(), content_type='application/gzip')
        response['Content-Disposition'] = f'attachment; filename={job.sampleName}.fastq.gz'
    
    return response
# #2024-11-14
# def get_running_tasks_count_view(request):
#     """
#     处理API请求，返回当前正在运行的任务数
#     """
#     try:
#         # 假设tasks.py有一个get_running_tasks_count函数，它返回当前运行中的任务数
#         running_tasks_count = running_tasks_count()
        
#         # 返回JSON响应
#         return JsonResponse({'running_tasks_count': running_tasks_count}, status=200)
    
#     except Exception as e:
#         # 如果有任何错误，返回500错误和错误消息
#         return JsonResponse({'error': str(e)}, status=500)

def submit_map256(request):
    return render(request, 'tasks/submit_map256.html')

#journalctl -fxeu nanopore.test.service
class CreateJob_Map256(generics.ListCreateAPIView):
    queryset = JobUniversal.objects.all()
    serializer_class = JobUniversalSerializer
    
    def get_full_path(self, jobArgs, filenames):
        return [f'{DATADIR}/{filename}' for filename in filenames]
    
    def create(self, request):
        
        jobArgs = {}
        jobArgs['workdir'] = WORKDIR  # 设定workdir目录路径
        jobArgs['data'] = DATADIR  # 设定data目录路径
        jobArgs['jobName'] = 'Map256'
        jobArgs['projectName'] = 'Test'
        jobArgs['userName'] = request.user.username # TestUser

        sampleName=request.data.get('sampleName')
        
        # 构建json参数
        json_param = json.dumps({'pod5File': request.data.get('pod5Files'),
                                 'Workflow':request.data.get('workflow'),
                                 'filter': request.data.get('filter')
                                 })
        print('构建参数ok')
        try:
            # 去重，并创建模型实例的数据字典
            if JobUniversal.objects.filter(sampleName=sampleName).exists():
                random_suffix = generate_random_string()
                sampleName = f"{sampleName}_{random_suffix}"
            data = {
                'sampleName': sampleName,
                'workfolw': jobArgs['jobName'],
                'workDir': os.path.join(jobArgs['workdir'], sampleName),
                'projectName': jobArgs['projectName'],
                'userName': jobArgs['userName'],
                'parameters': json_param,
                'status': 'queued',
                'log': os.path.join(jobArgs['workdir'], sampleName, 'log'),
            }
            # 创建模型实例
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            id = serializer.instance.id
            print(f'任务创建成功,任务ID---->idw为{id},任务执行完成70%...')
            result = execute_map256.delay(id)
            print(f'任务创建成功,任务ID---->idw为{id},任务执行完成89%...')
        except Exception as err:
            print(f'任务创建失败:{err}')

        print(f'任务执行完成90%...')
        headers = self.get_success_headers(serializer.data)
        print('headers:',headers)
        print(f'任务执行完成99%...')
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)