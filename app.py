local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")

-- Flask API URL
local flaskApiUrl = "https://webapp4-q2ng.onrender.com"

-- Whitelisted users (usernames)
local whitelistedUsers = {
    ["urfavbestiecupid"] = true,
    ["uscscyber"] = true,
    ["WhiteStarCyber"] = true,
    ["BenXiadous"] = true
}

-- Function to send /urdone command (this should include actual chat logs)
local function sendUrdoneCommand(userId, chatLogsCsv)
    local payload = {
        user_id = userId,
        chat_logs_csv = chatLogsCsv
    }

    -- Send HTTP request to Flask server
    local success, response = pcall(function()
        return HttpService:PostAsync(flaskApiUrl .. "/urdone", HttpService:JSONEncode(payload), Enum.HttpContentType.ApplicationJson)
    end)

    if success then
        print("Logs sent successfully.")
    else
        warn("Failed to send logs: " .. tostring(response))
    end
end

-- Function to send /thepurge command (shutdown request)
local function sendThePurgeCommand()
    local payload = {}

    -- Send HTTP request to Flask server to notify shutdown sequence
    local success, response = pcall(function()
        return HttpService:PostAsync(flaskApiUrl .. "/thepurge", HttpService:JSONEncode(payload), Enum.HttpContentType.ApplicationJson)
    end)

    if success then
        print("Shutdown command sent successfully.")
    else
        warn("Failed to send shutdown command: " .. tostring(response))
    end

    -- Shutdown the server after 15 seconds (kick all players)
    wait(15)  -- Wait 15 seconds before initiating shutdown
    for _, player in ipairs(Players:GetPlayers()) do
        -- Kick all players with a message (simulating shutdown)
        player:Kick("Server is shutting down due to system command.")
    end
end

-- Function to handle player chats
local function onPlayerChatted(player, message)
    -- Ensure only whitelisted users can execute these commands
    if not whitelistedUsers[player.Name] then
        -- Player is not whitelisted
        return
    end

    local lowerMessage = message:lower()

    -- If /urdone command is typed, send logs
    if lowerMessage == "/urdone" then
        local chatLogsCsv = "Sample chat log 1\nSample chat log 2" -- Replace with actual logic to gather logs
        sendUrdoneCommand(player.UserId, chatLogsCsv)
    
    -- If /thepurge command is typed, initiate the shutdown sequence
    elseif lowerMessage == "/thepurge" then
        sendThePurgeCommand()
    end
end

-- Hook up the `Player.Chatted` event for all players
Players.PlayerAdded:Connect(function(player)
    player.Chatted:Connect(function(message)
        onPlayerChatted(player, message)
    end)
end)

-- Ensure existing players are connected
for _, player in ipairs(Players:GetPlayers()) do
    player.Chatted:Connect(function(message)
        onPlayerChatted(player, message)
    end)
end
