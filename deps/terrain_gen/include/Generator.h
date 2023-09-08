#ifndef TG_GENERATOR_H
#define TG_GENERATOR_H

// #include <stdlib.h>
#include <math.h>
#include <time.h>
#include <pybind11/pybind11.h>
namespace py = pybind11;

// #include "numpy/ndarray.h" // numpy arrays
#include "FastNoise/FastNoise.h"

class Generator{
    private:
    unsigned int seed_sea, seed_mnt, seed_per;
    float freq_sea, freq_mnt, freq_per;

    FastNoise::SmartNode<FastNoise::Perlin> noise;
    FastNoise::SmartNode<FastNoise::FractalFBm> seas;
    FastNoise::SmartNode<FastNoise::FractalRidged> mnts;
    FastNoise::SmartNode<FastNoise::FractalFBm> pers;

    public:
    Generator();
    void setSeed( unsigned int seed=1223 );
};


#endif