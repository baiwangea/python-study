# Git Commit 说明规则

## 概述
本规范定义了 Git 提交信息的格式和内容要求，旨在提高代码提交的可读性、一致性和可追溯性，方便团队协作和自动化生成变更日志。

## 提交信息结构
提交信息由三部分组成：**标题（Header）**、**正文（Body）**（可选）和**脚注（Footer）**（可选），格式如下：

```
<类型>(<范围>): <简短描述>
<空行>
<详细说明（可选）>
<空行>
<脚注（可选）>
```

- **标题**：强制，单行，50 字符以内（最多 72 字符）。
- **正文**：可选，详细说明变更背景或细节，每行不超过 72 字符。
- **脚注**：可选，关联问题或说明破坏性变更。

## 类型（Type）
类型描述提交的性质，常用类型包括：

- **feat**：新增功能
- **fix**：修复 bug
- **docs**：文档变更
- **style**：代码格式调整（不影响功能，如空格、缩进）
- **refactor**：代码重构（不新增功能、不修复 bug）
- **perf**：性能优化
- **test**：添加或修改测试
- **build**：构建工具或依赖变更
- **ci**：持续集成配置变更
- **chore**：杂项任务（如更新版本号）
- **revert**：回滚某次提交

## 范围（Scope）
范围是可选的，指定变更影响的模块或功能区域，例如 `auth`、`ui`、`api`、`config`。应具体且简短。

## 简短描述（Subject）
- 使用动词开头，描述变更内容（如“添加”、“修复”）。
- 中文提交保持简洁，英文使用现在时（`add` 而非 `added`）。
- 首字母不大写，结尾不加句号。
- 长度控制在 50 字符以内。

## 正文（Body）
- 提供变更的背景、原因或细节。
- 每行不超过 72 字符。
- 可使用列表形式列出具体改动。
- 说明“为什么”而不仅仅是“做了什么”。

## 脚注（Footer）
- **关联问题**：格式如 `Closes #123` 或 `Fixes #456`。
- **破坏性变更**：以 `BREAKING CHANGE:` 开头，描述不向后兼容的变更。

## 示例
以下是符合规范的提交信息示例：

```
feat(auth): add user login functionality

Implement user authentication with JWT tokens.
- Add login endpoint in auth controller
- Update user model with password hashing
- Add validation for email and password fields

Closes #123
```

```
fix(ui): resolve button alignment issue on mobile

Adjust CSS to fix misaligned buttons in responsive view.
Tested on Chrome and Safari mobile browsers.
```

```
docs(readme): update installation instructions

Add steps for setting up Docker environment.
Clarify dependencies for Windows users.
```

```
revert: revert "feat(auth): add user login functionality"

This reverts commit abc123 due to breaking changes in auth flow.

BREAKING CHANGE: Reverts JWT implementation due to security concerns.
```

## 最佳实践
- **语义化**：提交信息应清晰反映变更目的。
- **一致性**：团队统一使用中文或英文。
- **原子提交**：一个提交只做一件事。
- **工具支持**：推荐使用 `commitizen` 或 `commitlint` 强制规范。
- **避免无意义提交**：如“fix bug”或“update”，需具体说明变更内容。

## 团队协作建议
- 定义团队专属的类型和范围列表（如 `frontend`、`backend`）。
- 使用 Git 钩子（如 Husky）集成 `commitlint`。
- 定期审查提交历史，确保一致性和可读性。