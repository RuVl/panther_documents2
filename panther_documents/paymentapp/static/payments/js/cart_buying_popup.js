const pay_popup = document.querySelector(".popup");

document.querySelector(".cart_pay_btn").onclick = () => {
  pay_popup.classList.add("active");
  document.body.classList.add("body_popup");
}

document.querySelector(".popup_close").onclick = () => {
  pay_popup.classList.remove("active");
  document.body.classList.remove("body_popup");
}

function send_pay_form(pay_form) {
  let cart_object = JSON.parse(localStorage.getItem("cart"));

  let formData = new FormData(pay_form);

  // Hidden products field widget
  let products_data = [];
  for (const p_type in cart_object)
    for (const p of cart_object[p_type])
      products_data.push({
        type: p.type,
        id: p.id,
        count: p.count
      });

  formData.set('products', JSON.stringify(products_data));

  fetch(pay_form.action, {
    body: formData,
    method: 'POST'
  }).then(resp => resp.json())
    .then(async data => {
      console.log(data);
      document.querySelector('.alert > ul').innerHTML = '';
      if (data['clear_cart'])
        localStorage.removeItem("cart");

      if (data['reload_cart'])
        await update_products();

      if (!data['success']) {
        for (let field in data.errors) {
          console.error(field, data.errors[field]);
          document.querySelector('.alert > ul').append(
            ...data.errors[field].map(err => {
              const li = document.createElement('li');
              li.textContent = `${escapeHTML(field)}: ${escapeHTML(err)}`;
              return li;
            })
          );
        }
      } else {
        console.log(`Go to ${window.location.origin + data['url']}`);
        window.location.assign(window.location.origin + data['url']); // replace will clear document history
      }

    }).catch(reason => console.error(reason));
}