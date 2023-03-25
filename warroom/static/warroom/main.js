// fullscreen canvas from https://stackoverflow.com/questions/4037212/html-canvas-full-screen/4037426
function init_canvas()
{
    var canvas = document.getElementById("mainCanvas");
    //canvas.width = document.body.clientWidth-6; //document.width is obsolete
    var borderW=parseInt(canvas.style.borderWidth, 10);
    canvas.width = window.innerWidth-2*borderW;
    canvas.height = window.innerHeight-2*borderW;
    
    var context = canvas.getContext('2d');

    context.strokeText("Frame", canvas.width-100, 50);

    /*
    //The rectangle should have x,y,width,height properties
    var rect = {
        x:5,
        y:5,
        width:100,
        height:100
    };

    context.beginPath();
    context.strokeStyle = "blue";
    context.rect(rect.x, rect.y, rect.width, rect.height);
    context.stroke();

    //Binding the click event on the canvas
    canvas.addEventListener('click', function(evt) {
        var mousePos = getMousePos(canvas, evt);

        if (isInside(mousePos,rect)) {
            alert('clicked inside rect');
        }else{
            alert('clicked outside rect');
        }   
    }, false);
    */
   

}


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


/////////////////////////////////////////////////////////
//                       INIT                          //
/////////////////////////////////////////////////////////
init_canvas();
var map = new Map(50,30);

var canvas = document.getElementById("mainCanvas");
var view = new View(canvas);
view.x_start=-1;
view.y_start=-1;
var frame = 0;
var lastFrameTime;
var dragging=false;

window.addEventListener('resize', function(evt) {
    canvas.width = window.innerWidth-2*borderW;
    canvas.height = window.innerHeight-2*borderW;
    view.resize(canvas);

}, true);

//Binding the mouse weel event on the canvas
canvas.addEventListener('wheel', function(evt) {
    //console.log("zoom:", evt);
    if (evt.deltaY > 0) {
        view.zoom_out();
    }else if(evt.deltaY < 0){
        view.zoom_in();
    }
    
    //TODO: zoom needs to center on mouse wheel or at least on canvas center
}, false);

//Binding of map dragging
canvas.addEventListener('mousedown', function(evt) {
    if(evt.button==2 && !dragging){ //RMB down
        dragging=true;
    }
}, false);

canvas.addEventListener('mouseup', function(evt) { //RMB up
    if(evt.button==2 && dragging){
        dragging=false;
    }
}, false);

canvas.addEventListener('contextmenu', function(evt) { //RMB up, prevent RMB menu
    if(dragging){
        dragging=false;
    }
    evt.preventDefault();
}, false);

canvas.addEventListener('mousemove', function(evt) {
    if(dragging){
        view.move(-evt.movementX, -evt.movementY);
    }
}, false);

var interval = setInterval(update, 1000/50); //aim for max of 30 fps
/////////////////////////////////////////////////////////

function update(){
    //clear screen
    var ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    //draw map
    map.draw(ctx, view);

    //FPS counter
    if(!lastFrameTime){lastFrameTime = Date.now();}
    var now = Date.now();
    var fps = 1000.0/(now - lastFrameTime);
    ctx.strokeText(`FPS: ${Math.round(fps)}`, canvas.width-100, 50);
    lastFrameTime = now;
    //console.log(`Frame #${fps}`);
}
