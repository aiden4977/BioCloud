import logging
class LoggerTest():
    def __init__(self, loggername, logFilePath):
         self.logger = logging.getLogger(loggername)
         self.logger.setLevel(logging.DEBUG)
         self.replace_handler(logFilePath, 
                              fmt = '%(asctime)s => %(name)s * %(levelname)s : %(message)s')

    
    def replace_handler(self, logFilePath, fmt):
        """
        用于在 logger 中替换与 new_handler 类型相同的 handler。
        如果没有相同类型的 handler，则直接添加 new_handler。
        """
        new_handler = logging.FileHandler(logFilePath, 'a+')
        formatter = logging.Formatter(fmt)
        new_handler.setFormatter(formatter)
        
        # 检查是否有相同类型的 handler
        for i, handler in enumerate(self.logger.handlers):
            if isinstance(handler, type(new_handler)):
                self.logger.handlers[i] = new_handler  # 直接替换
                return
        # 如果没有找到相同类型的 handler，则添加新的 handler
        self.logger.addHandler(new_handler)