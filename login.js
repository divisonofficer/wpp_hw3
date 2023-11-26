function register() {
  const username = document.getElementById("user-name").value;
  const password = "abcdefg";
  $.ajax({
    type: "POST",
    url: "/register",
    data: {
      username: username,
      password: password,
    },
    success: function (response) {
      if (response == "success") {
        login();
      } else {
        alert("회원가입 실패");
      }
    },
  });
}

let user = {
  id: -1,
};

function login() {
  const username = document.getElementById("user-name").value;
  const password = "abcdefg";
  $.ajax({
    type: "POST",
    url: "/login",
    data: {
      username: username,
      password: password,
    },
    success: function (response) {
      user = response;
      window.location.href = "/?userId=" + user.id;
    },
    error: function (error) {
      console.log(error);
      register();
    },
  });
}

$(document).ready(() => {
  $(".login-button").click(() => {
    login();
  });
});
