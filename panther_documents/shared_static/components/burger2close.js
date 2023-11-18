document.addEventListener('DOMContentLoaded', () =>
	document.querySelectorAll('.burger').forEach( el =>
		el.addEventListener('click', function() {
	    el.firstElementChild.classList.toggle('is-active');
		})
	)
);