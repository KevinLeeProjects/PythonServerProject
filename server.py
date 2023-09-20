import asyncio
import sys
import time
import aiohttp
import json




# tar -czvf project.tgz server.py report.pdf




globalServerName = ""
globalServerNameLower = ""
globalBuddyList = []
globalDataList = []
globalNameAndPort = []
globalAllServerNames = []
globalAllServerPorts = []
globalAPIKey = ""
globalWHATMessage = []
globalMyPort = ""




def GetServerName():
   if len(sys.argv) > 1:
       return sys.argv[1]
   else:
       return "? " + sys.argv[0]




async def main():
   global globalDataList
   globalDataList = []
   global globalNameAndPort
   global globalAllServerNames
   global globalAllServerPorts
   global globalAPIKey
   global globalWHATMessage
   global globalMyPort
   globalAPIKey = "" #Had to delete my API key so no one would use my account
   globalAllServerNames = ["Bailey", "Bona", "Campbell", "Clark", "Jaquez"]
   globalAllServerPorts = [10000, 10001, 10002, 10003, 10004]  # CHANGE
   # globalAllServerPorts = [17440, 17441, 17442, 17443, 17444] #Testing ports
   for index in range(5):
       hashTable = {
           "ServerName": globalAllServerNames[index],
           "ServerPort": globalAllServerPorts[index],
       }
       globalNameAndPort.append(hashTable)
   serverName = GetServerName()
   portNumber = 0
   global globalServerName
   globalServerName = GetServerName()
   global globalServerNameLower
   globalServerNameLower = serverName
   global globalBuddyList
  
   globalMyPort = portNumber
   if serverName == "Bailey":
       portNumber = 10000
       globalBuddyList = ["Bona", "Campbell"]
   elif serverName == "Bona":
       portNumber = 10001
       globalBuddyList = ["Bailey", "Campbell", "Jaquez"]
   elif serverName == "Campbell":
       portNumber = 10002
       globalBuddyList = ["Bailey", "Bona", "Jaquez"]
   elif serverName == "Clark":
       portNumber = 10003
       globalBuddyList = ["Jaquez", "Bona"]
   elif serverName == "Jaquez":
       portNumber = 10004
       globalBuddyList = ["Clark", "Campbell"]
   else:
       print("? " + GetServerName())
       return


   serverConnect = await asyncio.start_server(
       handle_connection, host="127.0.0.1", port=portNumber
   )
   await serverConnect.serve_forever()




# Get latitude and longitude
def GetLatAndLong(coord):
   coordSub = coord[1:]
   coordList = []
   try:
       longSub = coordSub.index("+")
       coordList.append(coord[0:longSub])
       coordList.append(coord[longSub + 1 :])
       return coordList
   except:
       longSub = coordSub.index("-")
       coordList.append(coord[0:longSub])
       coordList.append(coord[longSub + 1 :])
       return coordList




async def handle_connection(reader, writer):
   data = await reader.readline()
   dataDecoded = data.decode()
   dataParsed = dataDecoded.split()
   await HandleData(reader, writer, data)




# Handle different commands
async def HandleData(reader, writer, data):
   name = data.decode()
   nameList = name.split()
   whichCommand = nameList[0]
   if whichCommand == "IAMAT":
       await HandleDataIAMAT(reader, writer, data)
   elif whichCommand == "WHATSAT":
       await HandleDataWHATSAT(reader, writer, data)
   elif whichCommand == "requestData":
       await SendData(reader, writer, nameList[2], nameList[1])
   elif whichCommand == "sentData":
       await ReceivedData(reader, writer, data)
   elif whichCommand == "sentOtherData":
       await ReceiveOtherData(reader, writer, data)




