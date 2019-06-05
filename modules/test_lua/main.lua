main = {}


function main.on_message(await, client, message, ...)
    print("I LOVE LUA")
    print(message.content)
    if message.author.bot == false then
        await(message.channel.send("Tu n'es pas un bot"))
    end
end

return main