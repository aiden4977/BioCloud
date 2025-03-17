def generate_random_string(length=4):
    """生成指定长度的随机字符串"""
    import random
    import string
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def handle_map256_input(input_files, outdir, log):
    """处理Map256评估的输入文件
    
    Args:
        input_files: 输入文件路径列表
        outdir: 输出目录
        log: 日志对象
    
    Returns:
        处理后的输入文件路径列表
    """
    import shutil
    import os
    
    processed_files = []
    for file_path in input_files:
        if not os.path.exists(file_path):
            log.logger.error(f'文件不存在: {file_path}')
            continue
            
        # 移动文件到工作目录
        filename = os.path.basename(file_path)
        new_path = os.path.join(outdir, filename)
        shutil.copy2(file_path, new_path)
        processed_files.append(new_path)
        log.logger.info(f'已复制文件: {filename}')
    
    return processed_files

