/* Resource: https://www.w3schools.com/jsref/jsref_tolocaledatestring.asp */
var date = new Date();
var n = date.toLocaleDateString();
document.getElementById("dateToday").innerHTML = n;
