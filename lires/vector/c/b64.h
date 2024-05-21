#pragma once
#include "common.h"

std::string base64_encode(std::vector<uchar> const& in);
std::vector<uchar> base64_decode(std::string const& encoded_string);
namespace VectorStringEncode {
    std::string encode(const std::vector<fp32>& vec);
    std::vector<fp32> decode(const std::string& encoded);
}
