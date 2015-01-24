
for (var i=0; i<times.length; i++) {
    d = times[i];

    for (var k in d) {
	if (k != "addresses"){
	    document.getElementById( String(i) + "-" + k.replace("_","").replace("min","minute")).setAttribute("value",d[k]);
	}
    }

    m = "menu" + String(i);
    document.getElementById(m + "-day").innerHTML = d['day'];

    document.getElementById(m + "-start");
    document.getElementById(m + "-hour").innerHTML =['start_hour']; 
    document.getElementById(m + "-min").innerHTML =['start_min'];
    document.getElementById(m + "-type").innerHTML =['start_type'];

    document.getElementById(m + "-end");
    document.getElementById(m + "-hour2").innerHTML =['end_hour'];
    document.getElementById(m + "-min2").innerHTML =['end_min'];
    document.getElementById(m + "-type2").innerHTML =['end_type'];

    console.log(document.body);

/*
    document.getElementById(str(i) + "-day").setAttribute("value", d['day']);
    document.getElementById("menu" + i + "-day").innerHTML= d['day'];
    
    document.getElementById(str(i) + "-starthour").setAttribute("value",d['start_hour']);

    document.getElementById(str(i) + "-startminute").setAttribute("value",d['start_minute'])

    document.getElementBy
    */

    console.log(times[i]);
}
