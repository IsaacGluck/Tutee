document.getElementById("add").addEventListener('click', addMenu);

document.getElementById("counter").setAttribute("value", "0");
init_times();


function init_times() {


    var days = document.getElementsByClassName("d2 d2F 1 day");

    for (var i=0; i< days.length;i++) {
	
	days[i].addEventListener('click', setDay);
    }

    var hours1 = document.getElementsByClassName("s2 2 hours");
    for (var i=0; i < hours1.length;i++) {
	hours1[i].addEventListener('click',setHour);
    }


    var hours2 = document.getElementsByClassName("s2 3 hours2");
    for (var i=0; i < hours2.length;i++) {
	hours2[i].addEventListener('click',setHour);
    }

    var minutes1 = document.getElementsByClassName("s2 2 minutes");
    for (var i=0; i< minutes1.length; i++) {
	minutes1[i].addEventListener('click', setMinute);
    }


    var minutes2 = document.getElementsByClassName("s2 3 minutes2");
    for (var i=0; i< minutes2.length; i++) {
	minutes2[i].addEventListener('click', setMinute);
    }


    var type1 = document.getElementsByClassName("s2 2 types");
    for (var i=0; i< type1.length; i++) {
	type1[i].addEventListener('click', setType);
    }


    var type2 = document.getElementsByClassName("s2 3 types2");
    for (var i=0; i< type2.length; i++) {
	type2[i].addEventListener('click', setType);
    }

}


//add another dropdown menu for another day
function addMenu(e) {
    var val = "" + (parseInt(document.getElementById("counter").getAttribute("value")) + 1);
    document.getElementById("counter").setAttribute("value", val);
    var cur = document.getElementById("dropdowns");
    //var cur = document.getElementById("menu" + (parseInt(val)- 1));
    newM = document.createElement("div");
    newM.setAttribute("id", ("menu" + val));

    var xhr= new XMLHttpRequest();
    xhr.open('GET', '../static/html/dropdown.html?=1', true);
    xhr.onreadystatechange= function() {
	if (this.readyState!==4) return;
	if (this.status!==200) return;
	result =  String(this.responseText).replace(/\{\{n\}\}/g, val);
	newM.innerHTML= result;
	cur.appendChild(newM);
	init();
	init_times();
    };
    xhr.send();
}
