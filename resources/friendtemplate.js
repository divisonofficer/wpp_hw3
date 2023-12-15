function friendTemplate(
  id,
  name,
  img,
  mode,
  onClickBackground = undefined,
  onClickButton = undefined
) {
  //mode : 0 - 친구목록, 1 - 친구추천, 2 - 체크박스 off, 3 - 체크박스 on

  return `    
        <div class="friend-recommend-item" 
        ${onClickBackground && `onclick="${onClickBackground}(${id});"`}}    
        >
        
          <img src="${img || "/resources/icon_profile_basic.jpeg"}" />
          <p>${name}</p>
          ${
            mode === 2
              ? `<img src="/resources/icon_radio_checked.webp"
              class="image-button p12" 
              onclick="${onClickButton}(${id})"/>`
              : ``
          }
          ${
            mode === 3
              ? `<img src="/resources/icon_radio.png" 
              class="image-button p12" 
              onclick="${onClickButton}(${id})"/>`
              : ``
          }
       
          ${
            mode === 1
              ? `<button onclick="${onClickButton}(${id})"><img src="/resources/icon_add_user.png" /></button>`
              : ``
          }
         
        </div>
        `;
}
