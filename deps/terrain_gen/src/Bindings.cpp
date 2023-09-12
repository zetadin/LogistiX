#include <iostream>
#include <string>

#include "Generator.h"

// debug output for checking if import worked
static std::string version(void){
    static std::string version = "LogistiX terraingen v0.0.0";
    return(version);
}


PYBIND11_MODULE(terraingen, m) {
    // functions
    m.def("version", &version, "A function that returns the module version.");

    // define all classes
    py::class_<Generator>(m, "Generator")
            .def(py::init<>()) // constructor
            .def("setSeed", &Generator::setSeed, "Set noise seed", py::arg("seed"))
            .def("setFreq", &Generator::setFreq, "Set noise frequency", py::arg("freq"))
            .def("getTerrain", &Generator::getTerrain,
                 "Returns a numpy array of unsigned ints describing terrain types at x, y.",
                 py::arg("x"), py::arg("y"), py::arg("map_type")=1, py::arg("size")=5, py::arg("return_raw_noise")=false);
}