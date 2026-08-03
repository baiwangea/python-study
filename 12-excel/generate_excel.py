"""
生成带样式的Excel配置文件
包含多个工作表：API配置、请求参数、认证信息、环境配置
"""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, NamedStyle
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter


def create_styled_excel():
    wb = Workbook()

    # ========== 定义通用样式 ==========
    # 标题样式
    header_font = Font(name='微软雅黑', size=12, bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    # 数据样式
    data_font = Font(name='微软雅黑', size=11)
    data_alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)

    # 边框
    thin_border = Border(
        left=Side(style='thin', color='B4B4B4'),
        right=Side(style='thin', color='B4B4B4'),
        top=Side(style='thin', color='B4B4B4'),
        bottom=Side(style='thin', color='B4B4B4')
    )

    # 交替行颜色
    even_fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
    odd_fill = PatternFill(start_color='FFFFFF', end_color='FFFFFF', fill_type='solid')

    # 必填标记
    required_font = Font(name='微软雅黑', size=11, bold=True, color='C00000')

    def style_header_row(ws, headers, row=1):
        """设置表头样式"""
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col_idx, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = thin_border

    def style_data_row(ws, row_data, row_num, is_even=True):
        """设置数据行样式"""
        fill = even_fill if is_even else odd_fill
        for col_idx, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_num, column=col_idx, value=value)
            cell.font = data_font
            cell.fill = fill
            cell.alignment = data_alignment
            cell.border = thin_border

    def add_comment(ws, row, col, text):
        """添加单元格备注"""
        cell = ws.cell(row=row, column=col)
        cell.comment = Comment(text, 'System')

    def auto_width(ws, min_width=12, max_width=50):
        """自动调整列宽"""
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            adjusted_width = min(max(min_width, max_length + 4), max_width)
            ws.column_dimensions[column].width = adjusted_width

    # ========== 工作表1: API接口配置 ==========
    ws1 = wb.active
    ws1.title = 'API接口配置'
    ws1.sheet_properties.tabColor = '4472C4'

    headers1 = ['接口名称', '请求方法', '基础URL', '接口路径', '超时时间(秒)', '重试次数', '启用状态', '备注']
    style_header_row(ws1, headers1)

    # 添加备注
    add_comment(ws1, 1, 1, '接口的唯一标识名称，用于代码中引用')
    add_comment(ws1, 1, 2, 'HTTP方法：GET/POST/PUT/DELETE/PATCH')
    add_comment(ws1, 1, 3, 'API的基础域名，如 https://api.example.com')
    add_comment(ws1, 1, 4, '具体的API端点路径，如 /v1/users')
    add_comment(ws1, 1, 5, '请求超时时间，单位秒，建议3-30')
    add_comment(ws1, 1, 6, '请求失败时的重试次数，0表示不重试')
    add_comment(ws1, 1, 7, '是否启用该接口：是/否')
    add_comment(ws1, 1, 8, '接口的额外说明信息')

    api_data = [
        ['获取用户列表', 'GET', 'https://jsonplaceholder.typicode.com', '/users', 10, 3, '是', '获取所有用户信息'],
        ['获取用户详情', 'GET', 'https://jsonplaceholder.typicode.com', '/users/{id}', 10, 3, '是', '根据ID获取单个用户'],
        ['创建用户', 'POST', 'https://jsonplaceholder.typicode.com', '/users', 15, 2, '是', '创建新用户'],
        ['更新用户', 'PUT', 'https://jsonplaceholder.typicode.com', '/users/{id}', 15, 2, '是', '更新用户信息'],
        ['删除用户', 'DELETE', 'https://jsonplaceholder.typicode.com', '/users/{id}', 10, 2, '是', '删除用户'],
        ['获取文章列表', 'GET', 'https://jsonplaceholder.typicode.com', '/posts', 10, 3, '是', '获取所有文章'],
        ['获取评论列表', 'GET', 'https://jsonplaceholder.typicode.com', '/comments', 10, 3, '否', '获取所有评论'],
    ]

    for idx, row_data in enumerate(api_data, 2):
        style_data_row(ws1, row_data, idx, is_even=(idx % 2 == 0))

    auto_width(ws1)
    ws1.freeze_panes = 'A2'  # 冻结首行

    # ========== 工作表2: 请求参数配置 ==========
    ws2 = wb.create_sheet('请求参数配置')
    ws2.sheet_properties.tabColor = '70AD47'

    headers2 = ['参数名称', '所属接口', '参数位置', '参数类型', '默认值', '是否必填', '参数说明']
    style_header_row(ws2, headers2)

    add_comment(ws2, 1, 1, '参数的名称，如 page、limit、userId')
    add_comment(ws2, 1, 2, '关联的接口名称，对应API接口配置表')
    add_comment(ws2, 1, 3, '参数位置：query(URL参数)/body(请求体)/header(请求头)/path(路径参数)')
    add_comment(ws2, 1, 4, '参数数据类型：string/int/float/bool/list/object')
    add_comment(ws2, 1, 5, '参数的默认值，可为空')
    add_comment(ws2, 1, 6, '是否必填：是/否')
    add_comment(ws2, 1, 7, '参数的详细说明')

    param_data = [
        ['page', '获取用户列表', 'query', 'int', '1', '否', '页码，从1开始'],
        ['limit', '获取用户列表', 'query', 'int', '10', '否', '每页数量，最大100'],
        ['id', '获取用户详情', 'path', 'int', '', '是', '用户ID'],
        ['name', '创建用户', 'body', 'string', '', '是', '用户姓名'],
        ['email', '创建用户', 'body', 'string', '', '是', '用户邮箱'],
        ['phone', '创建用户', 'body', 'string', '', '否', '用户电话'],
        ['id', '更新用户', 'path', 'int', '', '是', '用户ID'],
        ['name', '更新用户', 'body', 'string', '', '否', '用户姓名'],
        ['email', '更新用户', 'body', 'string', '', '否', '用户邮箱'],
        ['id', '删除用户', 'path', 'int', '', '是', '用户ID'],
        ['postId', '获取评论列表', 'query', 'int', '', '否', '文章ID，筛选特定文章的评论'],
    ]

    for idx, row_data in enumerate(param_data, 2):
        style_data_row(ws2, row_data, idx, is_even=(idx % 2 == 0))

    auto_width(ws2)
    ws2.freeze_panes = 'A2'

    # ========== 工作表3: 认证信息配置 ==========
    ws3 = wb.create_sheet('认证信息配置')
    ws3.sheet_properties.tabColor = 'FFC000'

    headers3 = ['环境', '认证类型', 'Token/Key', '用户名', '密码', '过期时间', '刷新URL', '备注']
    style_header_row(ws3, headers3)

    add_comment(ws3, 1, 1, '运行环境：dev(开发)/test(测试)/staging(预发布)/prod(生产)')
    add_comment(ws3, 1, 2, '认证方式：Bearer/APIKey/Basic/OAuth2/None')
    add_comment(ws3, 1, 3, '认证令牌或API密钥')
    add_comment(ws3, 1, 4, 'Basic认证的用户名')
    add_comment(ws3, 1, 5, 'Basic认证的密码')
    add_comment(ws3, 1, 6, 'Token过期时间，格式 YYYY-MM-DD HH:MM:SS')
    add_comment(ws3, 1, 7, 'Token刷新接口URL')
    add_comment(ws3, 1, 8, '认证配置的说明')

    auth_data = [
        ['dev', 'Bearer', 'YOUR_DEV_BEARER_TOKEN', '', '', '2025-12-31 23:59:59', '', '开发环境Bearer Token'],
        ['test', 'Bearer', 'YOUR_TEST_BEARER_TOKEN', '', '', '2025-12-31 23:59:59', '', '测试环境Bearer Token'],
        ['staging', 'APIKey', 'YOUR_STAGING_API_KEY', '', '', '', '', '预发布环境API Key'],
        ['prod', 'Bearer', 'YOUR_PROD_BEARER_TOKEN', '', '', '2025-06-30 23:59:59', 'https://api.example.com/refresh', '生产环境Token，注意过期时间'],
    ]

    for idx, row_data in enumerate(auth_data, 2):
        style_data_row(ws3, row_data, idx, is_even=(idx % 2 == 0))

    auto_width(ws3)
    ws3.freeze_panes = 'A2'

    # ========== 工作表4: 环境配置 ==========
    ws4 = wb.create_sheet('环境配置')
    ws4.sheet_properties.tabColor = 'ED7D31'

    headers4 = ['配置项', '当前环境', '开发环境值', '测试环境值', '预发布环境值', '生产环境值', '配置说明']
    style_header_row(ws4, headers4)

    add_comment(ws4, 1, 1, '配置项名称')
    add_comment(ws4, 1, 2, '当前使用的环境标识')
    add_comment(ws4, 1, 3, '开发环境的配置值')
    add_comment(ws4, 1, 4, '测试环境的配置值')
    add_comment(ws4, 1, 5, '预发布环境的配置值')
    add_comment(ws4, 1, 6, '生产环境的配置值')
    add_comment(ws4, 1, 7, '该配置项的用途说明')

    env_data = [
        ['CURRENT_ENV', 'dev', '', '', '', '', '当前运行环境，读取时优先使用该项'],
        ['BASE_URL', 'dev', 'https://jsonplaceholder.typicode.com', 'https://test-api.example.com', 'https://staging-api.example.com', 'https://api.example.com', 'API基础地址'],
        ['LOG_LEVEL', 'dev', 'DEBUG', 'INFO', 'INFO', 'WARNING', '日志级别：DEBUG/INFO/WARNING/ERROR'],
        ['MAX_RETRIES', 'dev', '3', '3', '3', '5', '最大重试次数'],
        ['TIMEOUT', 'dev', '10', '10', '15', '15', '默认超时时间(秒)'],
        ['RATE_LIMIT', 'dev', '100', '100', '200', '1000', '每分钟请求次数限制'],
        ['ENABLE_SSL_VERIFY', 'dev', '否', '否', '是', '是', '是否验证SSL证书'],
        ['PROXY_URL', 'dev', '', 'http://proxy.test:8080', '', '', '代理服务器地址'],
        ['DB_CONNECTION_STRING', 'dev', 'sqlite:///dev.db', 'sqlite:///test.db', '', '', '数据库连接字符串'],
    ]

    for idx, row_data in enumerate(env_data, 2):
        style_data_row(ws4, row_data, idx, is_even=(idx % 2 == 0))

    auto_width(ws4)
    ws4.freeze_panes = 'A2'

    # ========== 工作表5: 日志配置 ==========
    ws5 = wb.create_sheet('日志配置')
    ws5.sheet_properties.tabColor = 'A5A5A5'

    headers5 = ['配置项', '配置值', '配置说明']
    style_header_row(ws5, headers5)

    add_comment(ws5, 1, 1, '日志相关的配置项名称')
    add_comment(ws5, 1, 2, '配置的具体值')
    add_comment(ws5, 1, 3, '配置项的详细说明')

    log_data = [
        ['日志目录', 'logs', '日志文件存放的文件夹路径'],
        ['日志文件名', 'api_client.log', '主日志文件名'],
        ['错误日志文件名', 'api_errors.log', '错误级别日志单独存储'],
        ['日志格式', '%(asctime)s - %(name)s - %(levelname)s - %(message)s', '日志输出格式'],
        ['日期格式', '%Y-%m-%d %H:%M:%S', '日志中时间的显示格式'],
        ['控制台输出', '是', '是否同时在控制台打印日志'],
        ['文件最大大小(MB)', '10', '单个日志文件的最大大小'],
        ['保留日志文件数', '30', '轮转的日志文件保留数量'],
        ['请求日志记录', '是', '是否记录每次请求的详细信息'],
        ['响应日志记录', '是', '是否记录每次响应的详细信息'],
        ['Excel日志记录', '是', '是否同时将请求/响应日志写入Excel工作表'],
        ['Excel日志文件', 'data/api_config.xlsx', '写入请求/响应日志的Excel文件路径'],
        ['Excel日志工作表', '请求响应日志', '用于保存请求/响应日志的新工作表名称'],
    ]

    for idx, row_data in enumerate(log_data, 2):
        style_data_row(ws5, row_data, idx, is_even=(idx % 2 == 0))

    auto_width(ws5)
    ws5.freeze_panes = 'A2'

    # ========== 工作表6: 请求响应日志 ==========
    ws6 = wb.create_sheet('请求响应日志')
    ws6.sheet_properties.tabColor = '9E480E'

    headers6 = ['时间', '类型', '方法/状态', 'URL/耗时', '内容']
    style_header_row(ws6, headers6)
    add_comment(ws6, 1, 1, '日志时间')
    add_comment(ws6, 1, 2, '请求或响应')
    add_comment(ws6, 1, 3, 'HTTP方法或状态码')
    add_comment(ws6, 1, 4, '请求URL或耗时')
    add_comment(ws6, 1, 5, '脱敏后的请求/响应内容')
    auto_width(ws6)
    ws6.freeze_panes = 'A2'

    # 保存文件
    output_path = Path(__file__).parent / 'data' / 'api_config.xlsx'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)
    print(f"✅ Excel配置文件已生成: {output_path.resolve()}")
    print(f"   包含工作表: {wb.sheetnames}")


if __name__ == '__main__':
    create_styled_excel()
