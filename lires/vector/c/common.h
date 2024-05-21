#pragma once

#ifndef FEAT_DIM
#define FEAT_DIM 768
#endif

#ifndef MODULE_NAME
#define MODULE_NAME vecdbImpl
#endif

#include <memory>
#include <vector>
#include <string>
#include <iostream>

#include <Eigen/Core>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
// #include <pybind11/eigen.h>

#include <assert.h>

// make sure float is 32bit
// float is 32bit on most platforms, but not guaranteed
// IEEE 754 single-precision binary floating-point format: binary32
typedef float fp32;
typedef fp32 num_t;
typedef unsigned char uchar;
static_assert(sizeof(num_t) == 4, "num_t must be 32bit");

typedef Eigen::Matrix<num_t, Eigen::Dynamic, FEAT_DIM, Eigen::RowMajor> 
MatrixF;
// typedef std::string SVector;
// typedef std::vector<std::string> SMatrix;
