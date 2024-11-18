from django.contrib import admin

from login.models import *

# Register your models here.


admin.site.site_title = "纳米孔数据分析系统_v2.1"
admin.site.site_header = "纳米孔数据分析系统_v2.1"
admin.site.index_title = "纳米孔数据分析系统_v2.1"


class StudentsManager(admin.ModelAdmin):
    # 列表页显示那些字段
    search_fields = ('name', 'phone')
    list_display = ['id', 'name', 'password', 'phone', 'email', 'time', 'is_active', 'admin_sample']


class BookingsManager(admin.ModelAdmin):
    # 列表页显示那些字段
    search_fields = ('students', 'number')
    list_display = ['id', 'students', 'number', 'room', 'period', 'time', 'is_active', 'admin_sample']


class RoomsManager(admin.ModelAdmin):
    # 列表页显示那些字段
    search_fields = ('name',)
    search_fields = ('name',)
    list_display = ['id', 'name', 'number', 'time', 'is_active', 'admin_sample']


class IntegralsManager(admin.ModelAdmin):
    # 列表页显示那些字段
    search_fields = ('student',)
    list_display = ['id', 'student', 'title', 'text', 'time', 'is_active', 'admin_sample']


class TextsManager(admin.ModelAdmin):
    # 列表页显示那些字段
    search_fields = ('title',)
    list_display = ['id', 'title', 'time', 'is_active']

class JobAurochManager(admin.ModelAdmin):
    # 列表页显示那些字段
    search_fields = ('arg1',)
    list_display = ('arg1', 'arg2','arg3','arg4','arg5')

class meiliUserManager(admin.ModelAdmin):
    # 列表页显示那些字段
    search_fields = ('id',)
    list_display = ('id','account', 'password')

class JobUniversalManager(admin.ModelAdmin):
    # 列表页显示那些字段
    search_fields = ('id', 'workfolw',)
    list_display = ['id', 'workfolw', 'parameters', 'sampleName', 'projectName', 'projectName', 'userName',
                    'workDir', 'status', 'log', 'created_at', 'updated_at', ]

    
admin.site.register(Students, StudentsManager)
admin.site.register(Rooms, RoomsManager)
admin.site.register(Bookings, BookingsManager)
admin.site.register(Integrals, IntegralsManager)
admin.site.register(Text, TextsManager)
admin.site.register(JobAuroch, JobAurochManager)
admin.site.register(meiliUser, meiliUserManager)
admin.site.register(JobUniversal, JobUniversalManager)