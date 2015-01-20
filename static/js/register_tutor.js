var curM = null;
var closer = null;
var curSub = null;
var curMenu = null;
document.getElementById("add").addEventListener('click', addMenu);
init();

function init() {
    console.log("hola");

    var menus = document.getElementsByClassName("m");
    for (var i=0; i<menus.length;i++) {
	console.log(menus[i]);
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


    var days = document.getElementsByClassName("1");
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



function hidedropstart(e){
    closer = window.setTimeout(hidedrop,1000);
}


function showdrop(e) {
    if (closer){
	window.clearTimeout(closer);
	closer = null;
    }
    /*
      if (curM) {
      //document.getElementById(curM).style.visibility = 'hidden';
      var subs = document.getElementsByClassName( curM.slice(1,2) );
      //console.log(subs);
      for (var i =0; i < subs.length; i++) {
      //console.log(subs[i]);
      subs[i].style.visibility = 'hidden';
      }
    */
    
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
    //console.log(curM);
    //document.getElementById(id).style.visibility = 'visible';
    document.getElementById("menu" + curMenu + "-" +id).style.visibility = 'visible';
    var subs = document.getElementsByClassName("d2 " +  curM.slice(1,2) + " menu" + curMenu);
    for (var i =0; i < subs.length; i++) {
	subs[i].style.visibility = 'visible';
    }
}

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
    if (el.getAttribute("class") == "menu" + curMenu + " d2 d2F " + curM.slice(1,2)) {
	curSub = el.getAttribute("child");
	var sub = document.getElementsByClassName("menu" + curMenu + " " + curSub);
	for (var i = 0; i < sub.length; i++) {
	    sub[i].style.visibility = 'visible';
	}
	var height = parseInt( window.getComputedStyle(el).height.slice(0,2));
	document.getElementsByClassName("menu" + curMenu + " s " + curM.slice(1,2) + " " + curSub)[0].style.marginTop = "" + parseInt( el.getAttribute("pos") ) * (height) + "px";
    }
}



function hidedrop(e) {
    //console.log(curM);
    // document.getElementById(curM).style.visibility = 'hidden';
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
/*
  function processdrop2(e) {
  var el = e.toElement;
  if (closer) {
  window.clearTimeout(closer);
  closer = null;
  }
  if (el.getAttribute("class") == "d") {
  curM = el.getAttribute("id");
  }
  else {
  curM = e.toElement.getAttribute("parent");
  }
  //console.log( curM );
  document.getElementById(curM).style.visibility = 'visible';
  }

  function processsub2(e) {
  var el = e.toElement;
  if (closer) {
  window.clearTimeout(closer);
  closer = null;
  }
  if (el.getAttribute("class") == "d") {
  curM = el.getAttribute("id");
  }
  else if (el.getAttribute("class").slice(0,2) == "d2") {
  curM = el.getAttribute("parent");
  }
  else {
  curM = el.getAttribute("root");
  }
  document.getElementById(curM).style.visibility = 'visible';
  var subs = document.getElementsByClassName( curM.slice(1,2) );
  for (var i =0; i < subs.length; i++) {
  subs[i].style.visibility = 'visible';
  }
  }

*/


function setDay(e) {
    var day = e.toElement.innerHTML;
    var num = e.toElement.getAttribute("day");
    document.getElementById("menu" + num + "-day").innerHTML = day;
    document.getElementById("" + num + "-day").setAttribute("value", day);
}

function setHour(e) {
    console.log(e.toElement);
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

function addMenu(e) {
    var val = "" + (parseInt(document.getElementById("counter").getAttribute("val")) + 1);
    console.log(val);
    document.getElementById("counter").setAttribute("val", val);
    var cur = document.getElementById("menu" + (parseInt(val)- 1));
    newM = document.createElement("div");
    newM.setAttribute("id", ("menu" + val));

    var xhr= new XMLHttpRequest();
    xhr.open('GET', '../static/js/dropdown.html', true);
    xhr.onreadystatechange= function() {
	if (this.readyState!==4) return;
	if (this.status!==200) return;
	result =  String(this.responseText).replace(/\{\{n\}\}/g, val);
	newM.innerHTML= result;
	console.log(result);
	cur.appendChild(newM);
	init();
    };
    xhr.send(); 
}




