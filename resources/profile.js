function fetchProfile() {
  const urlsplit = window.location.href.split("/");
  const userid = urlsplit[urlsplit.length - 1];

  $.ajax({
    type: "GET",
    url: "/user/" + userid,
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
