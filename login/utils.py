def generate_random_string(length=4):
    """生成指定长度的随机字符串"""
    import random
    import string
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))