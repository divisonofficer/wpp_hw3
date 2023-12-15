let chatroom_list = [];
function fetchChatroomList() {
  fetch("/chatroom/list", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  }).then(async (res) => {
    if (res.status === 200) {
      chatroom_list = await res.json();

      renderChatroomsAll();
    }
  });
}

function redirectToChatroom(chatroom_id) {
  window.location.href = "/chatroom/" + chatroom_id;
}

function renderChatroomsAll() {
  $("#chatrooms-holder").empty();
  chatroom_list.forEach((data) => {
    const messageLabel = data.chat_room.lastest_message
      ? data.chat_room.lastest_message.text
      : "";

    $("#chatrooms-holder").append(`
        <div class="lobby-chatroom">
        <img src="resources/icon_profile_basic.jpeg" />
        <div class="lobby-chatroom-text" onclick="redirectToChatroom(${
          data.chat_room.chatroom_id
        });">
          <h1>${data.chat_room.display_name}</h1>
          <p>${messageLabel}</p>
        </div>
        ${
          data.chat_room.unread_message_count > 0
            ? `
        <div class="lobby-chatroom-notification">
        <h5>오전 10:47</h5>
        <p>${data.chat_room.unread_message_count}</p>
      </div>
        `
            : ``
        }
       
      </div>
        `);
  });
}

$(document).ready(() => {
  fetchChatroomList();
});
