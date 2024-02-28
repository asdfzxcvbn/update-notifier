import std/[os, re, uri, json, jsonutils, times, tables, rdstdin, strutils, strformat, httpclient]

#[

side note: this is wayy better than the python version, even though im writing this pretty late at night
tbh it was surprisingly easy to recreate and it gave me another learning opportunity for nim
i might still be able to improve this, but this "beta" version is practically good enough.

LEARN NIM LEARN NIM LEARN NIM LEARN NIM I LOVE NIM <3
https://nim-lang.org

]#

const options: array[2, string] = ["start", "add"]
let
    confPath: string = "~/.config/updateNotifier".expandTilde
    dataPath: string = &"{confPath}/monitor.json"

var
    token: string
    chatId: string

proc makeRequest(url: string, specifyTime: bool = true): JsonNode =
    var client: HttpClient = newHttpClient()
    defer: client.close()

    let
        unix: int64 = getTime().toUnix
        urlAdd: string = if specifyTime: &"&{unix}={unix}" else: ""
        resp: string = client.getContent(url & urlAdd)

    return resp.parseJson()

proc getExistingData(): Table[string, Table[string, string]] =
    if not fileExists(dataPath):
        writeFile(dataPath, "{}")
        return initTable[string, Table[string, string]]()

    # assume file exists from this point
    return parseFile(dataPath).jsonTo(Table[string, Table[string, string]])

proc getAppVersion(appId: string, country: string, includeAppName: bool = false): Table[string, string] =
    var
        req: JsonNode = makeRequest(&"https://itunes.apple.com/lookup?limit=1&id={appId}&country={country}")
        version: string = req["results"][0]["version"].getStr()
        name: string = req["results"][0]["trackName"].getStr()

    if includeAppName:
        return {"version": version, "name": name}.toTable
    return {"version": version}.toTable

if not [1, 2].contains(paramCount()) or not options.contains(paramStr(1)):
    quit "[!] usage: upd (start | add <appstore link>)\nexample: upd add https://apps.apple.com/app/id324684580"
elif not confPath.dirExists:  # first time setup
    echo "[?] hi! since you're new, i'm going to need some info.\n"

    token = readLineFromStdin("[<] enter your bot token: ").strip
    chatId = readLineFromStdin("[<] enter your chat id: ").strip
    
    createDir(confPath)
    writeFile(&"{confPath}/conf.json", ${"token": token, "chat": chatId}.toTable)
    echo ""
elif paramStr(1) == "add":  # add new app
    if paramCount() != 2:
        quit "[!] usage: upd add <appstore link>"

    var
        appId: string
        country: string
        req: Table[string, string]
        version: string
        name: string
        data: Table[string, Table[string, string]] = getExistingData()

    try:  # regex in python was much easier but i guess this will work lol
        appId = paramStr(2).findAll(re"(?<=id)(\d{9,10})(?=\?|$)")[0]
        country = paramStr(2).findAll(re"(?<=\/)[a-z]{2}(?=\/)")[0]
    except IndexDefect:
        if appId == "":
            quit "[!] app id not found. are you sure that's a valid link?"
        country = "us"  # if country isn't found, use US by default.

    try:
        req = appId.getAppVersion(country, true)
        version = req["version"]
        name = req["name"]
    except IndexDefect:
        quit "[!] couldn't get latest version! are you sure you can access that link?"

    data[appId] = {"name": name, "version": version, "country": country}.toTable
    writeFile(dataPath, $data)

    quit(&"[*] added {name}!\n[*] current version: {version}", 0)

# can now be assumed that we are STARTING!
block:
    let data: Table[string, string] = parseFile(&"{confPath}/conf.json").jsonTo(Table[string, string])
    token = data["token"]
    chatId = data["chat"]

proc notify(name: string, appId: string, oldVer: string, newVer: string): void =
    var url: string = &"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatId}&text="
    url.add(encodeUrl(&"a new update has been released for {name}!\n\nupdate: {oldVer} -> {newVer}\n\ncheck it out here: https://apps.apple.com/app/id{appId}", false))
    # looks like nothing has changed from the python version! still a shitty ~~function~~ proc!

    discard url.makeRequest(false)

while true:
    var data: Table[string, Table[string, string]] = getExistingData()
    if data.len() == 0:
        quit "[!] you need to add apps to monitor first!"

    for id, info in data.pairs:
        echo "[*] checking " & info["name"] & " .."
        let req: Table[string, string] = id.getAppVersion(info["country"])

        if req["version"] != data[id]["version"]:
            echo "[*] update detected! notifying.."
            notify(info["name"], id, data[id]["version"], req["version"])
            echo "[*] done!\n"
            data[id]["version"] = req["version"]
        else:
            echo "[*] no update detected.\n"

        sleep(5000)  # 5 seconds, to prevent rate limits

    writeFile(dataPath, $data)
    echo "[*] done, checking again in 20 minutes..\n"
    sleep(1200000)  # check every 20 minutes
