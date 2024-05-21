#pragma once
#include "common.h"
#include "pybind11/pytypes.h"
namespace py = pybind11;

std::string base64_encode(std::vector<uchar> const& in);
std::vector<uchar> base64_decode(std::string const& encoded_string);
namespace VectorStringEncode {
    std::string encode_b64(const std::vector<fp32>& vec);
    std::vector<fp32> decode_b64(const std::string& encoded);

    py::bytes encode(const std::vector<fp32>& vec);
    std::vector<fp32> decode(const py::bytes& encoded);

    Eigen::Vector<fp32, FEAT_DIM> decode_eigen(const py::bytes& encoded);
}
