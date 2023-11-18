window.addEventListener('DOMContentLoaded', () => {
  const lang_select = document.getElementById("lang-select");
  const form_input = lang_select.querySelector('#lang-picker');
  const selected = lang_select.querySelector(".lang-selected");
  const optionsList = lang_select.querySelectorAll(".option");

  selected.addEventListener("click", () => {
    lang_select.classList.toggle("active");
  });

  optionsList.forEach(el => {
    el.addEventListener("click", () => {
      selected.querySelector('span').textContent = el.querySelector("label").textContent;
      lang_select.classList.remove("active");
      form_input.value = el.querySelector('input').value;
      form_input.form.submit();
    });
  });
});