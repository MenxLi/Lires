#pragma once

#ifndef FEAT_DIM
#define FEAT_DIM 768
#endif

#ifndef MODULE_NAME
#define MODULE_NAME vecdbImpl
#endif

#ifndef BUFFER_SIZE
#define BUFFER_SIZE int(1024*1024*8 / sizeof(num_t) / FEAT_DIM) // 8MB
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
static_assert(sizeof(fp32) == 4, "fp32 must be 32bit");

typedef double fp64;
static_assert(sizeof(fp64) == 8, "fp64 must be 64bit");

typedef fp64 num_t;
typedef unsigned char uchar;

typedef Eigen::Matrix<num_t, Eigen::Dynamic, FEAT_DIM, Eigen::RowMajor> 
MatrixF;
// typedef std::string SVector;
// typedef std::vector<std::string> SMatrix;
