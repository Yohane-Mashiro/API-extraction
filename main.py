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

    # 提取简单字符串常量
    var_string_map = {}
    try:
        # const/let/var name = "value";
        var_assign_pattern = r'\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*([\'"`])([^\'"`]*)\2\s*;'
        for name, _, val in re.findall(var_assign_pattern, content):
            var_string_map[name] = val
    except Exception:
        pass
    
    # 常见API字面量
    patterns = [
        # fetch("...") 纯字面量
        r'fetch\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',
        # XMLHttpRequest: open("METHOD", "URL")
        r'\.open\s*\(\s*[\'"`][^\'"`]+[\'"`]\s*,\s*[\'"`]([^\'"`]+)[\'"`]',
        # jQuery
        r'\$\.(?:get|post|ajax)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',
        # axios
        r'axios\.(?:get|post|put|delete|patch)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',
        # WebSocket
        r'new\s+WebSocket\s*\(\s*[\'"`]([^\'"`]+)[\'"`]',
        # http/https 直链
        r'[\'"`](https?://[^\'"`\s]+)[\'"`]',
        # 以 / 开头的常见路径
        r'[\'"`](/(?:api|rest|service|endpoint|v\d+/)[^\'"`\s]+)[\'"`]',
    ]
    for pattern in patterns:
        for match in re.findall(pattern, content, re.IGNORECASE):
            api_url = match.strip()
            if api_url and not api_url.startswith('//') and len(api_url) > 1:
                apis.append(api_url)

    # 处理“变量 + 字面量” 与 “字面量 + 变量”的形式
    concat_patterns = [
        # var + lit
        (r'fetch\s*\(\s*([A-Za-z_$][\w$]*)\s*\+\s*[\'"`]([^\'"`]+)[\'"`]', 'var+lit'),
        (r'axios\.(?:get|post|put|delete|patch)\s*\(\s*([A-Za-z_$][\w$]*)\s*\+\s*[\'"`]([^\'"`]+)[\'"`]', 'var+lit'),
        (r'\$\.(?:get|post|ajax)\s*\(\s*([A-Za-z_$][\w$]*)\s*\+\s*[\'"`]([^\'"`]+)[\'"`]', 'var+lit'),
        (r'new\s+WebSocket\s*\(\s*([A-Za-z_$][\w$]*)\s*\+\s*[\'"`]([^\'"`]+)[\'"`]', 'var+lit'),
        (r'\.open\s*\(\s*[\'"`][^\'"`]+[\'"`]\s*,\s*([A-Za-z_$][\w$]*)\s*\+\s*[\'"`]([^\'"`]+)[\'"`]', 'var+lit'),
        # lit + var
        (r'fetch\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*\+\s*([A-Za-z_$][\w$]*)', 'lit+var'),
        (r'axios\.(?:get|post|put|delete|patch)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*\+\s*([A-Za-z_$][\w$]*)', 'lit+var'),
        (r'\$\.(?:get|post|ajax)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*\+\s*([A-Za-z_$][\w$]*)', 'lit+var'),
        (r'new\s+WebSocket\s*\(\s*[\'"`]([^\'"`]+)[\'"`]\s*\+\s*([A-Za-z_$][\w$]*)', 'lit+var'),
        (r'\.open\s*\(\s*[\'"`][^\'"`]+[\'"`]\s*,\s*[\'"`]([^\'"`]+)[\'"`]\s*\+\s*([A-Za-z_$][\w$]*)', 'lit+var'),
    ]
    for pattern, kind in concat_patterns:
        for left, right in re.findall(pattern, content, re.IGNORECASE):
            if kind == 'var+lit':
                var, lit = left, right
                base = var_string_map.get(var, '')
                api_url = (base + lit).strip() if (var in var_string_map) else lit
            else:
                lit, var = left, right
                base = var_string_map.get(var, '')
                api_url = (lit + base).strip() if (var in var_string_map) else lit
            if api_url and not api_url.startswith('//') and len(api_url) > 1:
                apis.append(api_url)

    # 模板字符串：fetch(`${ny}/randomPayload`)
    tpl_patterns = [
        r'fetch\s*\(\s*`([^`]+)`',
        r'axios\.(?:get|post|put|delete|patch)\s*\(\s*`([^`]+)`',
        r'\$\.(?:get|post|ajax)\s*\(\s*`([^`]+)`',
        r'new\s+WebSocket\s*\(\s*`([^`]+)`',
        r'\.open\s*\(\s*[\'"`][^\'"`]+[\'"`]\s*,\s*`([^`]+)`',
    ]
    for pattern in tpl_patterns:
        for tpl in re.findall(pattern, content, re.IGNORECASE):
            def repl_var(m):
                v = m.group(1)
                return var_string_map.get(v, '')
            resolved = re.sub(r'\$\{\s*([A-Za-z_$][\w$]*)\s*\}', repl_var, tpl).strip()
            if resolved and not resolved.startswith('//') and len(resolved) > 1:
                apis.append(resolved)

    # 去重
    apis = sorted(set(apis))
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
            
            if not all_apis:
                return
            
            total_apis = 0
            for file_path, apis in all_apis.items():
                f.write(f"文件: {file_path}\n")
                
                for i, api in enumerate(apis, 1):
                    f.write(f"{api}\n")
                    total_apis += 1
                
            
            
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