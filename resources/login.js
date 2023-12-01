let user = {
  id: -1,
};

function fetchLogin(username, password) {
  $.ajax({
    type: "POST",
    url: "/login",
    data: {
      username: username,
      password: password,
    },
    success: function (response) {
      user = response;
      window.location.href = "/";
    },
    error: function (error) {
      console.log(error);
      alert("계정 정보를 찾을 수 없습니다.");
    },
  });
}

function login() {
  const username = document.getElementById("user-name").value;
  const password = document.getElementById("user-password").value;

  if (!username) {
    alert("아이디를 입력해주세요");
    return;
  }

  if (!password) {
    alert("비밀번호를 입력해주세요");
    return;
  }

  fetchLogin(username, password);
}

$(document).ready(() => {
  $("#login-button").click(() => {
    login();
  });

  $("#register-button").click(() => {
    window.location.href = "/register";
  });
});
