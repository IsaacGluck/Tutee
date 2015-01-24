start();

function start() {

    document.getElementById("edit_b").addEventListener('click', editable);
    document.getElementById("add").addEventListener('click', addMenu);
    
    document.getElementById("counter").setAttribute("value", String(times.length));

    for (var i=0; i<times.length; i++) {
	d = times[i];

	for (var k in d) {
	    if (k != "addresses"){
		document.getElementById( String(i) + "-" + k.replace("_","").replace("min","minute")).setAttribute("value",d[k]);
	    }
	}

	m = "menu" + String(i);
	document.getElementById(m + "-day").innerHTML = d['day'];

	document.getElementById(m + "-start").innerHTML = d['start_hour'] + ":" + d['start_min']  + " " + d['start_type'];
	document.getElementById(m + "-hour").innerHTML = d['start_hour']; 
	document.getElementById(m + "-min").innerHTML = d['start_min'];
	document.getElementById(m + "-type").innerHTML = d['start_type'];

	document.getElementById(m + "-end").innerHTML = d['end_hour'] + ":" + d['end_min']  + " " + d['end_type'];
	document.getElementById(m + "-hour2").innerHTML = d['end_hour'];
	document.getElementById(m + "-min2").innerHTML = d['end_min'];
	document.getElementById(m + "-type2").innerHTML = d['end_type'];

    }
    init();
    
}

function init() {
    var dels = document.getElementsByClassName("del_b");
}

function editable(e){
    newM = document.createElement("script");
    newM.type = "text/javascript";
    newM.src = "/static/js/dropdown_edit.js";
    document.body.appendChild( newM );

    var dels = document.getElementsByClassName("del_b");
    for (var i =0; i < dels.length; i++) {
	dels[i].style.visibility= "visible";
    }
}

function init_times() {
    return;
}
//function addMenu(e){
//}
