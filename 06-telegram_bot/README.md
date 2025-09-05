# Telegram Bot 消息发送模块

本模块提供了简单易用的函数，用于通过 Telegram Bot 发送**纯文本**、**富文本 (Markdown)**、**图片**和**文件**。

## 1. 配置步骤

(配置步骤与之前相同，保持不变...)

## 2. 安装依赖

```bash
pip install -r requirements.txt
```

## 3. 如何使用

### a. 发送纯文本、图片和文件

使用 `send_text_message`, `send_photo`, `send_document` 函数。

### b. 发送带格式的 Markdown 消息

使用 `send_markdown_message` 函数可以发送包含加粗、斜体、链接、代码块等格式的富文本消息。我们内置了几个常用的模板，可以直接调用。

**重要提示：关于 MarkdownV2 语法**

Telegram 使用 `MarkdownV2` 解析模式，它比标准 Markdown 更严格。如果你的文本中包含以下特殊字符，**必须在它们前面加上反斜杠 `\` 进行转义**，否则消息会发送失败！

```
特殊字符列表: _ * [ ] ( ) ~ ` > # + - = | { } . !
```

例如，要发送文本 `v1.2.0`，你需要写作 `v1\.2\.0`。

### c. 内置 Markdown 模板

`sender.py` 中内置了三个开箱即用的模板，你可以直接导入并使用它们。

#### 模板 1: 系统状态报告

- **效果预览:**

  *📊 系统状态报告*

  *服务状态:*
  🟢 `API 服务` - 运行正常
  🟢 `数据库`   - 连接成功
  🟠 `缓存服务` - 响应延迟

  *资源使用率:*
  CPU: `85%` 🌡️
  内存: `60%` 🧠

  `一切尽在掌握之中.`

- **使用方法:**
  ```python
  from sender import send_markdown_message, SYSTEM_STATUS_TEMPLATE
  
  await send_markdown_message(SYSTEM_STATUS_TEMPLATE)
  ```

#### 模板 2: 版本更新日志

- **效果预览:**

  *🚀 版本 v1.2.0 更新日志*

  *✨ 新功能*
  - 用户现在可以导出 CSV 格式的报告
  - 新增了仪表盘小组件

  *🐛 Bug 修复*
  - 修复了移动端导航栏错位的问题

  *查看完整详情:* `https://example.com/changelog/v1-2-0`

- **使用方法:**
  ```python
  from sender import send_markdown_message, CHANGELOG_TEMPLATE
  
  await send_markdown_message(CHANGELOG_TEMPLATE)
  ```

#### 模板 3: 错误警报

- **效果预览:**

  *🚨 严重错误警报*

  在处理用户请求时发生了一个未捕获的异常.

  *Details:*
  ```
  Traceback (most recent call last):
    File "/app/main.py", line 42, in process_request
      result = process_data(data)
    File "/app/utils.py", line 15, in process_data
      raise ValueError("Invalid data format")
  ValueError: Invalid data format
  ```

  *请立即检查日志以获取更多信息!* 🗂️

- **使用方法:**
  ```python
  from sender import send_markdown_message, ERROR_ALERT_TEMPLATE
  
  await send_markdown_message(ERROR_ALERT_TEMPLATE)
  ```

### d. 运行测试脚本

你可以直接运行 `sender.py` 来测试所有消息的发送效果，包括新增的 Markdown 模板。

```bash
python sender.py
```

### e. 可用函数列表

- `send_text_message(message: str)`: 发送纯文本消息。
- `send_markdown_message(text: str)`: 发送 MarkdownV2 格式的富文本消息。
- `send_photo(photo_path: str, caption: str = None)`: 发送本地图片。
- `send_document(document_path: str, caption: str = None)`: 发送本地文件。
