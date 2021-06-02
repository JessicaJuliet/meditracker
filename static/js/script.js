/* Resource: https://www.w3schools.com/jsref/jsref_tolocaledatestring.asp */
window.addEventListener("DOMContentLoaded", function(){
    const date = new Date();
    const dateTodayRef = document.getElementById("dateToday")
    dateTodayRef.innerHTML = date.toLocaleDateString();
})
