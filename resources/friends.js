function append_friends(friend) {
  const friend_view = `
    <div class="friend-item">
              <img src="${friend.profile_img}" />
              <p>${friend.username}</p>
             
            </div>
    `;

  $("#friends-holder").append(friend_view);
}

function append_user(user) {
  const user_view = `
    <div class="user-profile-item">
              <img src="${user.profile_img}" />
              <p>${user.username}</p>
              <h5>상태메세지+</h5>
            </div>
    `;

  $("#user-holder").append(user_view);
}

$(document).ready(() => {
  append_user({
    profile_img: "/resources/profile_1.png",
    username: "김철수",
  });

  append_friends({
    profile_img: "/resources/profile_1.png",
    username: "김철수",
  });
  append_friends({
    profile_img: "/resources/profile_1.png",
    username: "김철수",
  });
});
