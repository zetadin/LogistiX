var view = new View(canvas);
view.x_start=-1;
view.y_start=-1;
view.calc_limits();
var lastFrameTime;
var dragging=false;

window.addEventListener('resize', function(evt) {
    canvas.width = window.innerWidth-2*borderW-ctrlbarW-left_pad;
    canvas.height = window.innerHeight-2*borderW;
    view.resize(canvas);

}, true);

//Binding the mouse weel event on the canvas
canvas.addEventListener('wheel', function(evt) {
    if (evt.deltaY > 0) {
        view.zoom_out(evt.pageX-borderW-ctrlbarW-left_pad, evt.pageY-borderW);
    }else if(evt.deltaY < 0){
        view.zoom_in(evt.pageX-borderW-ctrlbarW-left_pad, evt.pageY-borderW);
    }
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

canvas.addEventListener('click', function(evt) {
    //LMB down
    const a = view.hex_scale;
    const h = 0.5*a*sqrtthree;

    // start  of the relative axes for click detection is at center of hex 0,0 - (a,h) in x and y
    const rel_start_x = -a * view.x_start - a;
    const rel_start_y = -a * view.y_start - h;

    const [rel_x, rel_y] = [evt.pageX-ctrlbarW-left_pad-borderW - rel_start_x, evt.pageY-borderW - rel_start_y];
    const tx = Math.floor(rel_x / (1.5*a));
    const remx = Math.fmod(rel_x, (1.5*a));
    const ty = Math.floor((rel_y - (tx%2==1 ? h : 0)) / (2*h)); // move odd columns down by half a hex
    const remy = Math.fmod(rel_y - (tx%2==1 ? h : 0), (2*h));

    let [mx, my] = [tx, ty]; // default values that get overwritten if wea re actually in a neighbouring hex
    if(remx<0.5*a){   // if we are left of here, we might be in hexes to the left,
                      // depending which side of edges we are on
        if(remy<h-remx*2*h/a) { // check above /
            mx = tx - 1;
            my = (tx%2==1) ? ty : ty-1; // reduce hex y index if we are in an even column an going left & up.
        }
        else if(remy>h+remx*2*h/a) { // check below \
            mx = tx - 1;
            my = (tx%2==1) ? ty+1 : ty; // increade hex y index if we are in an odd column an going left & down.
        }
    }
    
    console.log("click @ hex ", mx, my, "\ttemp:", tx, ty, "\tpixels:", evt.pageX, evt.pageY, "\trem:", remx, remy, "\ta:",a,"\th",h);
    // console.log("rel_start", rel_start_x, rel_start_y);

}, false);

//var interval = setInterval(update, 1000/50); //aim for max of 30 fps
const targetFPS = 50;
update();
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
    ctx.font = "20px sans";
    ctx.textAlign = "center";
    ctx.strokeText(`FPS: ${Math.round(fps)}`, canvas.width-100, 50);
    lastFrameTime = now;
    //console.log(`Frame #${fps}`);

    ctx.textAlign = "left";
    var debug_str ="";
    // debug_str += `start: ${view.x_start.toFixed(2)}, ${view.y_start.toFixed(2)}`+"\n";
    // debug_str += `hex: ${view.x_hex.toFixed(2)}, ${view.y_hex.toFixed(2)}`+"\n";
    // debug_str += `start_map: ${view.x_start_map.toFixed(2)}, ${view.y_start_map.toFixed(2)}\t=\t${(view.x_start/1.5).toFixed(2)}, ${(view.y_start/Math.sqrt(3)).toFixed(2)}`+"\n";
    // debug_str += `limits: x = ${view.x_min}, ${view.x_max}\ty = ${view.y_min}, ${view.y_max}`+"\n";
    var lineheight=16;
    var y=lineheight;
    var words = debug_str.split('\n');
    for(var n = 0; n < words.length; n++) {
        ctx.fillText(words[n], 10, y);
        y+=lineheight;
    }
    

    //schedule the next update
    setTimeout(() => {
        requestAnimationFrame(update);
      }, 1000 / targetFPS);
    
}
