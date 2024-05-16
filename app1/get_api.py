import requests
import csv
import json
import adcode2loc

def get_weather_data(location, api_key):
    try:
        # 构建请求URL
        #location = "11010100"
        url = f"https://api.qweather.com/v7/weather/now?location={location}&key={api_key}"

        # 打印调试信息
        print(f"Request URL: {url}")

        # 发送请求并获取响应
        response = requests.get(url)

        # 打印调试信息
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")

        # 检查请求是否成功
        if response.status_code == 200:
            data = response.json()
            if data['code'] == '200':
                # 解析返回的天气数据
                now = data['now']
                weather_data = {
                    'obsTime': now['obsTime'],
                    'temp': now['temp'],
                    'feelsLike': now['feelsLike'],
                    'icon': now['icon'],
                    'text': now['text'],
                    'wind360': now['wind360'],
                    'windDir': now['windDir'],
                    'windScale': now['windScale'],
                    'windSpeed': now['windSpeed'],
                    'humidity': now['humidity'],
                    'precip': now['precip'],
                    'pressure': now['pressure'],
                    'vis': now['vis'],
                    'cloud': now.get('cloud', ''),
                    'dew': now.get('dew', '')
                }

                # 写入CSV文件
                csv_file = 'weather_data.csv'
                with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(weather_data.keys())
                    writer.writerow(weather_data.values())

                return weather_data
            else:
                print(f"Error in API response: {data['code']}")
                return None
        else:
            print(f"HTTP request failed with status code: {response.status_code}")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_coordinates_from_file(adcode):
    adcode_center_map = {}
    file_path = "D:\\appfile\pythonfile\weather_backend\\app1\centers (1).txt"
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:
                parts = line.split('-')
                if len(parts) == 5:
                    adcode_key = parts[1]
                    coordinates = f"{parts[3]},{parts[4]}"
                    adcode_center_map[adcode_key] = coordinates

    return adcode_center_map.get(str(adcode), "Unknown adcode")


def main(adcodes, api_key):
    weather_data_list = []

    for adcode in adcodes:
        loc = get_coordinates_from_file(adcode)
        if loc == "Unknown adcode":
            weather_data_list.append({
                "adcode": adcode,
                "value": "Unknown adcode"
            })
            continue

        weather_data = get_weather_data(loc, api_key)
        if weather_data is None:
            weather_data_list.append({
                "adcode": adcode,
                "value": "Failed to retrieve weather data"
            })
            continue

        weather_data_list.append({
            "adcode": adcode,
            "value": [
                weather_data["pressure"],
                weather_data["temp"],
                weather_data["humidity"],
                weather_data["precip"],
                weather_data["windSpeed"],
                weather_data["vis"],
                weather_data["cloud"]
            ]
        })

    result = {
        "code": 62,
        "msg": "officia",
        "data": {
            "weather": weather_data_list
        }
    }
    return result

# 示例调用
api_key = '3cdf5414d4c5422abfb6aa6bcf19cbce'  # 替换为你的API Key
#latitude = 39.92  # 示例纬度
#longitude = 116.41  # 示例经度
#file_path = "D:\\appfile\pythonfile\weather_backend\\app1\centers (1).txt"
adcodes = ["110000", "120000", "130000"]
result = main(adcodes, api_key)
print(json.dumps(result, indent=2, ensure_ascii=False))
