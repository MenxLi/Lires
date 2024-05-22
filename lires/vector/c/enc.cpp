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

std::string VectorStringEncode::encode_b64(const std::vector<num_t>& vec){
    std::vector<uchar> vec_uchar((uchar*)vec.data(), (uchar*)vec.data() + vec.size() * sizeof(num_t));
    return base64_encode(vec_uchar);
}
std::vector<num_t> VectorStringEncode::decode_b64(const std::string& encoded){
    if (encoded.size() % sizeof(num_t) != 0){
        throw std::runtime_error("invalid encoded string");
    }
    std::vector<uchar> vec_uchar = base64_decode(encoded);

    // will this be unsafe?
    std::vector<num_t> vec((num_t*)vec_uchar.data(), (num_t*)vec_uchar.data() + vec_uchar.size() / sizeof(num_t));
    return vec;
}


py::bytes VectorStringEncode::encode(const std::vector<num_t>& vec){
    return py::bytes(
        (char*)vec.data(),
        vec.size() * sizeof(num_t)
    );
}

py::bytes VectorStringEncode::encode_fp64as32(const std::vector<fp64>& vec){
    // cast fp64 to fp32
    std::vector<fp32> vec_fp32(vec.size());
    for (unsigned long i = 0; i < vec.size(); i++){
        vec_fp32[i] = static_cast<fp32>(vec[i]);
    }
    return py::bytes(
        (char*)vec_fp32.data(),
        vec_fp32.size() * sizeof(fp32)
    );
}

std::vector<num_t> VectorStringEncode::decode(const py::bytes& encoded){
    std::string encoded_str = encoded;
    std::vector<num_t> vec((num_t*)encoded_str.data(), (num_t*)encoded_str.data() + encoded_str.size() / sizeof(num_t));
    return vec;
}

Eigen::Vector<num_t, FEAT_DIM> VectorStringEncode::decode_eigen(const py::bytes& encoded){
    std::string encoded_str = encoded;
    Eigen::Vector<num_t, FEAT_DIM> vec = Eigen::Map<const Eigen::Vector<num_t, FEAT_DIM>>((num_t*)encoded_str.data());
    return vec;
}
