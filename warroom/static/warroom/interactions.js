// fullscreen canvas from https://stackoverflow.com/questions/4037212/html-canvas-full-screen/4037426
function init()
{
    var canvas = document.getElementById("mainCanvas");
    //canvas.width = document.body.clientWidth-6; //document.width is obsolete
    var borderW=parseInt(canvas.style.borderWidth, 10);
    canvas.width = window.innerWidth-2*borderW;
    canvas.height = window.innerHeight-2*borderW;
    
    window.addEventListener('resize', function(event) {
        canvas.width = window.innerWidth-2*borderW;
        canvas.height = window.innerHeight-2*borderW;
    }, true);

    /*
    if( canvas.getContext )
    {
        setup();
        setInterval( run , 33 );
    }
    */

    var context = canvas.getContext('2d');
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


init();