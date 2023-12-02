function append_friends(friend) {
  const profileImg =
    friend.user_info.profile_img || "resources/icon_profile_basic.jpeg";
  const friend_view = `
    <div class="friend-item">
              <img src="${profileImg}" />
              <p>${friend.name}</p>
             
            </div>
    `;

  $("#friends-holder").append(friend_view);
}

function append_user(user) {
  $("#user-holder").empty();
  const profileImg =
    user.user_info.profile_img || "resources/icon_profile_basic.jpeg";
  const user_view = `
    <div class="user-profile-item">
              <img src="${profileImg}" />
              <p>${user.name}</p>
              <h5>상태메세지+</h5>
            </div>
    `;

  $("#user-holder").append(user_view);
}

function fetchFriends() {
  $.ajax({
    type: "GET",
    url: "/friend",
    success: function (response) {
      addFriends(response);
    },
  });
}

function fetchUser() {
  $.ajax({
    type: "GET",
    url: "/user/me",
    success: function (response) {
      append_user(response);
    },
  });
}

function addFriends(friends) {
  $("#friends-holder").empty();
  friends.forEach((friend) => {
    append_friends(friend);
  });
}

$(document).ready(() => {
  fetchUser();
  fetchFriends();
});
