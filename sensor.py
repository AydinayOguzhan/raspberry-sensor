import time 
import board
import adafruit_dht
import RPi.GPIO as GPIO
import requests
import json

#Eğer pulseio problemi çıkarsa aşağıdaki komutu çalıştırarak bütün pinlerin üzerindeki işlemleri bitir
#killall libgpiod_pulsein

dhtDevice = adafruit_dht.DHT22(board.D26)
sense_pin = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN)

cihazId = 5
userId = 1
mainUrl = 'http://194.27.64.147:3000'
url = f'{mainUrl}/cihaz/id/{cihazId}/{userId}'
sendDataUrl = f'{mainUrl}/olcum/{userId}'
veriGondermeSikligi = 5

cihazIp = ""

def getVeriGondermeSikligi():
    #veri gönderme sıklığını serverdan al
    response = requests.get(url)
    rJson = response.json()
    cihazIp = rJson["data"]["ip_adresi"]

    return rJson["data"]["veri_gonderme_sikligi"]

def postValuesToApi(temperature, humidity, gas, cihazId):
    #api için gerekli objeyi oluştur
    obj = {
        "cihaz_id":cihazId,
        "isik_siddeti":"123",
        "sicaklik":str(temperature),
        "karbondioksit_miktari":str(gas),
        "nem":str(humidity),
        "gurultu":"123",
    }
    
    res = requests.post(sendDataUrl, json=obj)
    resJson = res.json()
    
    if(res.status_code != 200):
        print("İşlem başarısız")
        print(res.status_code)
    else:
        print(resJson)

def getPublicIpAdress():
    ip = requests.get('https://api.ipify.org').text
    return ip

def updatePublicIpAdress():
    ip = getPublicIpAdress()
    updateIpUrl = f'{mainUrl}/cihaz/ip/{cihazId}/{ip}/{userId}'
    res = requests.put(updateIpUrl)
    
    if(res.statusCode != 200):
        print("İşlem başarısız")
    else:
        print("İşlem başarılı")

while True:
    try:
        veriGondermeSikligi = getVeriGondermeSikligi()

        #değerleri topla
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity
        gas = GPIO.input(sense_pin)
        
        #veritabanındaki cihaza ait ip adresini güncelle
        # updatePublicIpAdress()
        
        postValuesToApi(temperature_c, humidity, gas, cihazId)
    except RuntimeError as error:
        print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        dhtDevice.exit()
        raise error
    except KeyboardInterrupt:
        dhtDevice.exit()
        print("exiting script")
    print(f'Veri gönderme sıklığı: {veriGondermeSikligi}')
    time.sleep(veriGondermeSikligi)
        
        
        
        
        
        
        
        
        