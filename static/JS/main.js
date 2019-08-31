var ws = new WebSocket("ws://localhost:8100/websocket");

function sendMessage() {
    var messageInput = document.getElementById("send-message");
    var message = messageInput.value;
    var payload = {
        "message": message,
        "user": "You"
    }
    // Make the request to the WebSocket.
    ws.send(JSON.stringify(payload));
    // Clear the message from the input.
    messageInput.value = "";
    return false;
}

ws.onmessage = function(evt) {
    var messageDict = JSON.parse(evt.data);
    // Create a div with the format `user: message`.
    var messageBox = document.createElement("div");
    messageBox.className = "messages-box container";
    if(messageDict.user === "You"){
    	messageBox.innerHTML = '<p class="actual-message">' + '<b>'+messageDict.user+'</b>' + ": " + messageDict.message + '</p>';  
    	document.getElementById("messages").appendChild(messageBox);
    }else{
    	messageBox.innerHTML = '<p class="server-message">' + '<b>'+messageDict.user+'</b>' + ": " + messageDict.message + '</p>';  
    	document.getElementById("messages").appendChild(messageBox);
    }
    
};
