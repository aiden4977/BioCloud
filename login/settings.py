TASK_TEMPLATES = {
    'pod5_plotter': {
        'name': 'Pod5 Plotter分析',
        'template': 'tasks/submit_pod5_plotter.html',
        'description': 'Pod5文件分析与绘图',
        'category': 'analysis',
        'icon': 'el-icon-s-data',
        'api_url': '/login/api/pod5_plotter/',
        'view_url': '/login/view_job/',
        'result_url': '/login/result/',
        'input_type': ['pod5'],
        'output_type': ['png', 'pdf', 'pod5'],
        'parameters': {
            'workflow': {
                'type': 'select',
                'options': ['merge and plot', 'merge', 'plot'],
                'default': 'merge and plot',
                'required': True
            },
            'filter': {
                'type': 'boolean',
                'default': False,
                'required': True
            },
            'filter_time': {
                'type': 'float',
                'default': 0.1,
                'required': False
            }
        }
    },
    'map256': {
        'name': 'Map256评估',
        'template': 'tasks/submit_map256.html',
        'description': 'Map256蛋白质评估分析',
        'category': 'analysis',
        'icon': 'el-icon-s-data',
        'api_url': '/login/api/map256/',
        'view_url': '/login/view_job/',
        'result_url': '/login/result/',
        'input_type': ['zip'],
        'input_description': '请上传zip压缩包，内部需包含1个pod5文件和相关png图片文件',
        'output_type': ['txt', 'png', 'pdf'],
        'parameters': {
            'model': {
                'type': 'select',
                'options': [
                    'Map256polyT_NP6217_MA4.0',
                    'Map256_NP627_34_MA3.0',
                    'Map256_NP627_28_MA3.0',
                    'Map256_NP6217_MA3.0',
                    'Map256_NP6217_MA2.0',
                    'Map256_NP32_MA1.0'
                ],
                'default': 'Map256polyT_NP6217_MA4.0',
                'required': True
            }
        }
    },
} 