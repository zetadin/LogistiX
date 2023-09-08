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

