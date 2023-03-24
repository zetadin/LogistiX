
class Map {
    constructor(height, width) {
      this.height = height;
      this.width = width;
      this.hexes = [];
      this.init();
    }

    init() {
        for (let x = 0; x < this.width; x++) {
            for (let y = 0; y < this.height; y++) {
                var hex = new Hex(x,y);
                hex.color = `#${(Math.floor(Math.random()*16777215).toString(16))}`;
                this.hexes.push(hex);

                // console.log(`Hex at ${hex.x},${hex.y} color: ${hex.color}`)
              } 
          } 
    }

    draw(ctx, view) {
        this.hexes.forEach((h,i) => {
            h.draw(ctx, view);
        });
    }
}


const sqrtthree = Math.sqrt(3.0);
const hextheta = 2 * Math.PI / 6;

class Hex {
    constructor(x,y) {
      this.x = y;
      this.y = x;
      this.color = "#FAFAFA"
      this.border_w = 2
      this.border_color = "#000000"
    }

    draw(ctx, view) {
        if(this.x>=view.x_min && this.x<=view.x_max && this.y>=view.y_min && this.y<=view.y_max){
            const r = view.hex_scale;
            //console.log(`Drawing hex at: ${this.x},${this.y} color: ${this.color}, ${r}`);
            const s_x = 1.5 * r * (this.x - view.x_start);
            const s_y = sqrtthree*r * (this.y - view.y_start + (this.x%2==1 ? 0.5 : 0.0));
            ctx.beginPath();
            ctx.strokeStyle = "black";
            ctx.lineWidth = 2;
            for (var i = 0; i < 6; i++) {
                ctx.lineTo(s_x + r * Math.cos(hextheta * i), s_y + r * Math.sin(hextheta * i));
            }
            ctx.closePath();
            ctx.fillStyle = this.color;
            ctx.fill();
            ctx.stroke();
            
            ctx.fillStyle = '#000000';
            ctx.fillRect(s_x-2,s_y-2,5,5); // fill in the pixel at (10,10)
            ctx.textAlign = "center";
            ctx.fillText(`${this.x},${this.y}`, s_x, s_y+view.hex_scale*0.75);
        }
    }    
}


class View {
    constructor(canvas) {
        this.x_start = 0; //map coords
        this.y_start = 0; //map coords
        this.m_width = canvas.width; // px
        this.m_height = canvas.height;
        this.hex_scale = 30; //px per horizontal side
        this.x_max=0; //map coords
        this.y_max=0; //map coords
        this.x_min = 0; //map coords
        this.y_min = 0; //map coords
        this.calc_limits();
      }

      resize(canvas){
        this.m_width = canvas.width; // px
        this.m_height = canvas.height;
        this.calc_limits();
      }

      zoom_in(){
        this.hex_scale+=10;
        if(this.hex_scale>100){this.hex_scale=100};
        this.calc_limits();
      }

      zoom_out(){
        this.hex_scale-=10;
        if(this.hex_scale<10){this.hex_scale=10};
        this.calc_limits();
      }

      move(dxpx, dypx){
        this.x_start+=dxpx/this.hex_scale;
        this.y_start+=dypx/this.hex_scale;
        this.calc_limits();
      }

      calc_limits(){
        var map_width = this.m_width / this.hex_scale;
        var map_height = this.m_height / (this.hex_scale * sqrtthree);
        var half_scale = 0.5 * this.hex_scale;
        this.x_max = Math.ceil(this.x_start + map_width + half_scale);
        this.x_min = Math.floor(this.x_start - half_scale);
        this.y_max = Math.ceil(this.y_start + map_height + half_scale);
        this.y_min = Math.floor(this.y_start - half_scale);

        // this.debug();
      }

      debug(){
        console.log(`min: ${this.x_min}, ${this.y_min}\tmax: ${this.x_max}, ${this.y_max}`);
      }

}