# @Version        : 1.0
# @Update Time    : 2025/7/29 20:43
# @File           : stoplight_elements.py
# @IDE            : PyCharm
# @Desc           : FastAPI + Stoplight Elements 快速开发API文档
from __future__ import annotations

from enum import Enum
from fastapi.responses import HTMLResponse
from typing_extensions import Annotated, Doc


class TryItCredentialsPolicy(Enum):
    OMIT = "omit"
    INCLUDE = "include"
    SAME_ORIGIN = "same-origin"


class DocumentationLayout(Enum):
    SIDEBAR = "sidebar"
    RESPONSIVE = "responsive"
    STACKED = "stacked"


class NavigationRouter(Enum):
    HISTORY = "history"
    HASH = "hash"
    MEMORY = "memory"
    STATIC = "static"


def get_stoplight_elements_html(
    *,
    openapi_url: Annotated[
        str,
        Doc(
            """
            OpenAPI规范文件的URL路径。

            例如: `/openapi.json` 或 `/swagger.json`。

            注意: 此参数与 `api_description_document` 互斥，只能使用其中一个。
            """
        ),
    ],
    title: Annotated[
        str,
        Doc(
            """
            API文档页面的标题，将显示在浏览器标签页和页面顶部。

            例如: `我的API文档` 或 `用户服务API`。
            """
        ),
    ],
    stoplight_elements_js_url: Annotated[
        str,
        Doc(
            """
            Stoplight Elements JavaScript库的CDN URL。

            默认使用官方CDN: `https://unpkg.com/@stoplight/elements/web-components.min.js`。

            如果需要自托管或使用特定版本，可以修改此参数。
            """
        ),
    ] = "https://unpkg.com/@stoplight/elements/web-components.min.js",
    stoplight_elements_css_url: Annotated[
        str,
        Doc(
            """
            Stoplight Elements CSS样式的CDN URL。

            默认使用官方CDN: `https://unpkg.com/@stoplight/elements/styles.min.css`。

            如果需要自定义样式或使用特定版本，可以修改此参数。
            """
        ),
    ] = "https://unpkg.com/@stoplight/elements/styles.min.css",
    stoplight_elements_favicon_url: Annotated[
        str,
        Doc(
            """
            页面favicon图标的URL。

            默认使用FastAPI的官方图标: `https://fastapi.tiangolo.com/img/favicon.png`。

            可以替换为自定义图标URL。
            """
        ),
    ] = "https://fastapi.tiangolo.com/img/favicon.png",
    api_description_document: Annotated[
        str,
        Doc(
            """
            直接提供的OpenAPI文档内容（字符串形式）。

            当不想通过URL提供OpenAPI规范时，可以直接传入文档内容。

            注意: 此参数与 `openapi_url` 互斥，只能使用其中一个。

            格式可以是YAML或JSON字符串。
            """
        ),
    ] = "",
    base_path: Annotated[
        str,
        Doc(
            """
            API的基础路径，用于处理文档在子目录下的情况。

            例如: 如果API文档位于 `https://example.com/docs/api`，则设置为 `/docs/api`。

            当使用 `router: 'history'` 时特别有用。
            """
        ),
    ] = "",
    hide_internal: Annotated[
        bool,
        Doc(
            """
            是否隐藏标记为内部的API。

            设置为 `True` 时，会过滤掉所有带有 `x-internal` 标记的内容。

            默认值: `False`（显示所有API）。
            """
        ),
    ] = False,
    hide_try_it: Annotated[
        bool,
        Doc(
            """
            是否完全隐藏"Try It"功能。

            设置为 `True` 时，用户将无法在文档中直接测试API。

            默认值: `False`（显示"Try It"功能）。
            """
        ),
    ] = False,
    hide_try_it_panel: Annotated[
        bool,
        Doc(
            """
            是否隐藏"Try It"面板，但保留请求示例。

            设置为 `True` 时，用户可以看到请求示例，但不能直接执行测试。

            默认值: `False`（显示完整的"Try It"面板）。
            """
        ),
    ] = False,
    hide_schemas: Annotated[
        bool,
        Doc(
            """
            是否在侧边栏中隐藏模式定义（Schemas）。

            设置为 `True` 时，使用侧边栏布局时将不显示Schemas部分。

            默认值: `False`（显示Schemas）。
            """
        ),
    ] = False,
    hide_export: Annotated[
        bool,
        Doc(
            """
            是否隐藏导出按钮。

            设置为 `True` 时，文档概览部分的导出按钮将被隐藏。

            默认值: `False`（显示导出按钮）。
            """
        ),
    ] = False,
    try_it_cors_proxy: Annotated[
        str,
        Doc(
            """
            CORS代理URL，用于解决跨域问题。

            当API与文档不在同一域名下时，可以通过CORS代理发送"Try It"请求。

            提供的URL将被添加到实际请求的URL前面。
            """
        ),
    ] = "",
    try_it_credential_policy: Annotated[
        TryItCredentialsPolicy,
        Doc(
            """
            "Try It"功能的凭证策略。

            选项:
            - `omit`: 不发送凭证（默认）
            - `include`: 总是发送凭证
            - `same-origin`: 仅在同源时发送凭证

            根据API的安全要求选择合适的策略。
            """
        ),
    ] = TryItCredentialsPolicy.SAME_ORIGIN,
    layout: Annotated[
        DocumentationLayout,
        Doc(
            """
            文档的布局模式。

            选项:
            - `sidebar`: 三列布局，带可调整大小的侧边栏（默认）
            - `responsive`: 类似sidebar，但在小屏幕上将侧边栏折叠为可切换的抽屉
            - `stacked`: 单列布局，适合集成到已有网站中

            根据需求选择合适的布局。
            """
        ),
    ] = DocumentationLayout.SIDEBAR,
    logo: Annotated[
        str,
        Doc(
            """
            自定义Logo的URL，显示在标题旁边。

            图片应为正方形，建议尺寸 40x40 到 80x80 像素。

            留空则使用默认API图标。
            """
        ),
    ] = "",
    router: Annotated[
        NavigationRouter,
        Doc(
            """
            路由模式，决定导航如何工作。

            选项:
            - `history`: 使用HTML5 history API（默认）
            - `hash`: 使用URL的hash部分
            - `memory`: 在内存中保持"URL"历史记录（不读写地址栏）
            - `static`: 使用StaticRouter，有助于在服务器上渲染页面

            大多数SPA应用推荐使用`history`模式。
            """
        ),
    ] = NavigationRouter.HASH,
) -> HTMLResponse:
    # 根据配置生成属性字符串
    attributes = [
        f'title="{title}"',
        f'layout="{layout.value}"',
        f'router="{router.value}"',
        f'tryItCredentialPolicy="{try_it_credential_policy.value}"',
    ]

    if openapi_url and not api_description_document:
        attributes.append(f'apiDescriptionUrl="{openapi_url}"')
    elif api_description_document:
        attributes.append(f'apiDescriptionDocument="{api_description_document}"')

    if base_path:
        attributes.append(f'basePath="{base_path}"')
    if hide_internal:
        attributes.append('hideInternal="true"')
    if hide_try_it:
        attributes.append('hideTryIt="true"')
    if hide_try_it_panel:
        attributes.append('hideTryItPanel="true"')
    if hide_schemas:
        attributes.append('hideSchemas="true"')
    if hide_export:
        attributes.append('hideExport="true"')
    if try_it_cors_proxy:
        attributes.append(f'tryItCorsProxy="{try_it_cors_proxy}"')
    if logo:
        attributes.append(f'logo="{logo}"')

    attributes_str = "\n                ".join(attributes)

    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - API文档</title>
        <link rel="icon" href="{stoplight_elements_favicon_url}">
        <link rel="stylesheet" href="{stoplight_elements_css_url}">
        <script src="{stoplight_elements_js_url}"></script>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap">
        <style>
            :root {{
                --primary-color: #4f46e5;
                --secondary-color: #7c3aed;
                --bg-color: #f8fafc;
                --text-color: #1e293b;
                --card-bg: #ffffff;
                --border-color: #e2e8f0;
                --success-color: #10b981;
                --warning-color: #f59e0b;
                --error-color: #ef4444;
                --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            }}

            [data-theme="dark"] {{
                --primary-color: #818cf8;
                --secondary-color: #a78bfa;
                --bg-color: #0f172a;
                --text-color: #e2e8f0;
                --card-bg: #1e293b;
                --border-color: #334155;
            }}

            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}

            body {{
                background-color: var(--bg-color);
                color: var(--text-color);
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                line-height: 1.6;
                min-height: 100vh;
                transition: background-color 0.3s ease, color 0.3s ease;
            }}

            .container {{
                max-width: 1600px;
                margin: 0 auto;
                padding: 0 20px;
            }}

            header {{
                background-color: var(--card-bg);
                border-bottom: 1px solid var(--border-color);
                padding: 1.2rem 0;
                position: sticky;
                top: 0;
                z-index: 100;
                box-shadow: var(--shadow);
            }}

            .header-content {{
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}

            .brand {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}

            .logo {{
                width: 40px;
                height: 40px;
                border-radius: 8px;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 18px;
            }}

            .brand-text {{
                font-size: 1.4rem;
                font-weight: 700;
            }}

            .api-actions {{
                display: flex;
                gap: 12px;
                align-items: center;
            }}

            .theme-toggle {{
                background: transparent;
                border: none;
                color: var(--text-color);
                cursor: pointer;
                font-size: 1.2rem;
                width: 36px;
                height: 36px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background 0.2s;
            }}

            .theme-toggle:hover {{
                background: rgba(127, 127, 127, 0.1);
            }}

            .api-container {{
                margin-top: 2rem;
                margin-bottom: 3rem;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: var(--shadow);
                height: calc(100vh - 120px);
                min-height: 600px;
                background-color: var(--card-bg);
                transition: all 0.3s ease;
            }}

            elements-api {{
                --sl-color-primary: var(--primary-color);
                --sl-color-secondary: var(--secondary-color);
                --sl-background-color: var(--card-bg);
                --sl-foreground-color: var(--text-color);
                --sl-color-success: var(--success-color);
                --sl-color-warning: var(--warning-color);
                --sl-color-error: var(--error-color);
                --sl-border-color: var(--border-color);
                --sl-font: 'Inter', sans-serif;
                --sl-border-radius: 8px;
                --sl-elements-border-color: var(--border-color);
                --sl-elements-font-family: var(--sl-font);
            }}

            .footer {{
                text-align: center;
                padding: 1.5rem 0;
                color: var(--text-color);
                font-size: 0.9rem;
                opacity: 0.7;
                border-top: 1px solid var(--border-color);
                margin-top: 2rem;
            }}

            @media (max-width: 768px) {{
                .header-content {{
                    flex-direction: column;
                    gap: 15px;
                    align-items: flex-start;
                }}

                .api-actions {{
                    align-self: flex-end;
                }}

                .api-container {{
                    height: calc(100vh - 160px);
                    margin-top: 1rem;
                    border-radius: 8px;
                }}
            }}
        </style>
    </head>
    <body>
        <header>
            <div class="container">
                <div class="header-content">
                    <div class="brand">
                        <div class="logo">API</div>
                        <div class="brand-text">{title}</div>
                    </div>
                    <div class="api-actions">
                        <button class="theme-toggle" id="themeToggle" aria-label="切换主题">
                            <span id="themeIcon">🌙</span>
                        </button>
                    </div>
                </div>
            </div>
        </header>

        <div class="container">
            <div class="api-container">
                <elements-api
                    {attributes_str}
                />
            </div>
        </div>

        <script>
            document.addEventListener('DOMContentLoaded', () => {{
                // 主题切换功能
                const themeToggle = document.getElementById('themeToggle');
                const themeIcon = document.getElementById('themeIcon');
                const body = document.body;

                // 检测系统主题偏好
                const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                const savedTheme = localStorage.getItem('theme');

                // 应用主题
                function applyTheme(isDark) {{
                    if (isDark) {{
                        body.setAttribute('data-theme', 'dark');
                        themeIcon.textContent = '☀️';
                    }} else {{
                        body.removeAttribute('data-theme');
                        themeIcon.textContent = '🌙';
                    }}
                }}

                // 初始主题设置
                if (savedTheme === 'dark') {{
                    applyTheme(true);
                }} else if (savedTheme === 'light') {{
                    applyTheme(false);
                }} else {{
                    applyTheme(prefersDark);
                }}

                // 切换主题
                themeToggle.addEventListener('click', () => {{
                    const isDark = body.getAttribute('data-theme') === 'dark';
                    applyTheme(!isDark);
                    localStorage.setItem('theme', isDark ? 'light' : 'dark');
                }});

                // 响应式动画效果
                const container = document.querySelector('.api-container');
                container.style.opacity = '0';
                container.style.transform = 'translateY(20px)';
                container.style.transition = 'opacity 0.5s ease, transform 0.5s ease';

                setTimeout(() => {{
                    container.style.opacity = '1';
                    container.style.transform = 'translateY(0)';
                }}, 100);

                // 监听系统主题变化
                window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {{
                    if (!localStorage.getItem('theme')) {{
                        applyTheme(e.matches);
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)