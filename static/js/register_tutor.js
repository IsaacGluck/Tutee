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


