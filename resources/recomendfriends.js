// on Document ready (jquery)

$(document).ready(() => {
  fetchRecommendFriends();
});

function fetchRecommendFriends() {
  $.ajax({
    type: "GET",
    url: "/friend/recommend",
    success: function (response) {
      addRecommendFriends(response);
    },
  });
}

function postMakeFriend(friend_id) {
  $.ajax({
    type: "POST",
    url: "/friend/make",
    contentType: "application/json",
    data: JSON.stringify({
      friend_id: friend_id,
    }),
    success: function (response) {
      fetchRecommendFriends();
    },
  });
}

function addRecommendFriends(users) {
  $("#friends-holder").empty();
  users.forEach((user) => {
    $("#friends-holder").append(recommendFriendItem(user));
  });
}

function recommendFriendItem(user) {
  const img = user.user_info.profile_img || "resources/icon_profile_basic.jpeg";
  return `

  <div class="friend-recommend-item">
    <img src="${img}" />
    <p>${user.name}</p>
    <button onclick="postMakeFriend(${user.id})"><img src="resources/icon_add_user.png" /></button>
  </div>

  `;
}
