import pandas as pd

# 创建示例数据
data = {
    'path': ['/path/to/file1'],
    'ref': ['/path/to/ref1'],
    'chr': ['map256']
}

# 创建DataFrame
df = pd.DataFrame(data)

# 显示表格
print("HTML格式的表格：")
print(df.to_html())

print("\n普通表格显示：")
print(df) 