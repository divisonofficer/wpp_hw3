friends = [];
friends_chosen = [];

function fetchFriends() {
  $.ajax({
    type: "GET",
    url: "/friend",
    success: function (response) {
      friends = response;
      renderFriends();
    },
  });
}

function toggleFriendChosen(id, option) {
  for (var i = 0; i < friends_chosen.length; i++) {
    if (friends_chosen[i] === id) {
      if (option === false) friends_chosen.splice(i, 1);

      return;
    }
  }
  if (option === true) friends_chosen.push(id);

  renderFriends();
}

function onFriendChosen(id) {
  toggleFriendChosen(id, true);
}

function onFriendUnchosen(id) {
  toggleFriendChosen(id, false);
}

function renderFriend(friend, active, index) {
  const img = friend.img;
  const view = friendTemplate(
    friend.id,
    friend.name,
    img,
    active ? 2 : 3,
    active ? "onFriendUnchosen" : "onFriendChosen",
    active ? "onFriendUnchosen" : "onFriendChosen"
  );
  $("#friend-holder").append(view);
}

function checkFriendChosen(id) {
  for (var i = 0; i < friends_chosen.length; i++) {
    if (friends_chosen[i] == id) {
      return true;
    }
  }
  return false;
}

function renderFriends() {
  $("#friend-holder").empty();
  index = 0;
  friends.forEach(function (friend) {
    if (false /**todo : check friends already in room */) {
      return;
    }
    renderFriend(friend, checkFriendChosen(friend.id), index);

    index += 1;
  });
}

$(document).ready(function () {
  fetchFriends();
});

function createChatroomWithFriends() {
  if (friends_chosen.length == 0) {
    alert("친구를 선택해주세요.");
    return;
  }
  $.ajax({
    type: "POST",
    url: "/chatroom/group",
    data: JSON.stringify({
      friend_ids: friends_chosen,
    }),
    contentType: "application/json",
    success: function (response) {
      window.location.href = "/chatroom/" + response.id;
    },
    fail: function (error) {
      alert(JSON.stringify(error));
    },
  });
}
