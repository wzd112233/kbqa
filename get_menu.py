import os

# 配置：你的项目根目录（自动适配，无需修改）
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# 忽略的文件夹/文件（已添加 data、static、__pycache__）
IGNORE_LIST = {
    '__pycache__', 'static', 'data',  # 核心排除项
    '.git', '.idea', 'venv', 'env', 'dist', 'build', '.DS_Store'
}

def generate_tree(dir_path, prefix=''):
    """递归生成目录树结构"""
    items = sorted(os.listdir(dir_path))
    # 过滤忽略项
    items = [item for item in items if item not in IGNORE_LIST and not item.endswith('.pyc')]
    
    for i, item in enumerate(items):
        path = os.path.join(dir_path, item)
        is_last = i == len(items) - 1
        # 打印前缀
        connector = '└── ' if is_last else '├── '
        print(f'{prefix}{connector}{item}')
        
        # 递归处理子文件夹
        if os.path.isdir(path):
            new_prefix = prefix + ('    ' if is_last else '│   ')
            generate_tree(path, new_prefix)

if __name__ == '__main__':
    print("📁 项目目录结构：")
    print(os.path.basename(ROOT_DIR) + "/")
    generate_tree(ROOT_DIR, prefix='│   ')
    print("\n✅ 扫描完成！直接复制以上结构发给我即可~")