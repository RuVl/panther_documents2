window.addEventListener('DOMContentLoaded', () => {
	const curr_select = document.getElementById("currency-select");
	const form_input = curr_select.querySelector('#curr-picker');
	const selected = curr_select.querySelector(".curr-selected");
	const optionsList = curr_select.querySelectorAll(".option");

	selected.addEventListener("click", () => {
	  curr_select.classList.toggle("active");
	});

	optionsList.forEach(el => {
	  el.addEventListener("click", () => {
	    selected.querySelector('span').textContent = el.querySelector("label").textContent;
	    curr_select.classList.remove("active");
	    form_input.value = el.querySelector('input').value;
	    form_input.form.submit();
	  });
	});
});