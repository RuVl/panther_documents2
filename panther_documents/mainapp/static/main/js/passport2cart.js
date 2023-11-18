let product = {};

const cart_popup = document.querySelector('.popup');

function close_popup() {
	cart_popup.classList.remove('active');
	document.body.classList.remove('body_popup');
}

function add_to_cart() {
	/* cart_object: {
		"passports": [
			{
				"id": 3,
				"price": 10,
				"max_count": 3,
				"count": 2,
				"title": "ID карта",
				"country": {
					"title": "Австралия"
				}
			}
		]
	} */

	let cart_object = JSON.parse(localStorage.getItem('cart')) || {passports: []};

	cart_object.passports.push(product);
	localStorage.setItem('cart', JSON.stringify(cart_object));

	updateCartCounter(cart_object);
}

function counter_change(_) {
  if (this.classList.contains("disabled"))
    return;

  const quantity = this.parentElement.querySelector('.quantity');

  if (this.classList.contains('co_mi')) {
    if (product.count > 2) {
      product.count--;
      this.nextElementSibling.nextElementSibling.classList.remove("disabled");
    } else {
      product.count = 1;
      this.classList.add("disabled");
    }
  } else if (this.classList.contains('co_pl')) {
    if (product.count < product.max_count - 1) {
      product.count++;
      this.previousElementSibling.previousElementSibling.classList.remove("disabled");
    } else {
      product.count = product.max_count;
      this.classList.add("disabled");
    }
  } else return;

	const total = Math.ceil(product.price * product.count * 100) / 100;

  quantity.textContent = product.count.toString();
	popup.querySelector('.price').textContent = total.toString();
}

const popup = document.querySelector('.popup_form > .form_content');
document.addEventListener("DOMContentLoaded", () => {
	document.querySelectorAll('.counter_')
		.forEach(el => el.addEventListener('click', counter_change))

	document.querySelectorAll('.popup_open').forEach(button => {
		button.addEventListener('click', (e) => {
			e.preventDefault();

			const tr = button.closest(".product-tr");
			product = {
				id: parseInt(tr.querySelector('.product-id').textContent),
				title: tr.querySelector('.product-title').textContent,
				max_count: parseInt(tr.querySelector('.product-count').textContent),
				price: tr.querySelector('.price').textContent,
				count: 1, // default
				type: tr.getAttribute('product-type'),
			}

			popup.querySelector('.product_name').textContent = product.title;
			popup.querySelector('.price').textContent = (product.price * product.count).toString();
			popup.querySelector('.quantity').textContent = product.count;

			const co_pl = popup.querySelector('.counter_.co_pl');
			const co_mi = popup.querySelector('.counter_.co_mi');

			if (product.count < product.max_count) co_pl.classList.remove('disabled');
			else co_pl.classList.add('disabled');

			if (product.count === 1) co_mi.classList.add('disabled');
			else co_mi.classList.remove('disabled');

			cart_popup.classList.add('active');
			document.body.classList.add('body_popup');
		})
	});

	document.querySelector('.popup_close').addEventListener('click', close_popup);

	// обработка кнопки добавления товара в корзину
	document.querySelector('.cart_add_btn').addEventListener('click', () => {
		add_to_cart();
		close_popup();
	});

	document.querySelector('.pay_btn').addEventListener('click', () => {
		add_to_cart();
		window.location.assign(window.location.origin + '/cart');
	});
});
