var curM = null;
var closer = null;
var curSub = null;
var curMenu = null;


function hidedropstart(e){
    closer = window.setTimeout(hidedrop,1000);
}

// display current dropdown menu & close any others open
function showdrop(e) {
    if (closer){
	window.clearTimeout(closer);
	closer = null;
    }
    
    if (curMenu) {
	var open = document.getElementsByClassName("menu" + curMenu);
	for (var i = 0; i < open.length; i++) {
	    open[i].style.visibility = 'hidden';
	}
    }	
    
    
    curSub = null;
    var id = e.toElement.getAttribute("child");
    curM = id;
    curMenu = e.toElement.getAttribute("menu");
    document.getElementById("menu" + curMenu + "-" +id).style.visibility = 'visible';
    var subs = document.getElementsByClassName("d2 " +  curM.slice(1,2) + " menu" + curMenu);
    for (var i =0; i < subs.length; i++) {
	subs[i].style.visibility = 'visible';
    }

}

// show dropdown submenu & close any other subs
function showsub(e) {
    if (closer) {
	window.clearTimeout(closer);
    }
    var el = e.toElement;
    if (curSub) {
	var sub = document.getElementsByClassName(curSub);
	for (var i = 0; i < sub.length; i++) {
	    sub[i].style.visibility = 'hidden';
	}
    }
    if (el.getAttribute("class") == "menu" + curMenu + " d2 d2F " + curM.slice(1,2) + " sub") {
	curSub = el.getAttribute("child");
	var sub = document.getElementsByClassName("menu" + curMenu + " " + curSub);
	for (var i = 0; i < sub.length; i++) {
	    sub[i].style.visibility = 'visible';
	}
	var height = parseInt( window.getComputedStyle(el).height.slice(0,2));
	document.getElementsByClassName("menu" + curMenu + " s " + curM.slice(1,2) + " " + curSub)[0].style.marginTop = "" + parseInt( el.getAttribute("pos") ) * (height) + "px";
    }
}


//hide dropdown menu
function hidedrop(e) {
    var subs = document.getElementsByClassName( "menu" + curMenu );
    for (var i =0; i < subs.length; i++) {
	subs[i].style.visibility = 'hidden';
    }
    curM = null;
    curSub = null;
    curMenu = null;
}


function processdrop(e) {
    if (closer){
	window.clearTimeout(closer);
	closer = null;
    }
    
}

function processsub(e) {
    if (closer) {
	window.clearTimeout(closer);
	closer = null;
    }
}

//if click a day, display result and add to hidden field
function setDay(e) {
    var day = e.toElement.innerHTML;
    var num = e.toElement.getAttribute("day");
    document.getElementById("menu" + num + "-day").innerHTML = day;
    document.getElementById("" + num + "-day").setAttribute("value", day);
}

//if click an hour, display result and add to hidden field
function setHour(e) {
    var hour = e.toElement.innerHTML;
    var parent = e.toElement.getAttribute("parent");
    var num = e.toElement.getAttribute("day");
    document.getElementById("menu" + num + "-" +  parent).innerHTML = hour + ":00"
    checkComplete(curM.slice(1,2),num);
    if (e.toElement.getAttribute("root") == "m2") {
	document.getElementById(num + "-starthour").setAttribute("value", hour);
    }
    else {
	document.getElementById(num + "-endhour").setAttribute("value", hour);
    }
}

//if click a minute, display result and add to hidden field
function setMinute(e) {
    var min = e.toElement.innerHTML;
    var parent = e.toElement.getAttribute("parent");
    var num = e.toElement.getAttribute("day");
    document.getElementById("menu" + num + "-" + parent).innerHTML = " " + min;
    checkComplete(curM.slice(1,2),num);
    if (e.toElement.getAttribute("root") == "m2") {
	document.getElementById(num+ "-startminute").setAttribute("value", min.slice(1,3));
    }
    else {
	document.getElementById(num + "-endminute").setAttribute("value", min.slice(1,3));
    }
}

//if click type, display result & add to hidden field
function setType(e) {
    var type = e.toElement.innerHTML;
    var parent = e.toElement.getAttribute("parent");
    var num = e.toElement.getAttribute("day");
    document.getElementById("menu" + num + "-" + parent).innerHTML = type;
    checkComplete(curM.slice(1,2),num);
    if (e.toElement.getAttribute("root") == "m2") {
	document.getElementById(num+"-starttype").setAttribute("value", type);
    }
    else {
	document.getElementById(num+"-endtype").setAttribute("value", type);
    }
}

//check if three components of time are complete, if so displays
function checkComplete(men, num) {
    if (men==2) {
	var hour = document.getElementById("menu" + num + "-hour").innerHTML;
	var min = document.getElementById("menu" + num + "-min").innerHTML;
	var type = document.getElementById("menu" + num + "-type").innerHTML;
	var id = "start"
    }
    else {
	var hour = document.getElementById("menu" + num + "-hour2").innerHTML;
	var min = document.getElementById("menu" + num +"-min2").innerHTML;
	var type = document.getElementById("menu" + num + "-type2").innerHTML;
	var id = "end"
    }
    if (hour != "Hour" && min != "Minute" && type != "Type") {
	var val = hour.slice(0,(hour.length - 3)) + min.slice(1,4) + " " + type;
	document.getElementById("menu" + num + "-" + id).innerHTML = val;
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
    xhr.open('GET', '../static/html/dropdown.html?=2', true);
    xhr.onreadystatechange= function() {
	if (this.readyState!==4) return;
	if (this.status!==200) return;
	result =  String(this.responseText).replace(/\{\{n\}\}/g, val);
	newM.innerHTML= result;
	if (document.getElementById("edit_times") != null) {
	    button = document.createElement("button");
	    button.setAttribute("type", "button");
	    button.setAttribute("class", "del_b");
	    button.setAttribute("id", String(val) + "-del")
	    button.innerHTML = "Delete";
	    if (document.getElementById("save_b").style.visibility == "visible") {
		button.style.visibility = "visible";
		button.addEventListener("click", deleteM);
	    }
	    newM.appendChild(button);
	}
	newM.appendChild( document.createElement("br") );
	newM.appendChild( document.createElement("br") );
	cur.appendChild(newM);
	init();
	init_times();
    };
    xhr.send();
}


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
