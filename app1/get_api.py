import requests
import csv
import json
import redis
#import adcode2loc

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
    file_path = "/home/appfile/backend/djangoProject/app1/centers (1).txt"
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
    print("1/n")
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
    #print("1/n")
    print(weather_data_list)
    result = {
        "code": 20000,
        "msg": "success",
        "data": {
            "weather": weather_data_list
        }
    }
    return result
import requests
import json
import schedule
import time
import MySQLdb
def fetch_and_store_weather_data():
    api_key = '3cdf5414d4c5422abfb6aa6bcf19cbce'  # 替换为你的API Key
    file_path = '/home//appfile//backend//djangoProject//app1//centers (1).txt'  # 替换为中心文件的路径

    # 连接到SQLite数据库
    conn = MySQLdb.connect(
        host='localhost',
        user='root',  # 替换为你的MySQL用户名
        password='',  # 替换为你的MySQL密码
        db='weather_db',  # 替换为你的数据库名称
        charset='utf8mb4'
    )
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS weather (
            adcode VARCHAR(50) PRIMARY KEY,
            pressure VARCHAR(255),
            temp VARCHAR(255),
            humidity VARCHAR(255),
            precip VARCHAR(255),
            windSpeed VARCHAR(255),
            vis VARCHAR(255),
            cloud VARCHAR(255)
        )
    ''')

    # 从文件中读取所有adcode和坐标
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:
                parts = line.split('-')
                if len(parts) >= 5:
                    adcode = parts[1]
                    coordinates = f"{parts[3]},{parts[4]}"
                    weather_data = get_weather_data(coordinates, api_key)
                    if weather_data:
                        c.execute('''
                            REPLACE INTO weather (adcode, pressure, temp, humidity, precip, windSpeed, vis, cloud)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (
                            adcode,
                            weather_data["pressure"],
                            weather_data["temp"],
                            weather_data["humidity"],
                            weather_data["precip"],
                            weather_data["windSpeed"],
                            weather_data["vis"],
                            weather_data["cloud"]
                        ))
    conn.commit()
    conn.close()
    print("Weather data has been stored in the database.")



def retrieve_weather_data(adcodes):
    cache = redis.Redis(host='localhost', port=6379, db=0)
    query = "|".join(adcodes)
    cached_data = cache.get(query)
    
    if cached_data:
        return json.loads(cached_data)
    
    # 缓存中没有数据，从数据库获取
    #result = get_data_from_db(query)
    
    # 将数据存储到缓存中，并设置过期时间（例如 300 秒）
    conn = MySQLdb.connect(
        host='localhost',
        user='root',  # 替换为你的MySQL用户名
        password='',  # 替换为你的MySQL密码
        db='weather_db',  # 替换为你的数据库名称
        charset='utf8mb4'
    )
    c = conn.cursor()
    weather_data_list = []
    for adcode in adcodes:
        c.execute('SELECT * FROM weather WHERE adcode = %s', (adcode,))
        row = c.fetchone()
        if row:
            weather_data_list.append({
                "adcode": adcode,
                "value": [row[1], row[2], row[3], row[4], row[5], row[6], row[7]]
            })
        else:
            weather_data_list.append({
                "adcode": adcode,
                "value": "Data not found"
            })

    conn.close()
    
    result = {
        "code": 20000,
        "msg": "success",
        "data": {
            "weather": weather_data_list
        }
    }
    cache.setex(query, 30, json.dumps(result))
    return result


# 定义定时任务
def scheduled_job():
    schedule.every().day.at("00:00").do(fetch_and_store_weather_data)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    #adcodes = ["110000", "120000", "130000"]
    #print(retrieve_weather_data(adcodes))
    #fetch_and_store_weather_data()
    fetch_and_store_weather_data()
# 示例调用
#api_key = '3cdf5414d4c5422abfb6aa6bcf19cbce'  # 替换为你的API Key
#latitude = 39.92  # 示例纬度
#longitude = 116.41  # 示例经度
#file_path = "D:\\appfile\pythonfile\weather_backend\\app1\centers (1).txt"
#result = main(adcodes, api_key)
#print(json.dumps(result, indent=2, ensure_ascii=False))
