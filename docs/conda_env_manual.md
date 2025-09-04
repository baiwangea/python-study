# Python Conda 环境管理常用操作手册

Conda 是 Python 中常用的包管理和环境管理工具，适用于 Anaconda 和 Miniconda。  
本手册覆盖 **基础操作 → 环境管理 → 包管理 → 高级用法**。

---

## 一、基础操作

### 1. 查看 Conda 版本
```bash
conda --version
```

### 2. 查看当前 Conda 信息
```bash
conda info
```

### 3. 更新 Conda 本身
```bash
conda update conda
```

---

## 二、环境管理

### 1. 创建新环境
```bash
conda create -n myenv python=3.11
```
- `-n myenv`：指定环境名称  
- `python=3.11`：指定 Python 版本

### 2. 激活环境
```bash
conda activate myenv
```

### 3. 退出环境
```bash
conda deactivate
```

### 4. 查看已有环境
```bash
conda env list
# 或
conda info --envs
```

### 5. 删除环境
```bash
conda remove -n myenv --all
```

### 6. 导出环境
```bash
conda env export > environment.yml
```

### 7. 使用 YAML 文件创建环境
```bash
conda env create -f environment.yml
```

---

## 三、包管理

### 1. 查看已安装包
```bash
conda list
```

### 2. 安装包
```bash
conda install numpy
```
- 安装指定版本：
```bash
conda install numpy=1.25
```

### 3. 升级包
```bash
conda update numpy
```

### 4. 删除包
```bash
conda remove numpy
```

### 5. 安装 pip 包
```bash
conda install pip
pip install requests
```

---

## 四、环境克隆与迁移

### 1. 克隆环境
```bash
conda create --name newenv --clone myenv
```

### 2. 导出依赖文件
```bash
conda list --explicit > spec-file.txt
```

### 3. 使用依赖文件创建环境
```bash
conda create --name myenv --file spec-file.txt
```

---

## 五、高级用法

### 1. 设置频道
```bash
conda config --add channels conda-forge
```

### 2. 查看配置
```bash
conda config --show
```

### 3. 搜索包
```bash
conda search pandas
```

### 4. 清理缓存
```bash
conda clean -a
```

### 5. 使用 mamba 提升安装速度
```bash
mamba install numpy
```
- `mamba` 是 Conda 的快速替代工具，兼容大部分 Conda 命令

---

## 六、最佳实践

1. 每个项目使用独立环境，避免包冲突  
2. 定期导出 `environment.yml` 以便迁移和共享  
3. 优先使用 Conda 官方或 `conda-forge` 频道安装包  
4. 对大型科学计算或深度学习项目，推荐使用 `mamba` 提升安装速度  
5. 遇到冲突或错误，可使用 `conda update --all` 或重新创建环境

---
