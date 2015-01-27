console.log(subjects);
console.log(classes);

var courses = document.getElementsByName("course");
for (var i = 0; i< courses.length; i++) {
    if (classes.indexOf(courses[i].getAttribute("value"))>= 0){
	courses[i].checked =true;
    }
}

var subs = document.getElementsByName("subject");
for (var i = 0; i< subs.length; i++) {
    if (subjects.indexOf(subs[i].getAttribute("value"))>= 0){
	subs[i].checked =true;
    }
}
