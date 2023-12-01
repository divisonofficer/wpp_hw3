function register() {
  const username = document.getElementById("user-name").value;
  const passwordConfirm = document.getElementById("user-password-check").value;
  const password = document.getElementById("user-password-input").value;

  if (!username) {
    alert("아이디를 입력해주세요");
    return;
  }

  if (!password) {
    alert("비밀번호를 입력해주세요");
    return;
  }

  if (password !== passwordConfirm) {
    alert("비밀번호가 일치하지 않습니다.");
    return;
  }

  $.ajax({
    type: "POST",
    url: "/register",
    data: {
      username: username,
      password: password,
    },
    success: function (response) {
      if (response == "success") {
        fetchLogin(username, password);
      } else {
        alert("회원가입 실패");
      }
    },
    error: function (error) {
      console.log(error);
    },
  });
}

$(document).ready(() => {
  $("#register-confirm-button").click(() => {
    register();
  });
});
