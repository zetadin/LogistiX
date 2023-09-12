#ifndef TG_GENERATOR_H
#define TG_GENERATOR_H

// #include <stdlib.h>
#include <math.h>
#include <time.h>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
namespace py = pybind11;

// #include "numpy/ndarray.h" // numpy arrays
#include "FastNoise/FastNoise.h"

enum Terrain : unsigned int { None=0, Sea, Swamp, Plain, Forest, Hills, Mountains};
enum MapType : unsigned int { Island=0, Default=1, Coast=2 };

class Generator{
    private:
    unsigned int seed_sea, seed_mnt, seed_per;
    float freq_sea, freq_mnt, freq_per;

    FastNoise::SmartNode<FastNoise::Perlin> noise;
    FastNoise::SmartNode<FastNoise::FractalFBm> seas;
    FastNoise::SmartNode<FastNoise::FractalRidged> mnts;
    FastNoise::SmartNode<FastNoise::FractalFBm> pers;

    inline void assign(std::vector<Terrain>& out, std::vector<float>& map_seas, std::vector<float>& map_mnts, std::vector<float>& map_pers, unsigned int mt = MapType::Default);

    public:
    Generator();
    void setSeed( unsigned int seed=1223 );
    void setFreq( float f=0.003 );
    py::array getTerrain(py::buffer x, py::buffer y, unsigned int mt = MapType::Default, float size=5, bool return_raw_noise=false);
};


// from https://stackoverflow.com/questions/37128451/random-number-generator-with-x-y-coordinates-as-seed/37221804#37221804
// cash stands for chaos hash :D
inline uint32_t cash(uint32_t x, uint32_t y, uint32_t seed){   
    uint32_t h = seed + x*374761393 + y*668265263; //all constants are prime
    h = (h^(h >> 13))*1274126177;
    return h^(h >> 16);
}

#endif