async def HandleDataIAMAT(reader, writer, data):
   if data.decode() in globalDataList:
       serverTime = time.time()
       name = data.decode()
       nameList = name.split()
       timeDifference = serverTime - float(nameList[3])
       message = (
           "AT "
           + globalServerName
           + " "
           + str("+" + "{:.9f}".format(timeDifference))
           + " "
       )
       globalWHATMessage.append(message + name.split(" ", 1)[1])
       writer.write(message.encode() + name.split(" ", 1)[1].encode())
       await writer.drain()
       writer.close()
   else:
       globalDataList.append(data.decode())
       serverTime = time.time()
       name = data.decode()
       nameList = name.split()
       timeDifference = serverTime - float(nameList[3])
       message = (
           "AT "
           + globalServerName
           + " "
           + str("+" + "{:.9f}".format(timeDifference))
           + " "
       )
       globalWHATMessage.append(message + name.split(" ", 1)[1])
       writer.write(message.encode() + name.split(" ", 1)[1].encode())


       for index in range(len(globalBuddyList)):
           for i in range(len(globalNameAndPort)):
               if globalBuddyList[index] == globalNameAndPort[i]["ServerName"]:
                   reader, writer = await asyncio.open_connection(
                       "127.0.0.1", globalNameAndPort[i]["ServerPort"]
                   )
                   writer.write(data)
                   writer.close()




# This is for when a server needs to  send data to a server that has gone down and lost its data list
async def SendData(reader, writer, data, port):
   reader, writer = await asyncio.open_connection("127.0.0.1", port=int(port))
   newData = ""
   tempData = []
   for i in range(len(globalDataList)):
       tempData.append(globalDataList[i])
   tempData.reverse()
   for i in range(len(tempData)):
       tempList = tempData[i].split()
       if tempList[1] == data:
           newData = tempData[i] + " "
   sendData = "sentData " + newData
   writer.write(sendData.encode())
   await writer.drain()
   writer.close()


   reader, writer = await asyncio.open_connection("127.0.0.1", port=int(port))


   newOtherData = ""
   tempOtherData = []
   for i in range(len(globalWHATMessage)):
       tempOtherData.append(globalWHATMessage[i])
   tempOtherData.reverse()
   for i in range(len(tempOtherData)):
       tempList = tempOtherData[i].split()
       if tempList[3] == data:
           newOtherData = tempOtherData[i] + " "
   sendOtherData = "sentOtherData " + newOtherData
   writer.write(sendOtherData.encode())
   await writer.drain()
   writer.close




# Receive globalDataList value from different server
async def ReceivedData(reader, writer, data):
   dataDecode = data.decode()
   dataList = dataDecode.split()
   newDataList = dataList[1:]
   newData = ""
   for i in range(len(newDataList)):
       newData += newDataList[i] + " "
   if newData not in globalDataList:
       globalDataList.append(newData)




# Receive globalWHATMessage value from different server
async def ReceiveOtherData(reader, writer, data):
   dataDecode = data.decode()
   dataList = dataDecode.split()
   newDataList = dataList[1:]
   newData = ""
   for i in range(len(newDataList)):
       if i == len(newDataList) - 1:
           newData += newDataList[i]
       else:
           newData += newDataList[i] + " "
   if newData not in globalDataList:
       globalWHATMessage.append(newData)




