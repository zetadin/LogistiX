#include "Generator.h"

Generator::Generator(){
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
    pers->SetLacunarity(3.0);
}

void Generator::setSeed( unsigned int seed){
    seed_sea = seed;            // seas
    seed_mnt = seed_sea+51;     // mountains
    seed_per = seed_sea+145;    // percipitation
}

py::array_t<unsigned int> Generator::getTerrain(py::buffer x, py::buffer y){
    
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
    memcpy(np_x.data(), static_cast<float *>(info_x.ptr), N*sizeof(float));

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
    seas->GenPositionArray2D( map_seas.data(), N, my_x.data(), my_y.data(), 0, 0, seed_mnt );
    
    for (unsigned int i=0; i<N; ++i){
        my_x[i] = np_x[i]*freq_per;
        my_y[i] = np_y[i]*freq_per;
    }
    seas->GenPositionArray2D( map_seas.data(), N, my_x.data(), my_y.data(), 0, 0, seed_per );

    // TODO: height modifications go here

    // assign terrain types
    std::vector<Terrain> map_out(N);
    assign(map_out, map_seas, map_mnts, map_pers);

    // re-aquire GIL
    py::gil_scoped_acquire acquire;

    // return a numpy array with a copy of the data
    return py::array(N, map_out.data());
}




void Generator::assign(std::vector<Terrain>& map_out, std::vector<float>& map_seas, std::vector<float>& map_mnts, std::vector<float>& map_pers){
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