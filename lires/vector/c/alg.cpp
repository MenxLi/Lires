
#include <iostream>
#include "pybind11/attr.h"
#include "pybind11/cast.h"
#include "pybind11/pytypes.h"
#include "common.h"
#include "b64.h"

namespace SearchAlgorithm {
    std::vector<int> topKIndices(const Eigen::Vector<float, Eigen::Dynamic> scores, int k){
        std::vector<int> ret;
        std::vector<std::pair<float, int>> scores_idx;
        scores_idx.reserve(scores.size());
        for (int i = 0; i < scores.size(); i++){
            scores_idx.push_back(std::make_pair(scores[i], i));
        }
        // sort with the k-th element as the pivot
        std::nth_element(scores_idx.begin(), scores_idx.begin() + k, scores_idx.end(), [](const std::pair<float, int>& a, const std::pair<float, int>& b){
            return a.first > b.first;
        });
        // sort the first k elements, the rest are not sorted, make the larger the first
        std::sort(scores_idx.begin(), scores_idx.begin() + k, [](const std::pair<float, int>& a, const std::pair<float, int>& b){
            return a.first > b.first;
        });
        for (int i = 0; i < k; i++){
            ret.push_back(scores_idx[i].second);
        }
        return ret;
    }
    inline Eigen::Vector<float, Eigen::Dynamic> cosineSimilarity(const MatrixF& target, const Eigen::Vector<fp32, FEAT_DIM>& query_matrix){
        const fp32 _eps = 1e-8;
        if (target.cols() != query_matrix.size()){
            throw std::runtime_error("query size not match");
        }
        Eigen::Matrix<fp32, Eigen::Dynamic, 1> search_scores = target * query_matrix;
        float norm_query = query_matrix.norm();
        Eigen::Vector<float, Eigen::Dynamic> norm_collection = target.rowwise().norm();
        search_scores = search_scores.array() / (norm_query * norm_collection.array() + _eps);
        return search_scores;
    }
    inline Eigen::Vector<float, Eigen::Dynamic> cosineSimilarity(const MatrixF& target, const std::vector<fp32>& query){
        if (target.cols() != query.size()){
            throw std::runtime_error("query size not match");
        }
        Eigen::Matrix<fp32, FEAT_DIM, 1> query_matrix = Eigen::Map<const Eigen::Matrix<fp32, FEAT_DIM, 1>>(query.data());
        return cosineSimilarity(target, query_matrix);
    }
}


std::vector<fp32> similarity(
    const std::string& query_encoded,
    const std::vector<std::string>& target_encoded
){
    std::vector<fp32> query = VectorStringEncode::decode(query_encoded);
    MatrixF target(target_encoded.size(), FEAT_DIM);
    for (int i = 0; i < target_encoded.size(); i++){
        std::vector<fp32> vec = VectorStringEncode::decode(target_encoded[i]);
        target.row(i) = Eigen::Map<const Eigen::Matrix<fp32, FEAT_DIM, 1>>(vec.data());
    }
    Eigen::Vector<float, Eigen::Dynamic> scores = SearchAlgorithm::cosineSimilarity(target, query);
    return std::vector<fp32>(scores.data(), scores.data() + scores.size());
}

std::vector<int> topKIndices(
    const std::vector<fp32>& scores,
    const int k
){
    Eigen::Vector<float, Eigen::Dynamic> scores_eigen = Eigen::Map<const Eigen::Vector<float, Eigen::Dynamic>>(scores.data(), scores.size());
    return SearchAlgorithm::topKIndices(scores_eigen, k);
}

// namespace py = pybind11;
PYBIND11_MODULE(MODULE_NAME, m) {
    m.doc() = "vector database algorithoms";
    m.attr("FEAT_DIM") = FEAT_DIM;  // for debug
    m.def("similarity", &similarity, "distance between a encoded query and a list of targets");
    m.def("topKIndices", &topKIndices, "top k indices of scores");
    m.def("encode", &VectorStringEncode::encode, "encode vector to string");
    m.def("decode", &VectorStringEncode::decode, "decode string to vector");
}