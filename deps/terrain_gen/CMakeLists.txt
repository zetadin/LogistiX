cmake_minimum_required(VERSION 3.3.0) # pybind11 needs cmake policy 0057: if ... IN_LIST ...

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_FLAGS "-O2 -ftree-vectorize -g -fPIC")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -ffast-math -Wall -ftree-vectorize -fPIC")


project(terraingen)

# Include dir
include_directories(/usr/local/include)

# Src
AUX_SOURCE_DIRECTORY(src SRC_FILES)

# folders
set(PROJECT_SOURCE_DIR "src")
set(PROJECT_INCLUDE_DIR "include")


# files
file (GLOB SOURCE_FILES "${PROJECT_SOURCE_DIR}/*.cpp")
file (GLOB HEADER_FILES "${PROJECT_INCLUDE_DIR}/*.hpp" "${PROJECT_INCLUDE_DIR}/*.h")
#file (GLOB PYTHON_FILES "python/*.cpp" "python/*.hpp")

message(STATUS HEADER_FILES="${HEADER_FILES}")


# Set up such that XCode organizes the files correctly
source_group(TREE ${CMAKE_CURRENT_SOURCE_DIR} FILES ${SOURCE_FILES} ${HEADER_FILES})
#source_group(TREE ${CMAKE_CURRENT_SOURCE_DIR} FILES ${SOURCE_FILES} ${HEADER_FILES} ${PYTHON_FILES})


# Find Python
find_package (Python COMPONENTS Interpreter Development REQUIRED)
# if(Python_FOUND)
#     message(STATUS "Python version ${Python_VERSION} found")
#     message(STATUS "Python executable: ${Python_EXECUTABLE}")
#     message(STATUS "Python standard install directory: ${Python_STDLIB}")
#     message(STATUS "Python include directories: ${Python_INCLUDE_DIRS}")
#     message(STATUS "Python library directories: ${Python_LIBRARY_DIRS}")
#     message(STATUS "Python libraries: ${Python_LIBRARIES}")
# endif()
execute_process (
    COMMAND "${Python_EXECUTABLE}" -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(), end='')"
    OUTPUT_VARIABLE PYTHON_SITEPATH
)

# add search path for pybind11 and FastNoise2
# list(APPEND CMAKE_PREFIX_PATH "${PYTHON_SITEPATH}/pybind11/share/cmake")
# list(APPEND CMAKE_PREFIX_PATH "../FastNoise2/build/generated")
# message(STATUS "Setting " CMAKE_PREFIX_PATH="${CMAKE_PREFIX_PATH}")


# find packages
find_package(pybind11 REQUIRED HINTS ${PYTHON_SITEPATH}/pybind11/share/cmake)
find_package(FastNoise2 REQUIRED HINTS /usr/local/lib/cmake)

# add include paths
include_directories(${PROJECT_INCLUDE_DIR} ${Python_INCLUDE_DIRS})


pybind11_add_module(terraingen 
	${SOURCE_FILES}
	${HEADER_FILES}
	# ${PYTHON_FILES}
)

# also link to FastNoise2
target_link_libraries(terraingen PRIVATE FastNoise2::FastNoise)
