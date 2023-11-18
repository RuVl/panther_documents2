// Данные о товарах из localStorage
let cart_object = JSON.parse(localStorage.getItem("cart"));

// Элементы корзины
const empty_cart_div = document.querySelector(".empty_cart");
const cart_page_wrap_div = document.querySelector(".cart_page_wrap");

const final_price = document.getElementById("final_price");
const currency_factor = parseFloat(final_price.getAttribute('currency-factor').replace(',', '.'));
const currency_symbol = final_price.parentElement.querySelector('.currency-symbol').innerText;

const product_list_div = document.querySelector(".product_list");

// const lang_code = document.getElementById("current-language").innerText;

const get_products_form = document.getElementById("get-products-form");

const escapeHTML = str => str.toString().replace(/[&<>'"]/g, tag => ({
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  "'": '&#39;',
  '"': '&quot;'
}[tag] || tag));

function change_currency(price) {
  if (currency_factor === 1)
    return Math.ceil(price * 100) / 100;
  return Math.ceil(price * currency_factor);
}

function showProducts() {
  let html = '';

  for (const p_type in cart_object) {
    for (let p of cart_object[p_type]) {
      // noinspection HtmlUnknownAttribute
      html += `
      <div class="product_item" product-id="${escapeHTML(p.id)}" product-type="${escapeHTML(p_type)}">
          <div class="name_div"><span>${escapeHTML(p.title)}</span></div>
          <div class="quantity_div">
              <div class="counter_ co_mi ${p.count === 1 ? 'disabled' : ''}"><i class="fa-solid fa-minus"></i></div>
              <div class="quantity">${escapeHTML(p.count)}</div>
              <div class="counter_ co_pl ${p.count === p.max_count ? 'disabled' : ''}"><i class="fa-solid fa-plus"></i></div>
          </div>
          <div class="price_div">
            <span class="price">${escapeHTML(change_currency(p.price))}</span>
            <span class="currency-symbol">${currency_symbol}</span>
          </div>
          <div class="remove_div"><span onclick="return delete_product(this)">${gettext('Delete')}</span></div>
      </div>
      `;
    }
  }

  product_list_div.innerHTML = html;
  product_list_div.querySelectorAll('.counter_')  // События счётчика
    .forEach(el => el.addEventListener('click', counter_change));
}

// Изменение количества товаров (co_pl, co_mi)
function counter_change(_) {
  if (this.classList.contains("disabled"))
    return;

  const product_item = this.parentElement.parentElement;
  const quantity = product_item.querySelector('.quantity');
  const product_id = parseInt(product_item.getAttribute("product-id"));
  const p_type = product_item.getAttribute("product-type");

  const index = cart_object[p_type].findIndex(el => el.id === product_id);

  let current_count = cart_object[p_type][index].count;
  if (this.classList.contains('co_mi')) {
    if (current_count > 2) {
      current_count--;
      this.nextElementSibling.nextElementSibling.classList.remove("disabled");
    } else {
      current_count = 1;
      this.classList.add("disabled");
    }
  } else if (this.classList.contains('co_pl')) {
    if (current_count < cart_object[p_type][index].max_count - 1) {
      current_count++;
      this.previousElementSibling.previousElementSibling.classList.remove("disabled");
    } else {
      current_count = cart_object[p_type][index].max_count;
      this.classList.add("disabled");
    }
  } else return;
  quantity.textContent = current_count.toString();

  cart_object[p_type][index].count = current_count;

  updateCartObject();
  updateFinalPrice();
}

function delete_product(btn) {
  const product_item = btn.parentElement.parentElement;
  const product_id = parseInt(product_item.getAttribute("product-id"));
  const p_type = product_item.getAttribute("product-type");

  const index = cart_object[p_type].findIndex(el => el.id === product_id);

  cart_object[p_type].splice(index, 1);
  product_item.remove();

  updateCartCounter(cart_object);
  updateCartObject(cart_object);
  updateFinalPrice();

  if (Object.keys(cart_object).length === 0) {
    cart_page_wrap_div.classList.add("inactive");
    empty_cart_div.classList.remove("inactive");
  }

  return false; // event.preventDefault
}

function updateFinalPrice() {
  let total_price = 0;
  for (const p_type in cart_object)
    for (const p of cart_object[p_type])
      total_price += p.price * parseInt(p.count);

  total_price = change_currency(total_price);
  final_price.textContent = total_price.toString();
}

function update_products() {
  /* products_data: {
    product_type: [
      {
        id: 1,
        count: 3
      }
    ]
  } */

  /* cart_object: {
    "passports": [
      {
        "id": 3,
        "price": 10,
        "max_count": 3,
        "count": 2,
        "title": "ID карта",
        "country": {
          "title": "Австралия",
        }
      }
    ]
  } */

  let formData = new FormData(get_products_form);

  let products_data = {};
  for (const p_type in cart_object) {
    products_data[p_type] = [];
    for (const p of cart_object[p_type])
      products_data[p_type].push({
        id: p.id,
        count: p.count !== 0 ? p.count : 0,
      });
  }

  formData.append('products', JSON.stringify(products_data));

  return fetch(get_products_form.action, {
    method: 'POST',
    body: formData,
  }).then(resp => resp.json())
    .then(data => {
      if (data == null) return;

      // Fix price (maybe not optimised)
      for (const p_type in data) {
        for (let i = 0; i < data[p_type].length; i++) {
          const product = data[p_type][i];
          data[p_type][i].price = parseFloat(product.price);

          for (const p of products_data[p_type]) {
            if (p.id === product.id) {
              data[p_type][i].count = p.count < product.max_count ? p.count : product.max_count;
              break;
            }
          }
        }
      }

      updateCartObject(data);
    }).catch(() => console.error("Can't get products!"));
}

function updateCartObject(data=null) {
  if (data != null) cart_object = data;
  localStorage.setItem('cart', JSON.stringify(cart_object));
}

window.addEventListener("DOMContentLoaded", async () => { // Загружаем корзину как только весь DOM получен
  if (cart_object != null && Object.keys(cart_object).length !== 0) {
    cart_page_wrap_div.classList.remove("inactive");
    await update_products();
    updateCartCounter(cart_object);
    showProducts();
    updateFinalPrice();
  } else empty_cart_div.classList.remove("inactive");
})