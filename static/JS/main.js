var ws = new WebSocket("ws://localhost:8100/websocket");

while(!user){
    var user = prompt("What's your name?");
};

function sendMessage() {
    var messageInput = document.getElementById("send-message");
    var message = messageInput.value;
    var payload = {
        "message": message,
        "user": user
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
    if(messageDict.user === 'Server' && messageDict.message === 'Wipe'){
		document.getElementById("messages").innerHTML = "";
		return;
    }
    var messageBox = document.createElement("div");
    messageBox.setAttribute("id", "individual-message");
    messageBox.className = "messages-box container";
    if(messageDict.user === user){
    	messageBox.innerHTML = '<p class="actual-message">' + '<b>'+messageDict.user+'</b>' + ": " + messageDict.message + '</p>';  
    	document.getElementById("messages").appendChild(messageBox);
    }else{
    	messageBox.innerHTML = '<p class="server-message">' + '<b>'+messageDict.user+'</b>' + ": " + messageDict.message + '</p>';  
    	document.getElementById("messages").appendChild(messageBox);
    }
    var objDiv = document.getElementById("messages");
	objDiv.scrollTop = objDiv.scrollHeight;   
};