async def NextStep(reader, writer, data):
   name = data.decode()
   nameList = name.split()
   clientID = nameList[1]
   radius = nameList[2]
   maxInfo = int(nameList[3])


   # Since appending a value to a list appends it to the end, we want a  copy of the reverse of that list to get  the last first
   tempDataList = []
   resultLoc = []
   tempWHATMessage = []
   resultMessage = ""
   resultID = ""
   for i in range(len(globalDataList)):
       tempDataList.append(globalDataList[i])
   for i in range(len(globalWHATMessage)):
       tempWHATMessage.append(globalWHATMessage[i])
   tempDataList.reverse()
   tempWHATMessage.reverse()
   for i in range(len(tempDataList)):
       tempData = tempDataList[i].split()
       IDinData = tempData[1]
       if clientID == IDinData:
           resultID = clientID
           resultLoc = GetLatAndLong(tempData[2])
   for i in range(len(tempWHATMessage)):
       tempDataTwo = tempWHATMessage[i].split()
       IDInDataTwo = tempDataTwo[3]
       if clientID == IDInDataTwo:
           resultMessage = tempWHATMessage[i]


   url = (
       "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="
       + str(resultLoc[0])
       + "%2C"
       + str(resultLoc[1])
       + "&radius="
       + (str(int(radius) * 1000))
       + "&key="
       + globalAPIKey
   )
   JSONresult = ""
   async with aiohttp.ClientSession() as session:
       async with session.get(url) as resp:
           JSONresult = await resp.text()
   sendJSON = json.loads(JSONresult)
   finalJSON = sendJSON["results"]
   JSONValues = ""
   if len(finalJSON) <= maxInfo:
       JSONValues = str(resp.text())
   else:
       sendJSON["results"] = sendJSON["results"][0 : int(maxInfo)]
       JSONValues = json.dumps(sendJSON, sort_keys=True, indent=4)


   resultResult = resultMessage + "\n" + JSONValues + "\n\n"
   newresultResult = resultResult.replace("'", '"')
   writer.write(newresultResult.encode())
   await writer.drain()
   writer.close()




async def HandleDataWHATSAT(reader, writer, data):
   name = data.decode()
   nameList = name.split()
   clientID = nameList[1]
   radius = nameList[2]
   maxInfo = int(nameList[3])
   originalWriter = writer
   # Since appending a value to a list appends it to the end, we want a  copy of the reverse of that list to get  the last first
   tempDataList = []
   resultLoc = []
   tempWHATMessage = []
   resultMessage = ""
   resultID = ""
   for i in range(len(globalDataList)):
       tempDataList.append(globalDataList[i])
   for i in range(len(globalWHATMessage)):
       tempWHATMessage.append(globalWHATMessage[i])
   tempDataList.reverse()
   tempWHATMessage.reverse()
   for i in range(len(tempDataList)):
       tempData = tempDataList[i].split()
       IDinData = tempData[1]
       if clientID == IDinData:
           resultID = clientID
           resultLoc = GetLatAndLong(tempData[2])
   for i in range(len(tempWHATMessage)):
       tempDataTwo = tempWHATMessage[i].split()
       IDInDataTwo = tempDataTwo[3]
       if clientID == IDInDataTwo:
           resultMessage = tempWHATMessage[i]
   if resultID == "":
       # resultID would be "" if the server went down but others are still running
       # So request the data from other servers and use that to use for Places
       for index in range(len(globalBuddyList)):
           for i in range(len(globalNameAndPort)):
               if globalBuddyList[index] == globalNameAndPort[i]["ServerName"]:
                   reader, writer = await asyncio.open_connection(
                       "127.0.0.1", globalNameAndPort[i]["ServerPort"]
                   )
                   requestDataMessage = (
                       "requestData " + str(globalMyPort) + " " + clientID
                   )
                   writer.write(requestDataMessage.encode())
                   await writer.drain()
                   writer.close()
                   await asyncio.sleep(2)
                   await NextStep(reader, originalWriter, data)
   else:
       url = (
           "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="
           + str(resultLoc[0])
           + "%2C"
           + str(resultLoc[1])
           + "&radius="
           + (str(int(radius) * 1000))
           + "&key="
           + globalAPIKey
       )
       JSONresult = ""
       async with aiohttp.ClientSession() as session:
           async with session.get(url) as resp:
               JSONresult = await resp.text()
       sendJSON = json.loads(JSONresult)
       finalJSON = sendJSON["results"]
       JSONValues = ""
       if len(finalJSON) <= maxInfo:
           JSONValues = str(resp.text())
       else:
           sendJSON["results"] = sendJSON["results"][0 : int(maxInfo)]
           JSONValues = json.dumps(sendJSON, sort_keys=True, indent=4)


       resultResult = resultMessage + JSONValues + "\n\n"
       newresultResult = resultResult.replace("'", '"')
       writer.write(newresultResult.encode())
       await writer.drain()
       writer.close()




if __name__ == "__main__":
   asyncio.run(main())
