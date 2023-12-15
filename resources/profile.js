function getUrlUserId() {
  const urlsplit = window.location.href.split("/");
  const userid = urlsplit[urlsplit.length - 1];
  return userid;
}

function fetchProfile() {
  $.ajax({
    type: "GET",
    url: "/user/" + getUrlUserId(),
    success: function (response) {
      append_profile(response);
    },
  });
}

function append_profile(profile) {
  const profileImg =
    profile.user_info.profile_img || "/resources/icon_profile_basic.jpeg";

  $(".profile-image").attr("src", profileImg);
  $("h1").text(profile.name);
}

$(document).ready(() => {
  fetchProfile();
});

function fetchP2PChatInfo() {
  $.ajax({
    type: "GET",
    url: "/chatroom/p2p/" + getUrlUserId(),
    success: function (response) {
      window.location.href = "/chatroom/" + response.id;
    },
  });
}
