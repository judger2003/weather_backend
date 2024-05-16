def get_coordinates_from_file(adcode, file_path):
    adcode_center_map = {}

    # 打开文件并读取内容
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 去除行尾的换行符和多余的空格
            line = line.strip()
            if line:
                # 按照分隔符'-'分割字符串
                parts = line.split('-')
                if len(parts) == 5:
                    adcode_key = parts[1]
                    coordinates = f"{parts[3]},{parts[4]}"
                    adcode_center_map[adcode_key] = coordinates

    # 根据adcode返回对应的经纬度
    return adcode_center_map.get(str(adcode), "Unknown adcode")


# 示例使用
file_path = 'D:\\appfile\\pythonfile\\weather_backend\\app1\centers (1).txt'
adcode = "110000"
coordinates = get_coordinates_from_file(adcode, file_path)
print(coordinates)  # 输出: 116.405285,39.904989
