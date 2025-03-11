from bs4 import BeautifulSoup
import re
import pdfkit
import os

# 读取原始 HTML 文件
html_file_path = '/home/nanopore/01.Workdir/01.NAS/test/AurochOnline/login/templates/tasks/to_pdf/Drugvir_report.html'
with open(html_file_path, 'r', encoding='utf-8') as file:
    html_content = file.read()

# 使用 BeautifulSoup 解析 HTML
soup = BeautifulSoup(html_content, 'html.parser')

# 1) 找到表格并修改样式
table = soup.find('table', {'id': 'data-table'})
if table:
    table['style'] = table.get('style', '') + ' display: block;'  # 将 display 样式修改为 block

# 2) 找到 <script> 标签并修改内容
scripts = soup.find_all('script')
for script in scripts:
    if 'pageLength' in script.string:  # 查找包含 pageLength 的脚本
        script.string = re.sub(r'pageLength:\s*\d+', 'pageLength: 1000', script.string)

# 将修改后的 HTML 内容写回文件（永久文件）
modified_html_path = '/home/nanopore/01.Workdir/01.NAS/test/AurochOnline/login/templates/tasks/to_pdf/modified_drugvir_report.html'
with open(modified_html_path, 'w', encoding='utf-8') as file:
    file.write(str(soup))

# 生成 PDF
options = {
    'enable-local-file-access': None,
    'zoom': 1.3,
    'no-outline': None,  # 确保这也是有效的
}

pdf_output_path = '/home/nanopore/01.Workdir/01.NAS/test/AurochOnline/login/templates/tasks/to_pdf/out.pdf'
pdfkit.from_file(modified_html_path, pdf_output_path, options=options)

print(f"PDF 已成功保存到 {pdf_output_path}")

#删除modified_html_path
# 检查文件是否存在
if os.path.exists(modified_html_path):
    # 删除文件
    os.remove(modified_html_path)
    print(f"File {modified_html_path} has been deleted.")
else:
    print(f"File {modified_html_path} does not exist.")