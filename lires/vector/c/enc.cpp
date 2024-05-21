#include "enc.h"
#include "common.h"
#include "pybind11/detail/common.h"
#include "pybind11/pytypes.h"
#include <cstddef>
#include <pybind11/stl.h>
#include <vector>

/*
Encoding and Decoding Base64
Code from https://stackoverflow.com/questions/180947/base64-decode-snippet-in-c
*/
std::string base64_encode(const std::vector<uchar> &in) {
    std::string out;
    int val = 0, valb = -6;
    for (uchar c : in) {
        val = (val << 8) + c;
        valb += 8;
        while (valb >= 0) {
            out.push_back("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"[(val>>valb)&0x3F]);
            valb -= 6;
        }
    }
    if (valb>-6) out.push_back("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"[((val<<8)>>(valb+8))&0x3F]);
    while (out.size()%4) out.push_back('=');
    return out;
}
std::vector<uchar> base64_decode(const std::string &in) {
    // std::string out;
    std::vector<uchar> out;
    std::vector<int> T(256,-1);
    for (int i=0; i<64; i++) T["ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"[i]] = i;
    int val=0, valb=-8;
    for (uchar c : in) {
        if (T[c] == -1) break;
        val = (val << 6) + T[c];
        valb += 6;
        if (valb >= 0) {
            out.push_back(char((val>>valb)&0xFF));
            valb -= 8;
        }
    }
    return out;
}

std::string VectorStringEncode::encode_b64(const std::vector<fp32>& vec){
    std::vector<uchar> vec_uchar((uchar*)vec.data(), (uchar*)vec.data() + vec.size() * sizeof(fp32));
    return base64_encode(vec_uchar);
}
std::vector<fp32> VectorStringEncode::decode_b64(const std::string& encoded){
    if (encoded.size() % 4 != 0){
        throw std::runtime_error("invalid encoded string");
    }
    std::vector<uchar> vec_uchar = base64_decode(encoded);

    // will this be unsafe?
    std::vector<fp32> vec((fp32*)vec_uchar.data(), (fp32*)vec_uchar.data() + vec_uchar.size() / sizeof(fp32));
    return vec;
}


py::bytes VectorStringEncode::encode(const std::vector<fp32>& vec){
    return py::bytes(
        (char*)vec.data(),
        vec.size() * sizeof(fp32)
    );
}

std::vector<fp32> VectorStringEncode::decode(const py::bytes& encoded){
    std::string encoded_str = encoded;
    std::vector<fp32> vec((fp32*)encoded_str.data(), (fp32*)encoded_str.data() + encoded_str.size() / sizeof(fp32));
    return vec;
}

Eigen::Vector<fp32, FEAT_DIM> VectorStringEncode::decode_eigen(const py::bytes& encoded){
    std::string encoded_str = encoded;
    Eigen::Vector<fp32, FEAT_DIM> vec = Eigen::Map<const Eigen::Vector<fp32, FEAT_DIM>>((fp32*)encoded_str.data());
    return vec;
}
