#include "Generator.h"
#include <iostream>
#include <math.h>
#define _USE_MATH_DEFINES

Generator::Generator(){
    setFreq(0.003);
    noise = FastNoise::New<FastNoise::Perlin>();

    // seas
    seas = FastNoise::New<FastNoise::FractalFBm>();
    seas->SetSource( noise );
    seas->SetGain( 1.0 );
    seas->SetOctaveCount(3);
    seas->SetLacunarity(2.0);

    // mountains
    mnts = FastNoise::New<FastNoise::FractalRidged>();
    mnts->SetSource( noise );
    mnts->SetGain( 1.0 );
    mnts->SetOctaveCount(3);
    mnts->SetLacunarity(2.2);

    // percipitation
    pers = FastNoise::New<FastNoise::FractalFBm>();
    pers->SetSource( noise );
    pers->SetGain( 1.0 );
    pers->SetOctaveCount(3);
    pers->SetLacunarity(2.0);
}

void Generator::setSeed( unsigned int seed){
    seed_sea = seed;            // seas
    seed_mnt = seed_sea+51;     // mountains
    seed_per = seed_sea+145;    // percipitation
}

void Generator::setFreq( float f){
    freq_sea = f;
    freq_mnt = freq_sea * 0.7;
    freq_per = freq_sea * 2.5;
}

