factionColors={0:"#176ba3", // blue
               1:"#b00000", // red
               2:"#028A0F", // emerald
               3:"#F4C430", // saffron
               99:"#FAFAFA" // grey (neutral)
            }

class Platoon {
    constructor(x,y) {
      this.x = x;
      this.y = y;
      this.color = factionColors[99]
      this.border_w = 3

      this.data = {}
      this.iconURL = ""
    }

    draw(ctx, view) {
        if(this.x>=view.x_min && this.x<=view.x_max && this.y>=view.y_min && this.y<=view.y_max){
            var r = view.hex_scale;
            //console.log(`Drawing hex at: ${this.x},${this.y} color: ${this.color}, ${r}`);
            
            // screen coords of the center
            const s_x = 1.5 * r * (this.x - view.x_start_map);
            const s_y = sqrtthree*r * (this.y - view.y_start_map + (this.x%2==1 ? 0.5 : 0.0));

            // draw hexagonal border
            r = Math.min(r*0.8, r-3) // make it smaller then the map hex 
            ctx.beginPath();
            ctx.setLineDash([0.25*r, 0.5*r, 0.25*r, 0]);
            ctx.strokeStyle = this.color;
            ctx.lineWidth = Math.max(1, Math.min(this.border_w, view.hex_scale*0.15) );
            for (var i = 0; i < 6; i++) {
                ctx.lineTo(s_x + r * Math.cos(hextheta * i), s_y + r * Math.sin(hextheta * i));
            }
            ctx.closePath();
            ctx.stroke();
            ctx.setLineDash([]);

            // console.log("dash at:",s_x, s_y);
            let w = 1.3*r;
            // drawSVG(ctx, this.iconURL, s_x-0.5*w, s_y-0.5*w, w, w, this.color);
            drawPNG(ctx, this.iconURL, s_x-0.5*w, s_y-0.5*w, // + sqrtthree*view.hex_scale,
                    w, w, this.color)
        }
    }    
}