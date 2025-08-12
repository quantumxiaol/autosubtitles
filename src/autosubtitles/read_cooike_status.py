from datetime import datetime

def parse_cookies_file(file_path):
    """
    解析Netscape HTTP Cookie格式的文件，并打印每个cookie的信息和过期时间。
    
    :param file_path: cookies.txt文件的路径
    """
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        print(f"开始处理 {len(lines)} 行数据...")
        
        for idx, line in enumerate(lines):
            # 忽略以#开头的注释行
            if line.startswith('#'):
                print(f"跳过注释行 {idx + 1}: {line.strip()}")
                continue
            
            # 跳过空行
            if not line.strip():
                print(f"跳过空行 {idx + 1}")
                continue
            
            parts = line.strip().split('\t')
            
            if len(parts) < 7:
                print(f"警告：发现格式不正确的行 {idx + 1}，跳过处理: {line.strip()}")
                continue
            
            domain, flag1, path, flag2, expires, name, value = parts[:7]
            
            # 将Unix时间戳转换为可读格式
            try:
                readable_expire_time = datetime.utcfromtimestamp(int(expires)).strftime('%Y-%m-%d %H:%M:%S UTC')
            except ValueError:
                readable_expire_time = "无期限"  # 如果expires是0或非数字，则认为没有设置过期时间
                
            # print(f"\n第 {idx + 1} 行:")
            print(f"域名: {domain}")
            print(f"路径: {path}")
            print(f"名称: {name}")
            # print(f"值: {value}")
            print(f"过期时间: {readable_expire_time}")
            # print('-' * 40)
        return {'name': name, 'readable_expire_time': readable_expire_time}
            
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
    except Exception as e:
        print(f"发生错误：{e}")

# 示例调用
parse_cookies_file('./cookies.txt')
