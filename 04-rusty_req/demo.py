from faker import Faker

# 初始化，默认是英文环境
fake = Faker()

# 生成中文数据
fake_zh = Faker('zh_CN')

# --- 生成各类数据 ---

# 姓名
print(f"姓名: {fake.name()}")
print(f"中文姓名: {fake_zh.name()}")

# 地址
print(f"地址: {fake.address()}")
print(f"中文地址: {fake_zh.address()}")

# 随机文本
print(f"文本: {fake.text()}")

# 电子邮件
print(f"电子邮件: {fake.email()}")

# 公司名称
print(f"公司: {fake_zh.company()}")

# 手机号码
print(f"手机号: {fake_zh.phone_number()}")

# 身份证号
print(f"身份证号: {fake_zh.ssn()}")
