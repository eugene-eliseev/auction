function click_item(id,item_name,item_id,count,user,server){
	var elem0 = document.getElementById("id");
	var elem1 = document.getElementById("item_name");
	var elem2 = document.getElementById("item_id");
	var elem3 = document.getElementById("item_count");
	var elem4 = document.getElementById("item_user");
	var elem5 = document.getElementById("item_server");

	elem0.value = id
	elem1.innerHTML = item_name;
	elem2.innerHTML = "<b>Id предмета:</b> "+item_id;
	elem3.innerHTML = "<b>Количество:</b> "+count;
	elem4.innerHTML = "<b>Владелец:</b> "+user;
	elem5.innerHTML = "<b>Сервер:</b> "+server;
}

function mouse_enter(event){
	//alert('mouse lasfsdf');
	var elem = document.getElementById(event.target.id);
	elem.classList.add("bg-secondary");
}

function mouse_leave(event){
	//alert('mouse lasfsdf');
	var elem = document.getElementById(event.target.id);
	elem.classList.remove("bg-secondary");
}