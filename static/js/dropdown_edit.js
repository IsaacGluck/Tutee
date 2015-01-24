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

    
    var subs = document.getElementsByClassName("sub")
    for (var i=0; i<subs.length; i++){
	subs[i].addEventListener('mouseover',showsub);
    }

    var subs2  = document.getElementsByClassName("s2");
    for (var i=0; i < subs2.length;i++) {
	subs2[i].addEventListener('mouseover', processsub);
	subs2[i].addEventListener('mouseout', hidedropstart);
    }

}

