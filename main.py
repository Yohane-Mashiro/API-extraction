import os
import re
import glob
from pathlib import Path

def extract_apis_from_js_file(file_path):
    """
    从JavaScript文件中提取API相关的内容
    """
    apis = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='gbk') as file:
                content = file.read()
        except:
            print(f"无法读取文件: {file_path}")
            return apis
    
    # 正则表达式模式，用于匹配常见的API模式
    patterns = [
        # fetch API
        r'fetch\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',
        # XMLHttpRequest
        r'\.open\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*,\s*[\'"`]([^\'"`]+)[\'"`]',
        # jQuery AJAX
        r'\$\.(?:get|post|ajax)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',
        # axios
        r'axios\.(?:get|post|put|delete|patch)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',
        # 一般的URL模式
        r'[\'"`](https?://[^\'"`\s]+)[\'"`]',
        r'[\'"`](/api/[^\'"`\s]+)[\'"`]',
        r'[\'"`](/v\d+/[^\'"`\s]+)[\'"`]',
        # WebSocket
        r'new\s+WebSocket\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',
        # 其他常见API模式
        r'[\'"`](/(?:api|rest|service|endpoint)/[^\'"`\s]+)[\'"`]',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                # 对于有多个捕获组的匹配
                api_url = ' '.join(match)
            else:
                api_url = match
            
            # 清理和验证API URL
            api_url = api_url.strip()
            if api_url and not api_url.startswith('//') and len(api_url) > 3:
                apis.append(api_url)
    
    # 去重
    apis = list(set(apis))
    
    return apis

def scan_js_folder(js_folder_path):
    """
    扫描js文件夹中的所有JavaScript文件
    """
    all_apis = {}
    
    if not os.path.exists(js_folder_path):
        print(f"js文件夹不存在: {js_folder_path}")
        return all_apis
    
    # 查找所有JavaScript文件
    js_files = glob.glob(os.path.join(js_folder_path, "**/*.js"), recursive=True)
    js_files.extend(glob.glob(os.path.join(js_folder_path, "**/*.jsx"), recursive=True))
    js_files.extend(glob.glob(os.path.join(js_folder_path, "**/*.ts"), recursive=True))
    js_files.extend(glob.glob(os.path.join(js_folder_path, "**/*.tsx"), recursive=True))
    
    if not js_files:
        print("在js文件夹中没有找到JavaScript文件")
        return all_apis
    
    print(f"找到 {len(js_files)} 个JavaScript文件")
    
    for js_file in js_files:
        print(f"正在处理: {js_file}")
        apis = extract_apis_from_js_file(js_file)
        if apis:
            relative_path = os.path.relpath(js_file, js_folder_path)
            all_apis[relative_path] = apis
            print(f"  - 找到 {len(apis)} 个API")
    
    return all_apis

def write_apis_to_file(all_apis, output_file):
    """
    将提取的API写入到文件中
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("JavaScript文件API提取结果\n")
            f.write("=" * 50 + "\n\n")
            
            if not all_apis:
                f.write("未找到任何API\n")
                return
            
            total_apis = 0
            for file_path, apis in all_apis.items():
                f.write(f"文件: {file_path}\n")
                f.write("-" * 30 + "\n")
                
                for i, api in enumerate(apis, 1):
                    f.write(f"{i}. {api}\n")
                    total_apis += 1
                
                f.write(f"\n小计: {len(apis)} 个API\n\n")
            
            f.write(f"总计: {total_apis} 个API\n")
            
        print(f"API提取完成，结果已写入: {output_file}")
        print(f"总共提取了 {total_apis} 个API")
        
    except Exception as e:
        print(f"写入文件时出错: {e}")

def main():
    """
    主函数
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    js_folder = os.path.join(current_dir, "js")
    output_file = os.path.join(current_dir, "api.txt")
    
    print("开始从JavaScript文件中提取API...")
    print(f"扫描目录: {js_folder}")
    print(f"输出文件: {output_file}")
    print("-" * 50)
    
    # 扫描js文件夹
    all_apis = scan_js_folder(js_folder)
    
    # 写入结果到文件
    write_apis_to_file(all_apis, output_file)

if __name__ == "__main__":
    main()