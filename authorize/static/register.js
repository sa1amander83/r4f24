console.log('hello from register')
function show_hide_password1(target){

	var input = document.getElementById('id_password1');

	if (input.getAttribute('type') == 'password') {

		target.classList.add('view');

		input.setAttribute('type', 'text');

	} else {

		target.classList.remove('view');

		input.setAttribute('type', 'password');

	}

	return false;

}
  function show_hide_password2(target){

	var input = document.getElementById('id_password2');

	if (input.getAttribute('type') == 'password') {

		target.classList.add('view');

		input.setAttribute('type', 'text');

	} else {

		target.classList.remove('view');

		input.setAttribute('type', 'password');

	}

	return false;

}
$(function() {
  //задание заполнителя с помощью параметра placeholder
  $("#username").mask("999999");

});