py::array Generator::getTerrain(py::buffer x, py::buffer y, unsigned int mt, float size, bool return_raw_noise){
    
    // request a buffer descriptors from Python
    py::buffer_info info_x = x.request();
    py::buffer_info info_y = y.request();

    // run sanity checks
    if (info_x.format != py::format_descriptor<float>::format())
        throw std::runtime_error("x: Incompatible format: expected a float32 array!");

    if (info_y.format != py::format_descriptor<float>::format())
        throw std::runtime_error("y: Incompatible format: expected a float32 array!");

    if (info_x.ndim != 1 || info_y.ndim !=1)
        throw std::runtime_error("x or y: Incompatible buffer dimension: expected 1D buffers!");

    if (info_x.shape[0] != info_y.shape[0])
        throw std::runtime_error("Unequal shapes: x and y have different shapes!");


    //make local copy of coords so we can release GIL
    unsigned int N = info_x.shape[0];
    std::vector<float> np_x(N);
    std::vector<float> np_y(N);
    memcpy(np_x.data(), static_cast<float *>(info_x.ptr), N*sizeof(float));
    memcpy(np_y.data(), static_cast<float *>(info_y.ptr), N*sizeof(float));

    // release GIL
    py::gil_scoped_release release;

    // alocate temp vectors
    std::vector<float> map_seas(N);
    std::vector<float> map_mnts(N);
    std::vector<float> map_pers(N);
    
    // allocate storage for scaled coords
    std::vector<float> my_x(N);
    std::vector<float> my_y(N);

    // run noise generation
    for (unsigned int i=0; i<N; ++i){
        my_x[i] = np_x[i]*freq_sea;
        my_y[i] = np_y[i]*freq_sea;
    }
    seas->GenPositionArray2D( map_seas.data(), N, my_x.data(), my_y.data(), 0, 0, seed_sea );

    for (unsigned int i=0; i<N; ++i){
        my_x[i] = np_x[i]*freq_mnt;
        my_y[i] = np_y[i]*freq_mnt;
    }
    mnts->GenPositionArray2D( map_mnts.data(), N, my_x.data(), my_y.data(), 0, 0, seed_mnt );
    
    for (unsigned int i=0; i<N; ++i){
        my_x[i] = np_x[i]*freq_per;
        my_y[i] = np_y[i]*freq_per;
    }
    pers->GenPositionArray2D( map_pers.data(), N, my_x.data(), my_y.data(), 0, 0, seed_per );


    // TODO: height modifications go here
    switch(mt){
        case (MapType::Island): 
        {
            float center = size*0.5;
            float sea_edge_min = size*0.3 * size*0.3; // keep these squared for comparison with rsq
            float sea_edge_max = size*0.45 * size*0.45;
            float sea_edge_width = sea_edge_max - sea_edge_min;
            for(unsigned int i = 0; i < N; ++i)
            {
                float ydif = np_y[i]-center;
                ydif*=ydif;
                float xdif = np_x[i]-center;
                xdif*=xdif;
                float rsq = ydif + xdif;
                if(rsq>sea_edge_min){
                    float shift =(rsq - sea_edge_min)/sea_edge_width;
                    // float scale = 1.0 - 0.7*shift;
                    // map_seas[N*y+x]*=scale;
                    map_seas[i]-= 0.5*shift;
                }
                else{
                    float shift =(sea_edge_min-rsq)/sea_edge_min;
                    map_seas[i]+= 0.5*std::min(shift , 0.2f);
                }
            }
        } break;
        case (MapType::Coast):
        {
            float center = size*0.5;
            float sea_edge_min = size*0.3;
            float sea_edge_min_sq = sea_edge_min * sea_edge_min; // keep these squared for comparison with rsq
            float sea_edge_max_sq = size*0.45 * size*0.45;
            float sea_edge_width_sq = sea_edge_max_sq - sea_edge_min_sq;

            // random unit vector from center towards the coast
            // float coast_angle = 90.*M_PI/180.; // angle in radians
            float coast_angle = float(cash(seed_sea+5, 23, 4027)%360)*M_PI/180.; // angle in radians
            // std:: cout<< "coast_angle="<<coast_angle*180.f/M_PI << std::endl;
            float coast_edge_vec[2] = {cos(coast_angle), sin(coast_angle)};
            
            // std::cout << "center to coast vector:" << coast_edge_vec[0] <<" "<< coast_edge_vec[1] <<std::endl;
            // std::cout << "sea_edge_min=" << sea_edge_min <<" sea_edge_min_sq=" << sea_edge_min_sq <<" sea_edge_max_sq=" << sea_edge_max_sq <<std::endl;

            for(unsigned int i = 0; i < N; ++i)
            {
                float ydif = np_y[i]-center;
                float xdif = np_x[i]-center;
                
                // projection of position vector on the center to coast vector
                float r = xdif*coast_edge_vec[0] + ydif*coast_edge_vec[1];
                if(r>sea_edge_min){
                    float rsq = r*r;
                    float shift =(rsq - sea_edge_min_sq)/sea_edge_width_sq;
                    // float scale = 1.0 - 0.7*shift;
                    // map_seas[i]*=scale;
                    map_seas[i]-= 0.5*shift;

                    // std::cout<<"x=" << xdif <<" y="<< ydif << "\t r="<< r << " rsq="<< rsq << "\t shift="<< shift <<std::endl;
                }
                else{
                    float rsq = std::max(r, 0.f);
                    rsq*=rsq;
                    float shift =(sea_edge_min_sq - rsq)/sea_edge_min_sq;
                    map_seas[i]+= 0.5*std::min(shift , 0.2f);
                }
                
            }
        } break;
        
        default:
            // Deault does not need any modifictions
            break;
    }



    // create a 3D array with all three of noise maps
    if(return_raw_noise){
        std::vector<float> map_ret(N*3);
        memcpy ( map_ret.data(), map_seas.data(), sizeof(float)*N );
        memcpy ( &map_ret.data()[N], map_mnts.data(), sizeof(float)*N );
        memcpy ( &map_ret.data()[2*N], map_pers.data(), sizeof(float)*N );

        // memcpy ( map_ret.data(), my_x.data(), sizeof(float)*N );
        // memcpy ( &map_ret.data()[N], my_y.data(), sizeof(float)*N );

        py::gil_scoped_acquire acquire;
        py::array_t<float> ret = py::array_t<float>(N*3, map_ret.data());
        ret.resize(std::vector<unsigned int>{3,N});
        return(ret);
    }

    // assign terrain types
    std::vector<Terrain> map_out(N);
    assign(map_out, map_seas, map_mnts, map_pers, mt);

    // re-aquire GIL
    py::gil_scoped_acquire acquire;

    // return a numpy array with a copy of the data
    return py::array(N, map_out.data());
}




void Generator::assign(std::vector<Terrain>& map_out, std::vector<float>& map_seas, std::vector<float>& map_mnts, std::vector<float>& map_pers, unsigned int mt){
    // terrain assignment
    for(unsigned int i = 0; i < map_out.size(); ++i)
    {        
        if(map_seas[i]<-0.2){
            map_out[i]=Terrain::Sea;
        }
        else if(map_mnts[i]>0.9 && map_seas[i]>0){
            map_out[i]=Terrain::Mountains;
        }
        else if(map_mnts[i]>0.75 && map_seas[i]>0){
            map_out[i]=Terrain::Hills;
        }
        else if(map_pers[i]>0.55 && map_mnts[i] < 0.2 ){
            map_out[i]=Terrain::Swamp;
        }
        else if(map_pers[i]>0.15){
            map_out[i]=Terrain::Forest;
        }
        else{
            map_out[i]=Terrain::Plain;
        }
    }
}