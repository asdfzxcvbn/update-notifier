import std/[os, re, uri, json, jsonutils, times, tables, rdstdin, strutils, strformat, httpclient]

const options: array[2, string] = ["start", "add"]
let confPath: string = "~/.config/updateNotifier".expandTilde
var
    token: string
    chatId: string

proc makeRequest(client: HttpClient, url: string, specifyTime: bool = true): JsonNode =
    let
        unix: int64 = getTime().toUnix
        urlAdd: string = if specifyTime: &"&{unix}={unix}" else: ""
        resp: string = client.getContent(url & urlAdd)

    return resp.parseJson()

proc monitorCount(): int =
    for f in walkFiles(&"{confPath}/monitors/*.json"):
        inc result

proc getAppVersion(client: HttpClient, appId: string, country: string, includeAppName: bool = false): Table[string, string] =
    var req: JsonNode  # if only there was a better way to do this! RIGHT ?! PLEASE ?!!?
    while true:
        try:
            req = client.makeRequest(&"https://itunes.apple.com/lookup?limit=1&id={appId}&country={country}")
            break
        except IOError:
            echo "[!] error while checking version, trying again in 10 seconds..\n"
            sleep(10000)
        except:
            echo "[!] timeout reached, trying again..\n" 

    let
        version: string = req["results"][0]["version"].getStr()
        name: string = req["results"][0]["trackName"].getStr()
        bundle: string = req["results"][0]["bundleId"].getStr()

    if includeAppName:
        return {"version": version, "name": name, "bundle": bundle}.toTable
    return {"version": version}.toTable

if not [1, 2].contains(paramCount()) or not options.contains(paramStr(1)):
    quit "[!] usage: upd (start | add <appstore link>)\n[*] example: upd add https://apps.apple.com/app/id324684580"
elif not confPath.dirExists:  # first time setup
    echo "[?] hi! since you're new, i'm going to need some info.\n"

    token = readLineFromStdin("[<] enter your bot token: ").strip
    chatId = readLineFromStdin("[<] enter your chat id: ").strip
    
    createDir(confPath)
    writeFile(&"{confPath}/conf.json", ${"token": token, "chat": chatId}.toTable)
    echo ""

if paramStr(1) == "add":  # add new app
    if paramCount() != 2:
        quit "[!] usage: upd add <appstore link>"
    createDir(&"{confPath}/monitors")

    var
        appId: string
        country: string
        req: Table[string, string]
        version: string
        name: string
        bundle: string
        data: Table[string, string]

    try:  # regex in python was much easier but i guess this will work lol
        appId = paramStr(2).findAll(re"(?<=id)(\d{9,10})(?=\?|$)")[0]
        country = paramStr(2).findAll(re"(?<=\/)[a-z]{2}(?=\/)")[0]
    except IndexDefect:
        if appId == "":
            quit "[!] app id not found. are you sure that's a valid link?"
        country = "us"  # if country isn't found, use US by default.

    try:
        req = newHttpClient().getAppVersion(appId, country, true)
        version = req["version"]
        name = req["name"]
        bundle = req["bundle"]
    except IndexDefect:  # catch exception raised in `getAppVersion` call (empty results)
        quit "[!] couldn't get latest version! are you sure you can access that link?"

    data = {"name": name, "version": version, "country": country, "appId": appId}.toTable
    writeFile(&"{confPath}/monitors/{bundle}.json", $data)

    quit(&"[*] added {name}!\n[*] current version: {version}", 0)

# can now be assumed that we are STARTING!
block:
    let data: Table[string, string] = parseFile(&"{confPath}/conf.json").jsonTo(Table[string, string])
    token = data["token"]
    chatId = data["chat"]

proc notify(client: HttpClient, name: string, appId: string, oldVer: string, newVer: string): void =
    var url: string = &"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatId}&text="
    url.add(encodeUrl(&"a new update has been released for {name}!\n\nupdate: {oldVer} -> {newVer}\n\ncheck it out here: https://apps.apple.com/app/id{appId}", false))
    # looks like nothing has changed from the python version! still a shitty ~~function~~ proc!

    discard client.makeRequest(url, false)

if monitorCount() == 0:
    quit "[!] you need to add apps to monitor first!"

proc main(): void =
    var client: HttpClient = newHttpClient(timeout = 10000)  # should only need one client for everything
    defer: client.close()  # is this even needed? whatever honestly

    while true:
        for file in walkFiles(&"{confPath}/monitors/*.json"):
            var
                parsed: JsonNode = parseFile(file)
                info: Table[string, string] = parsed.jsonTo(Table[string, string]) 
                id: string = info["appId"]

            echo "[*] checking " & info["name"] & " .."
            let req: Table[string, string] = client.getAppVersion(id, info["country"])

            if req["version"] != info["version"]:
                echo "[*] update detected! notifying.."
                notify(client, info["name"], id, info["version"], req["version"])
                echo "[*] done!\n"
                info["version"] = req["version"]
                writeFile(file, $info)
            else:
                echo "[*] no update detected.\n"

            sleep(5000)  # 5 seconds, to prevent rate limits

        echo "[*] done, checking again in 20 minutes..\n"
        sleep(1200000)

when isMainModule:  # HAHA LOOK AT ME!! FOLLOWING DEFINITELY GREAT CONVENTIONS!!!
    main()
