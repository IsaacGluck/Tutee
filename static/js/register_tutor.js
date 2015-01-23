document.getElementById("add").addEventListener('click', addMenu);

document.getElementById("counter").setAttribute("value", "0");
init();


function init() {
  
    var menus = document.getElementsByClassName("m");
    for (var i=0; i<menus.length;i++) {
	menus[i].addEventListener('mouseover', showdrop);
	menus[i].addEventListener('mouseout', hidedropstart);
    }


    var dropdowns = document.getElementsByClassName("d2");
    for (var i =0; i < dropdowns.length;i++) {
	//console.log(dropdowns[i]);
	dropdowns[i].addEventListener('mouseover', processdrop);
	dropdowns[i].addEventListener('mouseout', hidedropstart);
    }

    var subs = document.getElementsByClassName("d2 d2F 2");
    for (var i=0; i < subs.length;i++) {
	subs[i].addEventListener('mouseover', showsub);
    }

    var subss = document.getElementsByClassName("d2 d2F 3");
    for (var i=0; i < subss.length;i++) {
	subss[i].addEventListener('mouseover', showsub);
    }

    var subs2  = document.getElementsByClassName("s2");
    for (var i=0; i < subs2.length;i++) {
	subs2[i].addEventListener('mouseover', processsub);
	subs2[i].addEventListener('mouseout', hidedropstart);
    }


<<<<<<< Updated upstream
    var days = document.getElementsByClassName("d2 d2F 1");
=======
    var days = document.getElementsByClassName("d2 d2F 1 day");
>>>>>>> Stashed changes
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
    xhr.open('GET', '../static/html/dropdown.html', true);
    xhr.onreadystatechange= function() {
	if (this.readyState!==4) return;
	if (this.status!==200) return;
	result =  String(this.responseText).replace(/\{\{n\}\}/g, val);
	newM.innerHTML= result;
	cur.appendChild(newM);
	init();
    };
    xhr.send();
}
