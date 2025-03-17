from django.urls import path

from . import views




urlpatterns = [
    path('', views.index, name="index"),  #
    #submit job
    path('submit_auroch/', views.submit_auroch, name="submit_auroch"),
    path('submit_pod5_plotter/', views.submit_pod5_plotter, name="submit_pod5_plotter"),
    path('submit_covid/', views.submit_covid, name="submit_covid"),
    path('submit_mapping/', views.submit_mapping, name="submit_mapping"),
    path('submit_handle_log/', views.submit_handle_log, name="submit_covid"),
    path('submit_sewage_water/', views.submit_sewage_water, name="submit_sewage_water"),
    path('submit_map256/', views.submit_map256, name="submit_map256"),
    path('empty/', views.empty, name="empty"),

    #新增加
    path('test1/', views.test1, name="test1"),
    path('test2/', views.test2, name="test2"),
    path('view_job/', views.view_job, name="view_job"),
    path('view_job/<int:pk>/', views.view_job_detail, name="view_job_detail"),
    path('Endurance_toxicity_analysis/', views.Endurance_toxicity_analysis, name="Endurance_toxicity_analysis"),

    #create job
    path('api/auroch/', views.CreateJob_Auroch.as_view(), name='auroch-list-create'),
    path('api/auroch/<int:pk>/', views.JobUniversalRetrieveUpdateDestroy.as_view(), name='universial job'),
    path('api/pod5_plotter/', views.CreateJob_Pod5Plotter.as_view(), name='create pod5 job'),
    path('api/covid/', views.CreateJob_Covid.as_view(), name='create covid job'),
    path('api/mapping/', views.CreateJob_Mapping.as_view(), name='create mapping job'),
    path('api/sewage_water/', views.CreateJob_Sewage.as_view(), name='create sewage_water'),
    path('api/submit_drugvir/', views.CreateJob_DrugVir.as_view(), name="submit_drug_vir"),
    path('api/map256/', views.CreateJob_Map256.as_view(), name='create map256 job'),
    path('api/handle_log/', views.handle_log, name='create handle_logb'),
    path('api/resubmit/<int:pk>/', views.resubmit, name='rerun user job'),

    #get info
    path('getlog/<int:pk>/', views.read_log, name='read_file'),
    path('getfastq/', views.read_fastq, name='read_file'),
    path('getmodel/', views.read_model, name='read_file'),
    path('upload/', views.upload_file, name='upload_file'),
    path('getreport/<int:pk>/', views.serve_html, name='upload_file'),
    path('download_zip/<int:pk>/', views.download_zip, name='upload_file'),
    path('download_fastq/<int:pk>/', views.download_fastq, name='upload_file'),

    #2024-11-14
    #get running tasks count
    #path('api/running_tasks_count/', views.get_running_tasks_count),
    
]
