
//Mouse detection based on https://stackoverflow.com/a/24384882

//Function to get the mouse position
function getMousePos(canvas, event) {
    var rect = canvas.getBoundingClientRect();
    return {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top
    };
}
//Function to check whether a point is inside a rectangle
function isInside(pos, rect){
    return pos.x > rect.x && pos.x < rect.x+rect.width && pos.y < rect.y+rect.height && pos.y > rect.y
}

var canvas = document.getElementById('myCanvas');
var context = canvas.getContext('2d');
//The rectangle should have x,y,width,height properties
var rect = {
    x:250,
    y:350,
    width:200,
    height:100
};
//Binding the click event on the canvas
canvas.addEventListener('click', function(evt) {
    var mousePos = getMousePos(canvas, evt);

    if (isInside(mousePos,rect)) {
        alert('clicked inside rect');
    }else{
        alert('clicked outside rect');
    }   
}, false);

context.beginPath();
context.strokeStyle = "blue";
context.rect(rect.x, rect.y, rect.width, rect.height);
context.stroke();
