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

class Generator{
    private:
    unsigned int seed_sea, seed_mnt, seed_per;
    float freq_sea, freq_mnt, freq_per;

    FastNoise::SmartNode<FastNoise::Perlin> noise;
    FastNoise::SmartNode<FastNoise::FractalFBm> seas;
    FastNoise::SmartNode<FastNoise::FractalRidged> mnts;
    FastNoise::SmartNode<FastNoise::FractalFBm> pers;

    inline void assign(std::vector<Terrain>& out, std::vector<float>& map_seas, std::vector<float>& map_mnts, std::vector<float>& map_pers);

    public:
    Generator();
    void setSeed( unsigned int seed=1223 );
    py::array_t<unsigned int> getTerrain(py::buffer x, py::buffer y);
};


#endif