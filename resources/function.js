let chat_list = [
  /*{

    owner : 0,
    type : 0,
    text : "하이루?",
    time : "몰? 루?",
}*/
];

function profile_view(img, sender) {
  return `
    <div class="profile"> 
        <img src="${img}" alt="" onerror="this.style.backgroundColor = 'white';""/>
        <text>${sender.name}</text>
    </div>    
    `;
}

function dateTimeFormat(dateString) {
  let format = "H:mm (A)";
  let date = new Date(dateString);
  let hours = date.getHours();
  let minutes = `${date.getMinutes()}`.padStart(2, "0");
  let ampm = hours >= 12 ? "pm" : "am";
  hours = hours % 12 || 12;
  format = format.replace("H", hours).replace("mm", minutes).replace("A", ampm);
  return format;
}

function msg_view(owner, chat, profileVisible = false, timeVisible = true) {
  return `<div>
        ${
          profileVisible && owner === 1
            ? profile_view(
                `/resources/profile_${chat.sender_id % 5}.png`,
                chat.sender
              )
            : ""
        }
        <div class="message ${owner === 1 ? "from-other" : "from-me"}">
            <div class="time">${
              timeVisible ? dateTimeFormat(chat.created_at) : ""
            }</div>
            ${
              chat.message_type === "text"
                ? `<div class="text">${chat.message.replaceAll(
                    "\n",
                    "<br>"
                  )}</div>`
                : ""
            }
            ${
              chat.message_type === "image"
                ? `<div class="chat-image"><img src="/${chat.message}" alt=""/></div>`
                : ""
            }
            ${
              chat.message_type === "video"
                ? `<div class="chat-video"><video src="/${chat.message}" alt="" controls/></div>`
                : ""
            }
            
        </div>
        </div>
        
    `;
}

function chatDateHead() {
  return `
    <div style="display: flex; justify-content: center;">
        <div class="date-container">
            <span>${new Date().toLocaleDateString([], {
              year: "numeric",
              month: "long",
              day: "numeric",
            })}</span>
        </div>
    </div>
    `;
}

let user = {};
let chatroom_id = "";

function getParameterByName(name) {
  let url = window.location.href;
  name = name.replace(/[\[\]]/g, "\\$&");
  let regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)");
  let results = regex.exec(url);
  if (!results) {
    return null;
  }
  if (!results[2]) {
    return "";
  }
  return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function fetchUser() {
  $.ajax({
    type: "GET",
    url: "/user/me",
    success: function (response) {
      user = response;
      listen_websocket();
      fetchChatList();
    },
    error: function (error) {
      alert("로그인이 필요합니다.");
      window.location.href = "/login";
    },
  });
}

function fetchChatList() {
  chat_list = [];
  $.ajax({
    type: "GET",
    url: `/chatroom/${chatroom_id}/message`,
    success: function (response) {
      chat_list = response;
      renderChat();
    },
  });
}

function renderChat() {
  $("#chat-left").empty();
  $("#chat-left").append(chatDateHead());

  let i = 0;
  chat_list.forEach((chat) => {
    appendChatView(chat, chat.sender_id == user.id ? 0 : 1, i);
    i = i + 1;
  });
}
const appendChatResponse = (chat, owner) => {
  chat_list.push(chat);
  if (chat_list.length > 1) {
    //remove last chat header
    $("#chat-left").children().last().remove();
    appendChatView(
      chat_list[chat_list.length - 2],
      chat_list[chat_list.length - 2].sender_id == user.id ? 0 : 1,
      chat_list.length - 2
    );
  }
  appendChatView(chat, owner, chat_list.length - 1);
};

const appendChatView = (chat, owner, idx) => {
  const prevChat = chat_list[idx - 1];
  const nextChat = chat_list[idx + 1];
  const diffentWithPrev =
    prevChat == undefined ||
    prevChat.sender_id != chat.sender_id ||
    new Date(chat.created_at).getMinutes() !=
      new Date(prevChat.created_at).getMinutes();
  const diffentWithNext =
    nextChat == undefined ||
    nextChat.sender_id != chat.sender_id ||
    new Date(nextChat.created_at).getMinutes() !=
      new Date(chat.created_at).getMinutes();

  appendChat(chat, owner, diffentWithNext, diffentWithPrev);
};

function appendChat(chat, owner, timeVisible, profileVisible) {
  $("#chat-left").append(msg_view(owner, chat, profileVisible, timeVisible));

  $("#chat-left").scrollTop($("#chat-left")[0].scrollHeight);
}

function sendMsg() {
  let text = $("#input-left").val();
  text = text.trim();
  if (text == "") {
    return;
  }

  $("#input-left").val("");
  $("#send-left").css("background-color", "#e0e0e0");

  $.ajax({
    type: "POST",
    url: `/chatroom/${chatroom_id}/message`,
    contentType: "application/json",
    data: JSON.stringify({
      message_type: "text",
      message: text,
      sender_id: user.id,
    }),
    success: function (response) {
      $("#chat-left").scrollTop($("#chat-left")[0].scrollHeight);
      appendChatResponse(response, 0);
    },
  });

  renderChat();
  $("#chat-left").scrollTop($("#chat-left")[0].scrollHeight);
}

function sendMediaInput(type) {
  let file = $(`#input-${type}`)[0].files[0];
  if (file == undefined) {
    return;
  }
  sendMedia(file, type);
}

function sendMedia(file, type) {
  let formData = new FormData();
  formData.append("upload_file", file);
  formData.append("sender_id", user.id);
  formData.append("type", type);

  $.ajax({
    type: "POST",
    url: `/chatroom/${chatroom_id}/message/file`,
    data: formData,
    processData: false,
    contentType: false,
    success: function (response) {
      $("#chat-left").scrollTop($("#chat-left")[0].scrollHeight);
      appendChatResponse(response, 0);
    },
  });
}

$(document).ready(() => {
  chatroom_id = window.location.href.split("/").pop();
  fetchUser();

  //if input is empty, make send button disabled with gray color
  $("#input-left").on("input", function () {
    if ($(this).val().trim() == "") {
      $("#send-left").css("background-color", "#e0e0e0");
    } else {
      $("#send-left").css("background-color", "#ffeb3b");
    }
  });

  $("#input-left").keyup(function (e) {
    if (e.which == 13 && !e.shiftKey) {
      sendMsg(0);
      $("#input-left").blur();
      setTimeout(() => {
        $("#input-left").focus();
      }, 10);
    }
  });
});

let socket;
function listen_websocket() {
  socket = new WebSocket("ws://localhost:8000/message-ws");
  socket.onopen = function (event) {
    console.log("Connection established");
  };
  socket.onmessage = function (event) {
    const chat = JSON.parse(event.data);
    console.log(chat);
    console.log(event.data);
    console.log(chat.room_id, chatroom_id);
    if (chat.sender_id == user.id) {
      return;
    }
    if (chat.room_id != chatroom_id) {
      return;
    }
    appendChatResponse(chat, 1);
  };
  socket.onclose = function (event) {
    console.log("Connection closed");
  };
}
