

/////////////////////////////////////////////////////////
//                       INIT                          //
/////////////////////////////////////////////////////////
// fullscreen canvas from https://stackoverflow.com/questions/4037212/html-canvas-full-screen/4037426
var canvas = document.getElementById("mainCanvas");
var ctrlbar = document.getElementById("ctrlbar");
var maincontainer = document.getElementById("main");

var borderW = parseInt(canvas.style.borderWidth, 10);
var ctrlbarW = parseInt(getComputedStyle(ctrlbar).width, 10);
var left_pad = parseInt(getComputedStyle(maincontainer).paddingLeft, 10);
canvas.width = window.innerWidth-2*borderW-ctrlbarW-left_pad;
canvas.height = window.innerHeight-2*borderW;

var ctx = canvas.getContext('2d');
ctx.font = "14px serif";
ctx.strokeText("FPS", canvas.width-100, 50);
ctx.strokeText("Debug", 10, 10);

// if no map requested, make and show a random one
var map;
if (mapid==""){
    map = new Map(10,10);
}
else{ // otherwize get the map data
    var map_JSON;
    map = new Map(0,0, init=false);
    update_map();
    
}


