start();

function start() {
    
    var menus = document.getElementsByClassName("del_b");
    for (var i=0; i<menus.length; i++) {
	menus[i].style.position = "inline-block";
    }

    var dds = document.getElementsByClassName("dropdownL");
    for (var i=0; i < dds.length; i++) {
	dds[i].style.position = "inline-block";
    }


    document.getElementById("edit_b").addEventListener('click', editable);
    document.getElementById("add").addEventListener('click', addMenu);
    var dels = document.getElementsByClassName("del_b");
    for (var i = 0; i < dels.length; i++) {
	dels[i].addEventListener('click', deleteM);
    }
    
    document.getElementById("counter").setAttribute("value", String(times.length - 1));
    //console.log(times);
    for (var i=0; i<times.length; i++) {
	//console.log(i);
	d = times[i];
	//console.log(d);

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

	checkboxes = document.getElementsByName(String(i) + "-address");
	for (var j=0; j < checkboxes.length; j++){
	    if (d['addresses'].indexOf( checkboxes[j].getAttribute("value")) > -1){
		checkboxes[j].checked = true;
	    }
	    
	}
	

    }
    init();
    init_times();
    
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
	dels[i].addEventListener('click', deleteM);
    }
    document.getElementById("save_b").style.visibility = "visible";
    document.getElementById("save_b").addEventListener( 'click', save );
    document.getElementById("add").style.visibility="visible";
    document.getElementById("edit_b").style.visibility="hidden";
    var el = document.getElementById("change");
    el.parentNode.removeChild(el);
    edit_subs();
}

function edit_subs() {
    var max = parseInt(document.getElementById("counter").getAttribute("value"));
    for (var i=0; i<=max;i++) {
	document.getElementById("menu" + i + "-hour").innerHTML += ":00";
	document.getElementById("menu" + i + "-hour2").innerHTML += ":00";
	document.getElementById("menu" + i + "-min").innerHTML = " :" + document.getElementById("menu" + i + "-min").innerHTML;
	document.getElementById("menu" + i + "-min2").innerHTML = " :" + document.getElementById("menu" + i + "-min2").innerHTML;
    }
    console.log(max);
}

function save(e) {
    console.log(document.body);
}

function deleteM(e){
    var num = e.toElement.getAttribute("id").slice(0,1);
    var el = document.getElementById("menu" + num);
    el.parentNode.removeChild(el);
    var cnt = document.getElementById("counter").getAttribute("value");
    document.getElementById("counter").setAttribute("value", String(parseInt(cnt) - 1));
    if (parseInt(num) < parseInt(cnt) && cnt !=0){
	for (var i = parseInt(num); i<parseInt(cnt);i++){
	    cur_html = document.getElementById("menu" + (i+1)).innerHTML;
	    console.log(cur_html);
	    var menuNum = new RegExp( "menu" + String(i+1),"g" );
	    new_html = cur_html.replace( menuNum, "menu" + String(i));
	    var dayNum = new RegExp( 'day="' + String(i+1) + '"', "g");
	    new_html = new_html.replace( dayNum, 'day="' + String(i) + '"');
	    var menuAtt = new RegExp( 'menu="' + String(i+1) + '"',"g");
	    new_html = new_html.replace( menuAtt, 'menu="' + String(i) + '"');
	    console.log(new_html);
	    document.getElementById("menu" + (i+1)).innerHTML = new_html;
	    document.getElementById("menu" + (i+1)).setAttribute("id", "menu" + String(i));
	    document.getElementById(String(i+1) +"-del").setAttribute("id", String(i) + "-del");
	    init();
	    init_times();
	}
	inputs = document.getElementsByTagName("input");
	for (var i=0; i < inputs.length; i++) {
	    if (inputs[i].getAttribute("type") == "hidden" && parseInt(inputs[i].getAttribute("id").slice(0,1))>num){
		pos = String(parseInt(inputs[i].getAttribute("id").slice(0,1)) - 1);
		id = inputs[i].getAttribute("id");
		inputs[i].setAttribute("id", pos + id.slice(1,id.length));
		name = inputs[i].getAttribute("name");
		inputs[i].setAttribute("name", pos + name.slice(1,name.length));
	    }
	    
	}
    }
    
}
