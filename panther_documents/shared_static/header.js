// Cart counter
const cart_counter = document.getElementById('cart-counter');

window.addEventListener('DOMContentLoaded', () => {
    const cart_object = JSON.parse(localStorage.getItem('cart'));
    updateCartCounter(cart_object);

    const vertical_menu = document.getElementById('header-menu');
    document.getElementById('menu-control').firstElementChild.onclick = () => {
        vertical_menu.classList.toggle('hide_element_mobile');
    };
});

function updateCartCounter(cart_object) {
	let len = 0;
	for (const p_type in cart_object)
		len += cart_object[p_type].length;
	cart_counter.textContent = len.toString();
}
